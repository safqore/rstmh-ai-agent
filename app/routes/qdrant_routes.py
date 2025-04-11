from flask import Blueprint, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
from app.services.pdf_service import extract_qa_from_pdf, chunk_text, extract_text_from_pdf
from app.services.qdrant_service import upload_qa_to_qdrant, upload_chunks_to_qdrant
from app.services.embedding_service import embedder  # Ensure this exists and provides embeddings
from app.scripts.ingest_manual import insert_manual_override
from dotenv import load_dotenv

qdrant_bp = Blueprint('qdrant_pdf', __name__, url_prefix='/qdrant-pdf')

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
load_dotenv()

@qdrant_bp.route("/upload", methods=["GET"])
def upload_page():
    """Serves the HTML page for uploading PDFs."""
    return render_template("upload_pdf.html")

@qdrant_bp.route("/upload/qa", methods=["POST"])
def upload_qa_pdf():
    """Handles PDF uploads, extracts Q&A pairs, and stores them in Qdrant."""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided."}), 400
    
    file = request.files['file']
    collection_name = request.form.get('collection_name', os.getenv('FAQ_COLLECTION'))  # Allow custom collection name
    
    if file.filename == '':
        return jsonify({"error": "No selected file."}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    pdf_id = filename  # Using filename as unique identifier
    qa_pairs = extract_qa_from_pdf(filepath)
    
    upload_qa_to_qdrant(qa_pairs, pdf_id, collection_name, embedder)
    
    return jsonify({"message": f"Q&A pairs from '{filename}' processed and uploaded to Qdrant collection '{collection_name}'."})

@qdrant_bp.route("/upload/text", methods=["POST"])
def upload_text_pdf():
    """Handles PDF uploads, extracts raw text, splits into chunks, and stores them in Qdrant."""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided."}), 400
    
    file = request.files['file']
    collection_name = request.form.get('collection_name', os.getenv('DETAILS_COLLECTION'))  # Allow custom collection name
    
    if file.filename == '':
        return jsonify({"error": "No selected file."}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    pdf_id = filename  # Using filename as unique identifier
    text = extract_text_from_pdf(filepath)
    text_chunks = chunk_text(text)
    
    upload_chunks_to_qdrant(text_chunks, pdf_id, collection_name, embedder)
    
    return jsonify({"message": f"Raw text from '{filename}' processed and uploaded to Qdrant collection '{collection_name}'."})

@qdrant_bp.post("/seed/manual-override")
def seed_manual_override():
    insert_manual_override(collection_name=request.form.get('collection_name', os.getenv('DETAILS_COLLECTION')) )
    return {"status": "done"}
