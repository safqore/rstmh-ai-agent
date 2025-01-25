from app.services.qdrant_service import search_qdrant
from app.services.pdf_service import chunk_text
from sentence_transformers import SentenceTransformer

# Initialize embedding model
embedder = SentenceTransformer('all-MiniLM-L6-v2')

FAQ_COLLECTION = "faq_vectors"
DETAILS_COLLECTION = "details_vectors"

def handle_user_query(query):
    """Handles user queries by searching through Qdrant collections."""
    faq_results = search_qdrant(query, FAQ_COLLECTION, embedder)
    if faq_results and faq_results[0].score > 0.8:
        return faq_results[0].payload["answer"]

    details_results = search_qdrant(query, DETAILS_COLLECTION, embedder)
    if details_results:
        return details_results[0].payload["text"]

    return "Sorry, no relevant information found."