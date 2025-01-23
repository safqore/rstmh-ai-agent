from unittest.mock import MagicMock

def test_query_endpoint(client, mock_supabase, mock_qdrant):
    # Mock embedding service
    mock_embedding = MagicMock(return_value=[0.1, 0.2, 0.3])
    with client.application.app_context():
        # Mock the embedding service
        from app.services.embedding_service import generate_embedding
        generate_embedding.return_value = mock_embedding

    # Mock Qdrant search response
    mock_qdrant.search.return_value = [
        MagicMock(**{"payload": {"text": "Test result"}, "score": 0.95})
    ]

    # Perform the request
    response = client.post(
        "/query",
        json={"user_query": "Test query"},
        headers={"X-User-ID": "1234", "X-Session-ID": "5678"}
    )
    # Debug the response if the status code is not 200
    if response.status_code != 200:
        print("[DEBUG] Response data:", response.data.decode())

    assert response.status_code == 200
    assert "Test result" in response.json["context"][0]