from http.client import HTTPException
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pydantic import BaseModel
import requests
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import os
import re

app = Flask(__name__) # <--- FOR DEPLOYMENT!!!

# FOR DEPLOYMENT!!! -- Allow specific frontend origin (Netlify) 
CORS(app, resources={r"/api/*": {"origins": ["https://rsmth-demo.netlify.app"]}})


HF_API_URL = 'https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill'
HF_API_TOKEN = os.getenv('HF_API_TOKEN')  # Key to be picked up with environment variables

QDRANT_URL = "https://1c680bc9-2d9a-4b74-9ac9-8b537f9e1557.us-east4-0.gcp.cloud.qdrant.io"
QD_API_KEY = os.getenv('QD_API_TOKEN')
client = QdrantClient(QDRANT_URL, api_key=QD_API_KEY)
COLLECTION_NAME = "pdf_vectors"


# Embedding Model
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# Define Pydantic model for query requests
class QueryRequest(BaseModel):
    user_query: str  # Changed `query` to `user_query` for consistency

@app.post("/query")
def query_pdf():
    try:
        print("Received request on /query endpoint.")

        # Extract user_query directly from the request body (JSON)
        data = request.json
        print(f"Incoming JSON Payload: {data}")

        if not data or 'user_query' not in data:
            print("Missing or invalid JSON payload.")
            return jsonify({"error": "Invalid or missing JSON payload."}), 400

        user_query = data.get('user_query')
        print(f"User query: {user_query}")

        if not user_query:
            print("Query is empty.")
            return jsonify({"error": "Query cannot be empty"}), 400

        # Generate embedding (vector) for the user query
        print("Generating embeddings for user query.")
        query_vector = embedder.encode([user_query])[0].tolist()
        print(f"Generated embedding vector (first 10 values): {query_vector[:10]}...")

        # Search Qdrant for the top 10 matching chunks
        print("Querying Qdrant for matching vectors.")
        search_result = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=10  # Retrieve top 10 most relevant chunks
        )

        # Log Qdrant search response
        # print(f"Qdrant search result: {search_result}")

        # Extract and combine relevant text from the search results
        relevant_chunks = [result.payload['text'] for result in search_result if 'text' in result.payload]
        # print(f"Retrieved {len(relevant_chunks)} chunks from Qdrant.")

        # If no chunks are found, return an error
        if not relevant_chunks:
            print("No relevant chunks found in Qdrant.")
            return jsonify({"error": "No relevant information found."}), 404

        # Combine the chunks into a single context for the LLM
        context = " ".join(relevant_chunks)
        # print(f"Context prepared for LLM ---> (first 200 chars): {context[:200]}...")

        # Truncate context if it's too long (to avoid exceeding API limits)
        # MAX_CONTEXT_LENGTH = 1000
        # if len(context) > MAX_CONTEXT_LENGTH:
        #     print(f"Context too long ({len(context)} chars), truncating...")
        #    context = context[:MAX_CONTEXT_LENGTH]

        # Prepare the LLM prompt with context
        prompt = (
            f"You are an expert assistant. Answer the following question based on the provided context.\n\n"
            f"Context:\n{context}\n\n"
            f"Ignore any external knowledge and focus solely on the context above.\n"
            f"Question: {user_query}\n"
            f"Answer:"
        )
        print("Sending prompt to LLM.")

        # Call Hugging Face LLM API with the combined context
        headers = {
            "Authorization": f"Bearer {HF_API_TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 1000  # Adjust this to a larger number if necessary
            },
            "options": {"wait_for_model": True}
        }
        
        print(f"Payload sent to LLM: {payload}")

        response = requests.post(HF_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        print("Received successful response from Hugging Face API.")

        data = response.json()
        print(f"Raw LLM response ----> : {data}")

        # Handle different response structures
        if isinstance(data, list) and data:
            llm_reply = data[0].get('generated_text', 'No response.')
        elif isinstance(data, dict):
            llm_reply = data.get('generated_text', 'No response.')
        else:
            llm_reply = "No response received from LLM."

        # Extract the actual answer from the response
        if "Answer:" in llm_reply:
            llm_reply = llm_reply.split("Answer:")[-1].strip()

        return jsonify({
            "query": user_query,
            "answer": llm_reply
            # "context": relevant_chunks
        })

    except requests.exceptions.RequestException as e:
        print(f"Request to LLM API failed: {str(e)}")
        return jsonify({"error": f"LLM request failed: {str(e)}"}), 500

    except Exception as e:
        print("Internal server error occurred.")
        print(str(e))
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')

    if not user_message:
        return jsonify({"reply": "Message is required."}), 400

    payload = {
        "inputs": user_message,
        "options": {"wait_for_model": True}
    }

    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload)
        response.raise_for_status()

        data = response.json()
        print("API Response: ", data)  # Debugging line
        reply = data[0].get('generated_text', 'No response.')
        return jsonify({"reply": reply.strip()})

    except requests.exceptions.RequestException as e:
        print(f"Error contacting Hugging Face API: {e}")
        return jsonify({"reply": "An error occurred while fetching the response."}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use PORT from environment or default to 5000
    app.run(host='0.0.0.0', port=port)
