from dotenv import load_dotenv
from app.services.qdrant_service import list_collections
from pprint import pprint

# Load environment variables
load_dotenv()

def main():
    """
    Runs the Qdrant inspection script locally.
    """
    print("[INFO] Running Qdrant inspection script...")
    try:
        collections = list_collections()
        if not collections:
            print("[INFO] No collections found in Qdrant.")
        else:
            print("[INFO] Listing all collections:")
            pprint(collections)
    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")

if __name__ == "__main__":
    main()