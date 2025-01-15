from http.client import HTTPException
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from pydantic import BaseModel
import requests
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from supabase_logging import log_interaction
import os
import re
import uuid
from dotenv import load_dotenv
from openai import OpenAI

app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')
# app.static_folder = '../cdn'  # Serve static files from the cdn folder
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})  # Enable CORS for all routes

# Serve files from the 'cdn' directory
@app.route('/cdn/huggingface.js')
def serve_huggingface_js():
    return send_from_directory('../cdn', 'huggingface.js')

@app.route('/cdn/chat-widget.js')
def serve_chat_widget_js():
    return send_from_directory('../cdn', 'chat-widget.js')

load_dotenv()

# Set the OpenAI API key
openai_client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# Qdrant Client Setup (Replace with your actual endpoint and key)
QDRANT_URL = os.getenv('QDRANT_URL')
API_KEY = os.getenv('QD_API_TOKEN')
COLLECTION_NAME = "pdf_vectors"
qdrant_client = QdrantClient(QDRANT_URL, api_key=API_KEY)

# Embedding Model
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# Define Pydantic model for query requests
class QueryRequest(BaseModel):
    user_query: str  # Changed `query` to `user_query` for consistency

@app.before_request
def handle_options():
    if request.method == "OPTIONS":
        response = app.make_default_options_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        return response

@app.route('/')
def index():
    return render_template('index.html')

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
        search_result = qdrant_client.search(
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
        print("Sending prompt to OpenAI GPT-4o-mini.")

        try:
            # Make API call to GPT-4o-mini
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # For Logging raw response for troubleshooting
            def log_llm_response(response):
                with open("llm_response_log.txt", "a", encoding="utf-8") as log_file:
                    log_file.write(f"{response}\n\n")

            # Log the raw response
            log_llm_response(response)

            # Extract and clean up the LLM response
            llm_reply = response.choices[0].message.content.strip()

            if "Answer:" in llm_reply:
                llm_reply = llm_reply.split("Answer:")[-1].strip()

            print(f"LLM Reply-------> : {llm_reply}")
        except Exception as e:
            print("Internal server error occurred.")
            print(str(e))
            return jsonify({"error": f"Internal server error: {str(e)}"}), 500


        # Generate user and session IDs for logging (replace with actual logic)
        user_id = request.headers.get("X-User-ID", str(uuid.uuid4()))  # Use header if available, else generate UUID
        session_id = request.headers.get("X-Session-ID", str(uuid.uuid4()))

        # Log interaction
        log_interaction(
            user_id=user_id,
            session_id=session_id,
            prompt=user_query,
            response=llm_reply,
            source_pdf="charity_guidelines.pdf",  # TODO: Update with actual PDF source, can't get it to work
            metadata={"ip": request.remote_addr, "user_agent": request.headers.get("User-Agent")}
        )

        return jsonify({
            "query": user_query,
            "answer": llm_reply,
            "context": relevant_chunks
        })

    except requests.exceptions.RequestException as e:
        print(f"Request to LLM API failed: {str(e)}")
        return jsonify({"error": f"LLM request failed: {str(e)}"}), 500

    except Exception as e:
        print("Internal server error occurred.")
        print(str(e))
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route('/test_qdrant', methods=['POST'])
def test_qdrant():
    user_query = request.json.get('query')
    
    # Generate embedding for the user query
    query_vector = embedder.encode([user_query])[0].tolist()

    # Perform search in Qdrant
    search_result = qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=3  # Get top 3 chunks
    )

    # Extract and return the matching chunks
    chunks = [result.payload['text'] for result in search_result if 'text' in result.payload]
    return jsonify({"chunks": chunks})


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
    port = int(os.getenv('PORT', 5000))  # Default to 5000 if PORT is not set
    app.run(host='0.0.0.0', port=port)
