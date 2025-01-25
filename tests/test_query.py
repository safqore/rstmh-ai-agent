from unittest.mock import MagicMock
from app.services.supabase_logging import SupabaseLogger
from datetime import datetime, timezone, timedelta

def test_query_endpoint(client, mock_supabase, mock_qdrant):
    # Mock SupabaseLogger instance
    logger = SupabaseLogger(supabase_client=mock_supabase)

    # Mock session existence in the `sessions` table
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = {
        "data": [{"session_id": "5678", "last_active": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()}]
    }

    # Mock embedding service
    mock_embedding = MagicMock(return_value=[0.1, 0.2, 0.3])
    with client.application.app_context():
        from app.services.embedding_service import generate_embedding
        generate_embedding.return_value = mock_embedding

    # Mock Qdrant search response
    mock_qdrant.search.return_value = [
        MagicMock(payload={"question": "What is Python?", "answer": "Python is a programming language."}, score=0.95)
    ]

    # Perform the request
    response = client.post(
        "/query",
        json={"user_query": "Test query"},
        headers={"X-User-ID": "1234", "X-Session-ID": "5678"}
    )

    # Debug response if needed
    if response.status_code != 200:
        print("[DEBUG] Response data:", response.data.decode())

    # Assertions
    assert response.status_code == 200
    assert "Question: What is Python?\nAnswer: Python is a programming language.\nScore: 0.95" in response.json["context"]
    assert response.json["source"] == "faq_vectors"