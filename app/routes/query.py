from flask import Blueprint, request, jsonify, current_app
from app.services.qdrant_service import search_with_fallback
from app.services.embedding_service import generate_embedding
from app.services.supabase_logging import SupabaseLogger
from app.services.llm_service import get_llm_response
from app.services.toxicity_checker_service import ToxicityChecker
from dotenv import load_dotenv
from flask import Blueprint, render_template, current_app
import uuid
import os

# os.environ.clear
# Load environment variables
load_dotenv()

query_bp = Blueprint('query', __name__)

# Initialize Supabase logger
logger = SupabaseLogger()

FAQ_COLLECTION = "faq_vectors"
DETAILS_COLLECTION = "details_vectors"

# Load environment variables
PORT = os.getenv('PORT', 5000)

def get_base_urls():
    """Utility function to compute script_base_url and base_url."""
    script_base_url = (
        f"http://127.0.0.1:{PORT}/cdn"  # Internal during local development
        if current_app.config.get("ENV") == "development"  # ENV should be set in your Flask app
        else "https://rstmh-ai-agent-cdn.onrender.com"  # External for production
    )
    base_url = (
        f"http://127.0.0.1:{PORT}"
        if current_app.config.get("ENV") == "development"
        else "https://rstmh-ai-agent.onrender.com"
    )
    return script_base_url, base_url

@query_bp.route("/")
def index():
    # Call the utility function to get the URLs
    script_base_url, base_url = get_base_urls()
    print(f"[DEBUG]: script_base_url: {script_base_url}\nbase_url: {base_url}")
    return render_template("index.html", script_base_url=script_base_url, base_url=base_url)

@query_bp.route("/debug")
def debug():
    # Call the same utility function to get the URLs
    script_base_url, base_url = get_base_urls()
    return jsonify({
        "ENV": current_app.config.get("ENV"),
        "script_base_url": script_base_url,
        "base_url": base_url
    })

@query_bp.route("/query", methods=["POST"])
def query_handler():
    try:
        # Retrieve user ID and session ID from headers or generate new ones
        user_id = request.headers.get("X-User-ID")
        if user_id in [None, 'null']:
            user_id = str(uuid.uuid4())

        session_id = request.headers.get("X-Session-ID")
        if session_id in [None, 'null']:
            session_id = str(uuid.uuid4())

        print(f"[DEBUG]: user_id: {user_id} \n session_id: {session_id}")

        # Extract user query from the JSON payload
        data = request.json
        if not data or "user_query" not in data:
            return jsonify({"error": "Invalid or missing JSON payload."}), 400

        user_query = data.get("user_query", "").strip()
        if not user_query.strip():
            return jsonify({"error": "Query cannot be empty.", "error_code": "EMPTY_QUERY"}), 400
        
        # Check for toxic content
        is_toxic, categories = ToxicityChecker.check_toxicity(user_query)
        if is_toxic:
            print(f"[DEBUG] Query flagged as toxic: {categories}")
            return jsonify({"answer": "Your query contains inappropriate content and cannot be processed."})

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

        llm_reply = get_llm_response(query=user_query,context=context)

        # Ensure session exists
        session_id=logger.get_or_create_session(user_id=user_id, session_id=session_id)

        # Log the interaction
        logger.log_interaction(
            user_id=user_id,
            session_id=session_id,
            prompt=user_query,
            response=llm_reply,
            source_pdf=source_collection,
            metadata={
                "ip": request.remote_addr,
                "user_agent": request.headers.get("User-Agent")
            }
        )

        # check llm reply for toxicity
        is_toxic, categories = ToxicityChecker.check_toxicity(llm_reply)
        if is_toxic:
            print(f"[DEBUG] Response flagged as toxic: {categories}")
            llm_reply = "The generated response was flagged as inappropriate. Please try again."

        return jsonify({
            "user_id": user_id,
            "session_id": session_id,
            "query": user_query,
            "answer": llm_reply,
            "context": relevant_chunks,
            "source": source_collection
        })

    except Exception as e:
        current_app.logger.error("Error during query processing: %s", str(e), exc_info=True)
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
