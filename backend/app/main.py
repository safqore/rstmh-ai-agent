import os
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import PyPDF2
import faiss
import numpy as np
from langchain.text_splitter import CharacterTextSplitter
from sentence_transformers import SentenceTransformer
from huggingface_hub import InferenceClient

app = FastAPI()

# CORS Configuration
origins = [
    "http://localhost:3000",  # For local development
    "https://rsmth-demo.netlify.app"  # Your frontend on Netlify
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Initialize Hugging Face Inference API client
hf_api_key = os.getenv('HF_API_TOKEN')  # Replace with your Hugging Face API key
hf_model_name = "Qwen/QwQ-32B-Preview"  # Replace with the desired Hugging Face model
hf_client = InferenceClient(model=hf_model_name, token=hf_api_key)

# Load the pre-trained SentenceTransformer model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize FAISS index
dimension = 384
index = faiss.IndexFlatL2(dimension)  # L2 distance index (Euclidean distance)

# Store the chunks and corresponding metadata
chunk_texts = []

# Define Pydantic model for query requests
class QueryRequest(BaseModel):
    user_query: str  # Changed `query` to `user_query` for consistency


@app.post("/read-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="The file must be a PDF")

        pdf_reader = PyPDF2.PdfReader(file.file)
        text = ""  # Initialize the text variable
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text  # Append extracted text

        if not text.strip():  # Ensure text is not empty
            raise HTTPException(status_code=400, detail="No text found in the PDF")

        # Split text into chunks
        text_splitter = CharacterTextSplitter(separator="\n", chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_text(text)

        # Remove duplicate chunks
        unique_chunks = list(set(chunks))  # Deduplicate chunks

        # Turn unique chunks into vectors
        chunk_vectors = embedder.encode(unique_chunks)

        # Store the vectors in the FAISS index
        faiss_index = np.array(chunk_vectors, dtype=np.float32)
        index.add(faiss_index)

        # Store unique chunks in memory for querying
        global chunk_texts
        chunk_texts.extend(unique_chunks)

        # Check FAISS index status
        faiss_index_count = index.ntotal

        return {
            "message": "PDF uploaded and processed successfully!",
            "num_chunks": len(unique_chunks),
            "faiss_index_count": faiss_index_count,
            "chunks": unique_chunks[:5],  # First 5 unique chunks as preview
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/query/")
async def query_pdf(user_query: str):
    try:
        if not user_query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        # Convert the query into a vector
        query_vector = embedder.encode([user_query])[0]

        # Perform a similarity search in FAISS
        query_vector = np.array([query_vector], dtype=np.float32)
        k = 5  # Number of closest neighbors to retrieve
        distances, indices = index.search(query_vector, k)

        # Gather the most relevant chunks
        unique_indices = set(indices[0])
        relevant_chunks = [chunk_texts[idx] for idx in unique_indices if idx < len(chunk_texts)]

        # Combine relevant chunks into a single context
        context = " ".join(relevant_chunks)

        # Use Hugging Face Inference API to generate an answer
        prompt = (
            f"Context: {context}\n\n"
            f"Please answer the following question based on the context provided:\n"
            f"Question: {user_query}\n"
            f"Answer:"
        )
        hf_response = hf_client.text_generation(
            prompt, max_new_tokens=500, temperature=0.5, top_p=0.9
        )

        # Process response to keep only the first answer
        if "Answer:" in hf_response:
            answer = hf_response.split("Answer:")[1].split("Question:")[0].strip()
        else:
            answer = hf_response.strip()

        return {
            "query": user_query,
            "answer": answer,
            "relevant_chunks": relevant_chunks,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


    
@app.post("/clear/")
async def clear_knowledge_base():
    """
    Clears the FAISS index, chunks, and associated data.
    """
    global index, chunk_texts

    # Reinitialize the FAISS index
    dimension = 384
    index = faiss.IndexFlatL2(dimension)  # Reset to an empty FAISS index

    # Clear the chunks
    chunk_texts = []

    return {"message": "Knowledge base cleared successfully!"}
