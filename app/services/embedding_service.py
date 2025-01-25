from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

embedder = SentenceTransformer('all-MiniLM-L6-v2')

def generate_embedding(query):
    return embedder.encode([query])[0].tolist()