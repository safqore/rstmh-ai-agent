import os
import uuid
from datetime import datetime, timezone, timedelta
from supabase import create_client, Client
from dotenv import load_dotenv

# Load the environment variables
current_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the .env file
env_path = os.path.join(current_dir, '../..', '.env')
# Load the environment variables
load_dotenv(dotenv_path=env_path)

# print(f"[DEBUG]: {os.getenv('SUPABASE_URL')} and {os.getenv('SUPABASE_KEY')}")


class SupabaseLogger:
    def __init__(self, supabase_client=None):
        """
        Initialize the Supabase logger. Allows for dependency injection of a mocked client.
        """
        if supabase_client:
            self.supabase = supabase_client
        else:
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY")
            if not url or not key:
                raise ValueError("Supabase URL and API key must be set in environment variables.")
            self.supabase: Client = create_client(url, key)

    def log_interaction(self, user_id, session_id, prompt, response, source_pdf=None, section_reference=None, metadata=None):
        """
        Logs chatbot interaction to the Supabase database.
        """
        if not user_id or not isinstance(user_id, str) or user_id.strip() == "":
            raise ValueError("Invalid user_id provided")
        if not session_id or not isinstance(session_id, str) or session_id.strip() == "":
            raise ValueError("Invalid session_id provided")

        # Ensure session_id exists
        session_check = self.supabase.table("sessions").select("*").eq("session_id", session_id).execute()
        if not session_check.data:
            raise ValueError(f"Session ID {session_id} does not exist in the sessions table.")
    
        data = {
            "user_id": user_id,
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "prompt": prompt,
            "response": response,
            "source_pdf": source_pdf,
            "section_reference": section_reference,
            "metadata": metadata,
            "is_compliant": True  # Default value for compliance flag
        }

        try:
            result = self.supabase.table("interactions").insert(data).execute()
            print("[DEBUG] Logged interaction successfully:", result.data)
        except Exception as e:
            print(f"[ERROR] Error logging interaction to Supabase: {e}")
            raise # Re-raise the exception

    def get_or_create_session(self, user_id, session_id=None):
        """
        Retrieve or create a session in the `sessions` table.
        """
        current_time = datetime.now(timezone.utc)
        print("[DEBUG] Current time:", current_time)

        if session_id:
            # Check if the session exists
            result = self.supabase.table("sessions").select("*").eq("session_id", session_id).execute()
            print("[DEBUG] Retrieved session data:", result.data)

            if result.data:
                session = result.data[0]
                try:
                    last_active = datetime.fromisoformat(session["last_active"])
                    print("[DEBUG] Last active timestamp:", last_active)

                    # If inactive for 15 minutes, create a new session
                    if current_time.replace(tzinfo=None) - last_active > timedelta(minutes=15):
                        print("[DEBUG] Session inactive for more than 15 minutes. Creating new session.")
                        session_id = str(uuid.uuid4())
                        self._create_session(session_id, user_id, current_time)
                    else:
                        # Update the `last_active` timestamp
                        print("[DEBUG] Updating last_active for existing session.")
                        self.supabase.table("sessions").update({
                            "last_active": current_time.isoformat()
                        }).eq("session_id", session_id).execute()
                        print("[DEBUG] Updated last_active for session:", session_id)
                except Exception as e:
                    print(f"[ERROR] Error parsing last_active or updating session: {e}")
                    raise
            else:
                # If no session exists, create a new one
                print("[DEBUG] No session found for provided session_id. Creating new session.")
                session_id = str(uuid.uuid4())
                self._create_session(session_id, user_id, current_time)
        else:
            # Create a new session if no session_id is provided
            print("[DEBUG] No session_id provided. Creating new session.")
            session_id = str(uuid.uuid4())
            self._create_session(session_id, user_id, current_time)

        print(f"[DEBUG]: Returning session_id={session_id} for user_id={user_id}")
        return session_id

    def _create_session(self, session_id, user_id, current_time):
        """
        Helper method to create a new session in the `sessions` table.
        """
        try:
            self.supabase.table("sessions").insert({
                "session_id": session_id,
                "user_id": user_id,
                "last_active": current_time.isoformat(),
                "created_at": current_time.isoformat()
            }).execute()


            print("[DEBUG] Created new session in Supabase.")
        except Exception as e:
            print(f"[ERROR] Error creating session in Supabase: {e}")
            raise