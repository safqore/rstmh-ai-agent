from qdrant_client.http.models import PointStruct
import uuid
from app.services.embedding_service import generate_embedding  # or use embedder.encode()
from app.services.qdrant_service import client

def insert_manual_override(collection_name):
    manual_fallback_entry = {
        "text": (
            "Applicants do not need to be employed to apply for the RSTMH Early Career Grants Programme. "
            "While being employed or affiliated with an organisation is encouraged, the programme explicitly "
            "states that applications will also be considered from those who are not affiliated or employed."
        ),
        "pdf_id": "manual_override",
        "page": 0,
        "source": "manual_context",
        "question_tag": "employment_requirement"
    }

    vector = generate_embedding(manual_fallback_entry["text"])  # or embedder.encode(...).tolist()

    point = PointStruct(
        id=str(uuid.uuid4()),
        vector=vector,
        payload=manual_fallback_entry
    )

    client.upsert(collection_name=collection_name, points=[point])
    print("[✅] Manual override inserted.")