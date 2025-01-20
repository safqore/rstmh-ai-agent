from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import PyPDF2
import traceback
import os

load_dotenv()

# Qdrant Cloud setup
QDRANT_URL = os.getenv('QDRANT_URL')
API_KEY = os.getenv('QD_API_TOKEN')

# Collections for PDFs
FAQ_COLLECTION = "faq_vectors"
DETAILS_COLLECTION = "details_vectors"

# Initialize Qdrant client and embedding model
client = QdrantClient(QDRANT_URL, api_key=API_KEY)
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# Extract question answers from faq pdf
def extract_qa_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() or ""
    
    # Split text into potential questions and answers
    lines = full_text.split("\n")
    qa_pairs = []
    question = None

    for line in lines:
        if line.strip().endswith("?"):  # Identify lines ending with a question mark as questions
            if question:
                qa_pairs.append((question, answer.strip()))
            question = line.strip()  # Start a new question
            answer = ""
        elif question:
            answer += " " + line.strip()  # Append to the answer
    
    # Add the last QA pair
    if question and answer.strip():
        qa_pairs.append((question, answer.strip()))
    
    return qa_pairs

def upload_qa_to_qdrant(pdf_path, pdf_id, collection_name):
    """
    Extracts questions and answers from a PDF and uploads them as vectors to a Qdrant collection.

    Args:
        pdf_path (str): The file path to the PDF.
        collection_name (str): The name of the Qdrant collection.
        pdf_id (str): A unique identifier for the PDF.
    """
    # Extract QA pairs from the PDF
    qa_pairs = extract_qa_from_pdf(pdf_path)

    # Generate embeddings for questions only
    questions = [q for q, _ in qa_pairs]
    embeddings = embedder.encode(questions)

    # Recreate the collection
    recreate_qdrant_collection(vector_size=len(embeddings[0]), collection_name=collection_name)

    # Upload each question and its corresponding answer
    points = [
        models.PointStruct(
            id=idx,
            vector=embedding.tolist(),
            payload={
                "pdf_id": pdf_id,          # Unique identifier for the PDF
                "question": question,      # The question text
                "answer": answer           # The corresponding answer
            }
        )
        for idx, (embedding, (question, answer)) in enumerate(zip(embeddings, qa_pairs))
    ]

    client.upsert(collection_name=collection_name, points=points)
    print(f"[SUCCESS] Uploaded {len(points)} QA pairs from {pdf_path} to Qdrant collection '{collection_name}'.")

# Extract text from the PDF
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() or ""
    return full_text

# Chunk text with overlap to avoid missing context between segments
def chunk_text(text, max_length=500, overlap=100):
    chunks = []
    words = text.split()
    for i in range(0, len(words), max_length - overlap):
        chunk = " ".join(words[i:i+max_length])
        chunks.append(chunk)
    return chunks

# Delete and recreate the collection
def recreate_qdrant_collection(vector_size, collection_name):
    # Check if collection exists
    if client.collection_exists(collection_name=collection_name):
        print(f"[INFO] Deleting existing collection: {collection_name}...")
        client.delete_collection(collection_name=collection_name)
    
    # Recreate the collection with the same vector size and cosine distance
    print(f"[INFO] Creating new collection: {collection_name}...")
    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE)
    )

# Upload chunks of the PDF to Qdrant as vectors with integer IDs
def upload_pdf_to_qdrant(pdf_path, pdf_id, collection_name):
    # Extract full text from the PDF
    text = extract_text_from_pdf(pdf_path)

    # Break the text into overlapping chunks
    chunks = chunk_text(text)

    # Generate embeddings (vectors) for each chunk
    embeddings = embedder.encode(chunks)

    # Recreate collection to clear old vectors
    recreate_qdrant_collection(vector_size=len(embeddings[0]), collection_name=collection_name)

    # Upload each chunk as a vector with a unique integer ID
    points = [
        models.PointStruct(
            id=idx,
            vector=embedding.tolist(),
            payload={"text": chunk, "pdf_id": pdf_id}
        )
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings))
    ]
    
    client.upsert(collection_name=collection_name, points=points)
    print(f"[SUCCESS] Uploaded {len(points)} chunks from {pdf_path} to Qdrant collection '{collection_name}'.")

# Function to Search for the Most Relevant Answer
def search_qdrant(query, collection_name, top_k=3):
    query_vector = embedder.encode([query])[0].tolist()
    results = client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=top_k
    )
    print(f"[DEBUG] Search Results in {collection_name}: {results}")
    return results

# Main Function to Handle Query
def handle_user_query(query):
    # Search FAQ first
    faq_results = search_qdrant(query, FAQ_COLLECTION)
    if faq_results and faq_results[0].score > 0.8:  # Adjust threshold as needed
        print("[INFO] Answer found in FAQ:")
        return faq_results[0].payload["text"]
    
    # Fallback to Details if FAQ has no match
    print("[INFO] No sufficient match in FAQ. Searching Details...")
    details_results = search_qdrant(query, DETAILS_COLLECTION)
    if details_results:
        return details_results[0].payload["text"]
    return "Sorry, no relevant information found."

# Function to delete all collections
def delete_all_collections():
    try:
        # Get the list of all collections
        collections = client.get_collections().collections
        if not collections:
            print("[INFO] No collections found in Qdrant.")
            return
        
        # Iterate through each collection and delete it
        for collection in collections:
            collection_name = collection.name
            print(f"[INFO] Deleting collection: {collection_name}...")
            client.delete_collection(collection_name=collection_name)
            print(f"[SUCCESS] Deleted collection: {collection_name}")
        
        print("[INFO] All collections have been successfully deleted.")
    except Exception as e:
        print(f"[ERROR] Failed to delete collections: {str(e)}")

# Run the Process
if __name__ == "__main__":
    try:
        # delete_all_collections()
        results = search_qdrant("Am I eligible to apply for an RSTMH Early Career Grant?", FAQ_COLLECTION)
        for result in results:
            question = result.payload.get("question", "No question found")
            answer = result.payload.get("answer", "No answer found")
            score = result.score
            for _ in range(5):
                print("-----------------")
            print(f"Question: {question}")
            print(f"Answer: {answer}")
            print(f"Score: {score}")
            for _ in range(5):
                print("*")
        # Upload PDFs to Separate Collections
        # faq_pdf_path = 'faq.pdf'  # Replace with the path to faq.pdf
        # details_pdf_path = 'details.pdf'  # Replace with the path to details.pdf
        # upload_qa_to_qdrant(faq_pdf_path, 'faq', FAQ_COLLECTION)
        # upload_pdf_to_qdrant(details_pdf_path, 'details', DETAILS_COLLECTION)

        # # Example Query Handling
        # user_query = "Am I eligible to apply for an RSTMH Early Career Grant?"
        # answer = handle_user_query(user_query)
        # print(f"[ANSWER] {answer}")
    except Exception as e:
        print("[ERROR] Process terminated.")
        print(traceback.format_exc())