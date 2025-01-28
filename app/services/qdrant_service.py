from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv
import os

# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the .env file
env_path = os.path.join(current_dir, '../..', '.env')
# Load the environment variables
load_dotenv(dotenv_path=env_path)

# print(os.getenv('QDRANT_URL'), os.getenv('QD_API_TOKEN'))

# Initialize Qdrant client
client = QdrantClient(
    url=os.getenv('QDRANT_URL'),  # Qdrant URL from environment variables
    api_key=os.getenv('QD_API_TOKEN')  # Qdrant API Key from environment variables
)

def initialize_qdrant_client():
    """
    Initializes the Qdrant client using environment variables.
    """
    QDRANT_URL = os.getenv('QDRANT_URL')
    API_KEY = os.getenv('QD_API_TOKEN')

    if not QDRANT_URL or not API_KEY:
        raise ValueError("QDRANT_URL and QD_API_TOKEN environment variables must be set.")

    return QdrantClient(QDRANT_URL, api_key=API_KEY)

def list_collections():
    """
    Lists all collections in Qdrant and their details.

    Returns:
        list: A list of dictionaries containing collection details.
    """
    try:
        collections = client.get_collections()
        collection_details = []

        for collection in collections.collections:
            collection_info = client.get_collection(collection_name=collection.name)

            collection_details.append({
                "name": collection.name,
                "vector_size": collection_info.config.params.vectors.size,
                "distance_metric": collection_info.config.params.vectors.distance,
                "points_count": collection_info.points_count,
            })

        return collection_details

    except Exception as e:
        print(f"[ERROR] Failed to list collections: {e}")
        return []

def print_collections():
    """
    Prints all collections and their details in a readable format (for debugging or administrative purposes).
    """
    collections = list_collections()
    if not collections:
        print("[INFO] No collections found in Qdrant.")
        return

    print("[INFO] Collections in Qdrant:")
    for collection in collections:
        print(f"Name: {collection['name']}")
        print(f"Vector size: {collection['vector_size']}")
        print(f"Distance metric: {collection['distance_metric']}")
        print(f"Points count: {collection['points_count']}")
        print("-" * 50)

def recreate_qdrant_collection(vector_size, collection_name):
    """Deletes and recreates a Qdrant collection."""
    if client.collection_exists(collection_name=collection_name):
        print(f"[INFO] Deleting existing collection: {collection_name}...")
        client.delete_collection(collection_name=collection_name)
    print(f"[INFO] Creating new collection: {collection_name}...")
    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE)
    )

def upload_qa_to_qdrant(qa_pairs, pdf_id, collection_name, embedder):
    """Uploads question-answer pairs as vectors to a Qdrant collection."""
    questions = [q for q, _ in qa_pairs]
    embeddings = embedder.encode(questions)
    recreate_qdrant_collection(len(embeddings[0]), collection_name)
    points = [
        models.PointStruct(
            id=idx,
            vector=embedding.tolist(),
            payload={
                "pdf_id": pdf_id,
                "question": question,
                "answer": answer
            }
        )
        for idx, (embedding, (question, answer)) in enumerate(zip(embeddings, qa_pairs))
    ]
    client.upsert(collection_name=collection_name, points=points)
    print(f"[SUCCESS] Uploaded {len(points)} QA pairs to collection '{collection_name}'.")

def upload_chunks_to_qdrant(chunks, pdf_id, collection_name, embedder):
    """Uploads text chunks as vectors to a Qdrant collection."""
    embeddings = embedder.encode(chunks)
    recreate_qdrant_collection(len(embeddings[0]), collection_name)
    points = [
        models.PointStruct(
            id=idx,
            vector=embedding.tolist(),
            payload={"text": chunk, "pdf_id": pdf_id}
        )
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings))
    ]
    client.upsert(collection_name=collection_name, points=points)
    print(f"[SUCCESS] Uploaded {len(points)} text chunks to collection '{collection_name}'.")

def search_qdrant(query, collection_name, embedder, top_k=3):
    """Searches a Qdrant collection for the most relevant results."""
    query_vector = embedder.encode([query])[0].tolist()
    results = client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=top_k
    )
    print(f"[DEBUG] Search Results in {collection_name}: {results}")
    return results

def search_with_fallback(query_vector, faq_collection, details_collection, top_k=3, threshold=0.8):
    """
    Searches Qdrant collections with a fallback mechanism.

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
        faq_results = client.search(
            collection_name=faq_collection,
            query_vector=query_vector,
            limit=top_k
        )
        print(f"[DEBUG] FAQ Results: {faq_results}")

        # Check if any FAQ result meets the threshold
        # if faq_results and any(result.score >= threshold for result in faq_results):
        if faq_results:
            # Check if any result meets the threshold
            if any(getattr(result, "score", 0) >= threshold for result in faq_results):
                print("[DEBUG] Relevant FAQ result found.")
                return faq_results, faq_collection

        print("[INFO] Falling back to Details collection...")
        details_results = client.search(
            collection_name=details_collection,
            query_vector=query_vector,
            limit=top_k
        )
        print(f"[DEBUG] Details Results: {details_results}")

        return details_results, details_collection

    except Exception as e:
        print(f"[ERROR] Error in search_with_fallback: {str(e)}")
        raise

def delete_all_collections():
    """Deletes all collections from Qdrant."""
    try:
        collections = client.get_collections().collections
        if not collections:
            print("[INFO] No collections found in Qdrant.")
            return
        for collection in collections:
            collection_name = collection.name
            print(f"[INFO] Deleting collection: {collection_name}...")
            client.delete_collection(collection_name=collection_name)
            print(f"[SUCCESS] Deleted collection: {collection_name}")
    except Exception as e:
        print(f"[ERROR] Failed to delete collections: {str(e)}")