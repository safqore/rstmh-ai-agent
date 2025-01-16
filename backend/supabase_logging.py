import os
import uuid
from supabase import create_client, Client
from datetime import datetime
from dotenv import load_dotenv
from datetime import datetime, timedelta

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


def get_or_create_session(user_id, session_id):
    """
    Retrieve or create a session by updating the `interactions` table.
    
    Args:
        user_id (str): Unique user identifier.
        session_id (str): Current session ID provided by the client.
    
    Returns:
        str: Valid session ID.
    """
    # Check if the session exists and retrieve the latest `last_active` timestamp
    result = supabase.table("interactions").select("session_id, last_active").eq("session_id", session_id).order("last_active", desc=True).limit(1).execute()

    if result.data:
        session = result.data[0]
        last_active = datetime.fromisoformat(session["last_active"])

        # Check if session expired (15 minutes of inactivity)
        if datetime.now(datetime.timezone.utc) - last_active > timedelta(minutes=15):
            print("Session expired. Creating a new session.")
            session_id = str(uuid.uuid4())  # Generate a new session ID
            supabase.table("interactions").insert({
                "user_id": user_id,
                "session_id": session_id,
                "last_active": datetime.now(datetime.timezone.utc).isoformat()
            }).execute()
        else:
            # Update the last_active timestamp for the current session
            supabase.table("interactions").update({
                "last_active": datetime.now(datetime.timezone.utc).isoformat()
            }).eq("session_id", session_id).execute()
    else:
        # If no session exists, create a new session entry
        print("No session found. Creating a new session.")
        session_id = str(uuid.uuid4())
        supabase.table("interactions").insert({
            "user_id": user_id,
            "session_id": session_id,
            "last_active": datetime.now(datetime.timezone.utc).isoformat()
        }).execute()

    return session_id
