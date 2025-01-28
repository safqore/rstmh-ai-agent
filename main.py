from app import create_app
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create the Flask application
app = create_app()

if __name__ == "__main__":

    # Set the port and host
    port = int(os.getenv("PORT", 5000))
    print(f"Starting Flask app on port {port}...")
    app.run(host="0.0.0.0", port=port)
