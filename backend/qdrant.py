from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
import PyPDF2
import traceback
import os

# Qdrant Cloud setup
QDRANT_URL = "https://1c680bc9-2d9a-4b74-9ac9-8b537f9e1557.us-east4-0.gcp.cloud.qdrant.io"
API_KEY = os.getenv('QD_API_TOKEN')
COLLECTION_NAME = "pdf_vectors"

# Initialize Qdrant client and embedding model
client = QdrantClient(QDRANT_URL, api_key=API_KEY)
embedder = SentenceTransformer('all-MiniLM-L6-v2')

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
def recreate_qdrant_collection(vector_size):
    # Check if collection exists
    if client.collection_exists(collection_name=COLLECTION_NAME):
        print("[INFO] Deleting existing collection...")
        client.delete_collection(collection_name=COLLECTION_NAME)
    
    # Recreate the collection with the same vector size and cosine distance
    print("[INFO] Creating new collection...")
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE)
    )

# Upload chunks of the PDF to Qdrant as vectors with integer IDs
def upload_pdf_to_qdrant(pdf_path, pdf_id):
    # Extract full text from the PDF
    text = extract_text_from_pdf(pdf_path)

    # Break the text into overlapping chunks
    chunks = chunk_text(text)

    # Generate embeddings (vectors) for each chunk
    embeddings = embedder.encode(chunks)

    # Recreate collection to clear old vectors
    recreate_qdrant_collection(vector_size=len(embeddings[0]))

    # Upload each chunk as a vector with a unique integer ID
    points = [
        models.PointStruct(
            id=idx,  # Use the chunk index as the point ID
            vector=embedding.tolist(),
            payload={"text": chunk, "pdf_id": pdf_id}
        )
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings))
    ]
    
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"[SUCCESS] Uploaded {len(points)} chunks from {pdf_path} to Qdrant.")

# Run the process
if __name__ == "__main__":
    try:
        pdf_path = 'rstmh_pdf.pdf'  # Replace with the path to your PDF
        pdf_id = "rstmh_2024"  # Unique ID for this PDF
        print(f"[INFO] Processing PDF: {pdf_path}")
        
        # Extract text
        text = extract_text_from_pdf(pdf_path)
        if not text:
            raise Exception("No text extracted. Stopping execution.")
        
        # Chunk text
        chunks = chunk_text(text)
        if not chunks:
            raise Exception("No chunks generated. Stopping execution.")
        
        # Upload vectors with both path and PDF ID
        upload_pdf_to_qdrant(pdf_path, pdf_id)
        print("[SUCCESS] Entire process completed successfully.")
        
    except Exception as e:
        print("[ERROR] Process terminated.")
        print(traceback.format_exc())
