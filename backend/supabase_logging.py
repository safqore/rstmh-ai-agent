import os
from supabase import create_client, Client
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()
# Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def log_interaction(user_id, session_id, prompt, response, source_pdf=None, section_reference=None, metadata=None):
    """
    Logs chatbot interaction to the Supabase database.

    Args:
        user_id (str): Unique identifier for the user.
        session_id (str): Unique identifier for the session.
        prompt (str): User query.
        response (str): Chatbot response.
        source_pdf (str): Source PDF name.
        section_reference (str): Reference to the section of the PDF.
        metadata (dict): Additional metadata, e.g., IP, user-agent.
    """
    data = {
        "user_id": user_id,
        "session_id": session_id,
        "timestamp": datetime.utcnow().isoformat(),  # Use UTC timestamp
        "prompt": prompt,
        "response": response,
        "source_pdf": source_pdf,
        "section_reference": section_reference,
        "metadata": metadata,
        "is_compliant": True  # Default value for compliance flag
    }

    try:
        result = supabase.table("interactions").insert(data).execute()
        print("Logged interaction successfully:", result.data)
    except Exception as e:
        print(f"Error logging interaction to Supabase: {e}")
