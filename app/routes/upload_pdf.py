from flask import Blueprint, request, jsonify, render_template
from app.services.pdf_service import extract_text_from_pdf, extract_qa_from_pdf  # Extract text from PDFs
from app.services.qdrant_service import upload_chunks_to_qdrant, upload_qa_to_qdrant  # Upload to Qdrant
from sentence_transformers import SentenceTransformer
import uuid
import os

upload_pdf_bp = Blueprint("upload_pdf", __name__)

embedder = SentenceTransformer("all-MiniLM-L6-v2")  # Change model if needed
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@upload_pdf_bp.route("/upload-pdf", methods=["GET"])
def upload_pdf_form():
    """Render the web interface for PDF upload."""
    return render_template("upload.html")

@upload_pdf_bp.route("/upload-pdf", methods=["POST"])
def upload_pdf():
    """Handles PDF upload, extracts text, and uploads to Qdrant."""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded."}), 400
        
        file = request.files["file"]
        collection_name = request.form.get("collection_name", "pdf_collection")
        
        # Save PDF temporarily
        pdf_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{pdf_id}.pdf")
        file.save(file_path)
        
        # Extract text from PDF
        text_chunks = extract_text_from_pdf(file_path)
        if not text_chunks:
            return jsonify({"error": "No text extracted from the PDF."}), 400
        
        # Upload text to Qdrant
        upload_chunks_to_qdrant(text_chunks, pdf_id, collection_name, embedder)
        
        return jsonify({"pdf_id": pdf_id, "message": "PDF successfully uploaded and processed."}), 200
    
    except Exception as e:
        return jsonify({"error": f"Error processing PDF: {str(e)}"}), 500

@upload_pdf_bp.route("/upload-qa-form", methods=["GET"])
def upload_qa_form():
    """Render the web interface for QA PDF upload."""
    return render_template("upload_qa.html")

@upload_pdf_bp.route("/upload-qa", methods=["POST"])
def upload_qa():
    """Handles PDF upload, extracts QA pairs, and uploads to Qdrant."""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded."}), 400
        
        file = request.files["file"]
        collection_name = request.form.get("collection_name", "qa_collection")
        
        # Save PDF temporarily
        pdf_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{pdf_id}.pdf")
        file.save(file_path)
        
        # Extract QA pairs from PDF
        qa_pairs = extract_qa_from_pdf(file_path)
        if not qa_pairs:
            return jsonify({"error": "No QA pairs extracted from the PDF."}), 400
        
        # Upload QA pairs to Qdrant
        upload_qa_to_qdrant(qa_pairs, pdf_id, collection_name, embedder)
        
        return jsonify({"pdf_id": pdf_id, "message": "QA pairs successfully uploaded and processed."}), 200
    
    except Exception as e:
        return jsonify({"error": f"Error processing PDF: {str(e)}"}), 500