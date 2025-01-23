from flask import Blueprint, request, jsonify
from app.services.qdrant_service import search_with_fallback
from app.services.embedding_service import generate_embedding
from app.services.supabase_logging import SupabaseLogger
from dotenv import load_dotenv
from flask import Blueprint, render_template, current_app
import uuid
import os

# Load environment variables
load_dotenv()

query_bp = Blueprint('query', __name__)

# Initialize Supabase logger
logger = SupabaseLogger()

FAQ_COLLECTION = "faq_vectors"
DETAILS_COLLECTION = "details_vectors"
PORT = os.getenv('PORT'),  # get port

@query_bp.route("/")
def index():
    # Use current_app instead of app
    script_base_url = (
        f"http://127.0.0.1:{PORT}/cdn"  # Internal during local development
        if current_app.config.get("ENV") == "development"  # ENV should be set in your Flask app
        else "https://rsmth-test-bot-cdn.onrender.com"  # External for production
    )
    return render_template("index.html", script_base_url=script_base_url)

@query_bp.route("/query", methods=["POST"])
def query_pdf():
    try:
        # Retrieve user ID and session ID from headers or generate new ones
        user_id = request.headers.get("X-User-ID", str(uuid.uuid4()))
        session_id = request.headers.get("X-Session-ID", str(uuid.uuid4()))

        # Extract user query from the JSON payload
        data = request.json
        if not data or "user_query" not in data:
            return jsonify({"error": "Invalid or missing JSON payload."}), 400

        user_query = data["user_query"]
        if not user_query.strip():
            return jsonify({"error": "Query cannot be empty."}), 400

        # Generate embedding (vector) for the query
        query_vector = generate_embedding(user_query)

        # Perform search with fallback
        search_results, source_collection = search_with_fallback(
            query_vector, FAQ_COLLECTION, DETAILS_COLLECTION
        )

        # If no results found
        if not search_results:
            return jsonify({"error": "No relevant information found."}), 404

        # Format the results
        relevant_chunks = []
        for result in search_results:
            if source_collection == FAQ_COLLECTION:
                question = result.payload.get("question", "No question found")
                answer = result.payload.get("answer", "No answer found")
                score = result.score
                print("[DEBUG] FAQ question: ", question, "\nFAQ Answer: ", answer)
                relevant_chunks.append(f"Question: {question}\nAnswer: {answer}\nScore: {score}")
            elif source_collection == DETAILS_COLLECTION:
                text = result.payload.get("text", "No text found")
                print("[DEBUG] Details Results:", text)
                score = result.score
                relevant_chunks.append(f"Text: {text}\nScore: {score}")

        # Combine the chunks for context
        context = "\n\n".join(relevant_chunks)

        # Log the interaction
        logger.log_interaction(
            user_id=user_id,
            session_id=session_id,
            prompt=user_query,
            response=context,
            source_pdf=source_collection,
            metadata={
                "ip": request.remote_addr,
                "user_agent": request.headers.get("User-Agent")
            }
        )

        return jsonify({
            "query": user_query,
            "context": relevant_chunks,
            "source": source_collection
        })

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500