from qdrant_client import QdrantClient
import os

# Qdrant Cloud setup
QDRANT_URL = "https://1c680bc9-2d9a-4b74-9ac9-8b537f9e1557.us-east4-0.gcp.cloud.qdrant.io"
API_KEY = os.getenv('QD_API_TOKEN')

client = QdrantClient(QDRANT_URL, api_key=API_KEY)

# List all collections
collections = client.get_collections()

print("[INFO] Collections in Qdrant:")
for collection in collections.collections:
    print(f"Name: {collection.name}")

    # Fetch full configuration for each collection
    collection_info = client.get_collection(collection_name=collection.name)

    # Access vector size and distance metric correctly
    vector_size = collection_info.config.params.vectors.size
    distance_metric = collection_info.config.params.vectors.distance

    print(f"Vector size: {vector_size}")
    print(f"Distance metric: {distance_metric}")
    print("-" * 50)

    # Print the total number of vectors (points)
    print(f"[INFO] Collection '{collection.name}' has {collection_info.points_count} vectors (chunks).")




