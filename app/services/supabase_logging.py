import os
import uuid
from datetime import datetime, timezone, timedelta
from supabase import create_client, Client
from dotenv import load_dotenv

os.environ.clear()
# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the .env file
env_path = os.path.join(current_dir, '../..', '.env')
# Load the environment variables
load_dotenv(dotenv_path=env_path)

print(f"[DEBUG]: {os.getenv("SUPABASE_URL")} and {os.getenv("SUPABASE_KEY")}")

class SupabaseLogger:
    # def __init__(self):
    #     # Initialize Supabase client
    #     self.url = os.getenv("SUPABASE_URL")
    #     self.key = os.getenv("SUPABASE_KEY")

    #     if not self.url or not self.key:
    #         raise ValueError("Supabase URL and API key must be set in environment variables.")

    #     self.client: Client = create_client(self.url, self.key)

    def __init__(self, supabase_client=None):
        if supabase_client:
            self.supabase = supabase_client
        else:
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY")
            self.supabase = create_client(url, key)
    

    def log_interaction(self, user_id, session_id, prompt, response, source_pdf=None, section_reference=None, metadata=None):
        """
        Logs chatbot interaction to the Supabase database.
        """
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
            result = self.client.table("interactions").insert(data).execute()
            print("Logged interaction successfully:", result.data)
        except Exception as e:
            print(f"Error logging interaction to Supabase: {e}")

    def get_or_create_session(self, user_id, session_id=None):
        """
        Retrieve or create a session in the `sessions` table.
        """
        current_time = datetime.now(timezone.utc)

        if session_id:
            # Check if the session exists
            result = self.client.table("sessions").select("*").eq("session_id", session_id).execute()

            if result.data:
                session = result.data[0]
                last_active = datetime.fromisoformat(session["last_active"])

                # If inactive for 15 minutes, create a new session
                if current_time - last_active > timedelta(minutes=15):
                    session_id = str(uuid.uuid4())
                    self._create_session(session_id, user_id, current_time)
                else:
                    # Update the `last_active` timestamp
                    self.client.table("sessions").update({
                        "last_active": current_time.isoformat()
                    }).eq("session_id", session_id).execute()
            else:
                # If no session exists, create a new one
                session_id = str(uuid.uuid4())
                self._create_session(session_id, user_id, current_time)
        else:
            # Create a new session if no session_id is provided
            session_id = str(uuid.uuid4())
            self._create_session(session_id, user_id, current_time)

        print(f"[DEBUG]: Creating or retrieving session for user_id={user_id}, session_id={session_id}")
        return session_id

    def _create_session(self, session_id, user_id, current_time):
        """
        Helper method to create a new session in the `sessions` table.
        """
        self.supabase.table("sessions").insert({
            "session_id": session_id,
            "user_id": user_id,
            "last_active": current_time.isoformat(),
            "created_at": current_time.isoformat()
        }).execute()