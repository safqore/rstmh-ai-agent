import os
import uuid
from supabase import create_client, Client
from datetime import datetime
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

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


def get_or_create_session(user_id, session_id=None):
    """
    Retrieve or create a session in the `sessions` table.

    Args:
        user_id (str): Unique user identifier.
        session_id (str, optional): Current session ID provided by the client.

    Returns:
        str: Valid session ID.
    """
    from datetime import datetime, timezone, timedelta
    import uuid

    current_time = datetime.now(timezone.utc)

    if session_id:
        # Check if the session exists
        result = supabase.table("sessions").select("*").eq("session_id", session_id).execute()

        if result.data:
            # If session exists, check if it's still active
            session = result.data[0]
            last_active = datetime.fromisoformat(session["last_active"])

            # If inactive for 15 minutes, create a new session
            if current_time - last_active > timedelta(minutes=15):
                session_id = str(uuid.uuid4())
                supabase.table("sessions").insert({
                    "session_id": session_id,
                    "user_id": user_id,
                    "last_active": current_time.isoformat(),
                    "created_at": current_time.isoformat()
                }).execute()
            else:
                # Update the `last_active` timestamp
                supabase.table("sessions").update({
                    "last_active": current_time.isoformat()
                }).eq("session_id", session_id).execute()
        else:
            # If no session exists, create a new one
            session_id = str(uuid.uuid4())
            supabase.table("sessions").insert({
                "session_id": session_id,
                "user_id": user_id,
                "last_active": current_time.isoformat(),
                "created_at": current_time.isoformat()
            }).execute()
    else:
        # Create a new session if no session_id is provided
        session_id = str(uuid.uuid4())
        supabase.table("sessions").insert({
            "session_id": session_id,
            "user_id": user_id,
            "last_active": current_time.isoformat(),
            "created_at": current_time.isoformat()
        }).execute()

    return session_id
