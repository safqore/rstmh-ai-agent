from http.client import HTTPException
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from pydantic import BaseModel
import requests
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from supabase_logging import log_interaction, get_or_create_session
import os
import re
import uuid
from dotenv import load_dotenv
from openai import OpenAI
from qdrant_client.http import models
from toxicity_checker import ToxicityChecker

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

# Clear the environment variables comment this out before checking in
# os.environ.clear()

# Load dev environment variables
# load_dotenv(".env.dev")

# Load prod environment variables
load_dotenv()

# Set the OpenAI API key
openai_client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# Qdrant Client Setup (Replace with your actual endpoint and key)
QDRANT_URL = os.getenv('QDRANT_URL')
API_KEY = os.getenv('QD_API_TOKEN')
COLLECTION_NAME = "pdf_vectors"
print(f"[DEBUG]: {QDRANT_URL}, {API_KEY}")
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

# New Collection Names for Separate PDFs
FAQ_COLLECTION = "faq_vectors"
DETAILS_COLLECTION = "details_vectors"

# For Logging raw response for troubleshooting
def log_llm_response(response):
    with open("llm_response_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"{response}\n\n")

def search_with_fallback(query_vector, faq_collection, details_collection, top_k=3, threshold=0.8):
    """
    Search Qdrant collections with a fallback mechanism.

    Args:
        query_vector (list): The embedding of the query.
        faq_collection (str): The name of the FAQ collection.
        details_collection (str): The name of the Details collection.
        top_k (int): Number of top results to retrieve.
        threshold (float): Minimum score to consider a result as relevant.

    Returns:
        tuple: A tuple containing the search results and the source collection name.
    """
    try:
        print(f"[DEBUG] Searching FAQ collection: {faq_collection}")
        faq_results = qdrant_client.search(
            collection_name=faq_collection,
            query_vector=query_vector,
            limit=top_k
        )
        print(f"[DEBUG] FAQ Results: {faq_results}")

        if faq_results:
            # Check if any result meets the threshold
            if any(result.score >= threshold for result in faq_results):
                print("[DEBUG] Relevant FAQ result found.")
                return faq_results, faq_collection
            print("[DEBUG] FAQ results exist but none meet the threshold.")

        print("[INFO] Falling back to Details collection...")
        details_results = qdrant_client.search(
            collection_name=details_collection,
            query_vector=query_vector,
            limit=top_k
        )
        print(f"[DEBUG] Details Results: {details_results}")

        return details_results, details_collection

    except Exception as e:
        print(f"[ERROR] Error in search_with_fallback: {str(e)}")
        raise

@app.post("/query")
def query_pdf():
    try:
        print("[DEBUG] Received request at /query endpoint.")
        
        # Read user_id and session_id from headers or generate new ones
        user_id = request.headers.get("X-User-ID", str(uuid.uuid4()))  # Generate if missing
        session_id = request.headers.get("X-Session-ID", str(uuid.uuid4()))  # Generate if missing

        # Get or create a valid session
        session_id = get_or_create_session(user_id, session_id)

        # Extract user_query directly from the request body (JSON)
        data = request.json
        print(f"[DEBUG] Request payload: {data}")
        
        if not data or 'user_query' not in data:
            print("Missing or invalid JSON payload.")
            return jsonify({"error": "Invalid or missing JSON payload."}), 400

        user_query = data.get('user_query', None)
        print(f"User query: {user_query}")
        if not user_query:
            print("[DEBUG] Query is empty or missing.")
            return jsonify({"error": "Query cannot be empty"}), 400

        # Check for toxic content
        is_toxic, categories = ToxicityChecker.check_toxicity(user_query)
        if is_toxic:
            print(f"[DEBUG] Query flagged as toxic: {categories}")
            return jsonify({"answer": "Your query contains inappropriate content and cannot be processed."})

        # Generate embedding (vector) for the user query
        print("[DEBUG] Generating embedding for user query.")
        query_vector = embedder.encode([user_query])[0].tolist()
        print(f"[DEBUG] Generated query vector: {query_vector[:10]}...")

        # Search FAQ first, then fallback to Details
        print("[DEBUG] Invoking search_with_fallback...")
        search_results, source = search_with_fallback(query_vector, FAQ_COLLECTION, DETAILS_COLLECTION)

        if not search_results:
            print("[DEBUG] No results found in either collection.")
            return jsonify({"error": "No relevant information found."}), 404

        # Extract relevant chunks from the results
        relevant_chunks = []
        for result in search_results:
            if source == FAQ_COLLECTION:
                question = result.payload.get("question", "No question found")
                answer = result.payload.get("answer", "No answer found")
                score = result.score
                relevant_chunks.append(f"Question: {question}\nAnswer: {answer}\nScore: {score}")
            elif source == DETAILS_COLLECTION:
                text = result.payload.get("text", "No text found")
                score = result.score
                relevant_chunks.append(f"Text: {text}\nScore: {score}")

        if not relevant_chunks:
            print("[DEBUG] No relevant chunks extracted.")
            return jsonify({"error": "No relevant information found."}), 404

        # Combine the chunks into a single context
        context = "\n\n".join(relevant_chunks)
        print(f"[DEBUG] Context for LLM: {context[:200]}...")

        # Prepare LLM prompt
        prompt = (
            f"You are an expert assistant. Answer the following question based on the provided context.\n"
            f"You should only answer questions related to RSTMH Early Career Grants Programme.\n"
            f"If user asks questions unrelating to RSTMH Early Career Grants Programme, Politely inform user you can only answer question relating to RSTMH Early Career Grants Programme.\n"
            f"Context:\n{context}\n"            
            f"Question: {user_query}\n"
            f"Answer:"
        )
        print("[DEBUG] Sending prompt to OpenAI GPT-4o-mini.")

        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        # Log the raw response
        log_llm_response(response)

        llm_reply = response.choices[0].message.content.strip()
        print(f"[DEBUG] LLM Reply: {llm_reply}")

        if "Answer:" in llm_reply:
            llm_reply = llm_reply.split("Answer:")[-1].strip()

        # Log interaction
        log_interaction(
            user_id=user_id,
            session_id=session_id,
            prompt=user_query,
            response=llm_reply,
            source_pdf=source,
            metadata={"ip": request.remote_addr, "user_agent": request.headers.get("User-Agent")}
        )

        is_toxic, categories = ToxicityChecker.check_toxicity(llm_reply)
        if is_toxic:
            print(f"[DEBUG] Response flagged as toxic: {categories}")
            return jsonify({"answer": "The generated response was flagged as inappropriate. Please try again."})

        return jsonify({
            "query": user_query,
            "answer": llm_reply,
            "context": relevant_chunks,
            "source": source
        })

    except requests.exceptions.RequestException as e:
        print(f"Request to LLM API failed: {str(e)}")
        return jsonify({"error": f"LLM request failed: {str(e)}"}), 500
    
    except Exception as e:
        print(f"[ERROR] Exception in /query: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))  # Default to 5000 if PORT is not set
    app.run(host='0.0.0.0', port=port)
