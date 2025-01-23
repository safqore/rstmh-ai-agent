from unittest.mock import MagicMock
from app.services.qdrant_service import list_collections, search_with_fallback

def test_list_collections(mock_qdrant):
    # Mock the Qdrant collection response
    mock_qdrant.get_collections.return_value.collections = [
        {"name": "test_collection", "points_count": 5}  # Use a dictionary instead of MagicMock
    ]

    collections = list_collections()

    # Validate the mock response
    assert len(collections) == 1
    assert collections[0]["name"] == "test_collection"

def test_search_with_fallback(mock_qdrant):
    # Mock FAQ collection search results
    mock_qdrant.search.side_effect = [
        [
            MagicMock(payload={"question": "What is Python?", "answer": "Python is a programming language."}, score=0.9)
        ],  # FAQ search results
        [
            MagicMock(payload={"text": "Details result text."}, score=0.8)
        ]  # Details search results
    ]

    # Test FAQ search success
    query_vector = [0.1, 0.2, 0.3]
    results, source = search_with_fallback(query_vector, "FAQ_vectors", "details_vectors")
    assert source == "FAQ_vectors"
    assert len(results) == 1
    assert results[0].payload["question"] == "What is Python?"
    assert results[0].payload["answer"] == "Python is a programming language."
    assert results[0].score == 0.9

    # Test fallback to details
    mock_qdrant.search.side_effect = [
        [
            MagicMock(payload={"question": "What is Python?", "answer": "Python is a programming language."}, score=0.5)
        ],  # FAQ search results below threshold
        [
            MagicMock(payload={"text": "Fallback to details text."}, score=0.85)
        ]  # Details search results
    ]

    results, source = search_with_fallback(query_vector, "FAQ_vectors", "details_vectors")
    assert source == "details_vectors"
    assert len(results) == 1
    assert results[0].payload["text"] == "Fallback to details text."
    assert results[0].score == 0.85