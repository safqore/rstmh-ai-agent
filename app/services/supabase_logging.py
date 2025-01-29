import os
import uuid
import logging
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
        self.logger = logging.getLogger(__name__)
        if supabase_client:
            self.client = supabase_client
        else:
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY")
            if not url or not key:
                raise ValueError("Supabase URL and API key must be set in environment variables.")
            self.client: Client = create_client(url, key)

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
                    if current_time - last_active > timedelta(minutes=15):
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

    def get_total_sessions(self):
        """
        Fetch the total number of sessions from the Supabase database.
        """
        try:
            print("[DEBUG] Fetching total sessions...")
            # Call the 'count_sessions' Postgres function
            result = self.client.rpc("count_sessions").execute()
            if result.data:
                return result.data[0]["count"]
            return 0
        except Exception as e:
            print("[ERROR] Failed to fetch sessions:", e)
            raise

    def get_total_users(self):
        """
        Fetch the total number of distinct users from the Supabase database.
        """
        try:
            print("[DEBUG] Fetching total users...")
            # Call the 'count_distinct_users' Postgres function
            result = self.client.rpc("count_distinct_users").execute()
            if result.data:
                return result.data[0]["count"]
            return 0
        except Exception as e:
            print("[ERROR] Failed to fetch users:", e)
            raise

    def get_session_details(self, session_id, limit=10, offset=0, start_date=None, end_date=None, user_id=None, search_query=None):
        """
        Fetch session details from the database.

        :param session_id: ID of the session to fetch details for
        :param limit: Number of records to fetch (default: 10)
        :param offset: Offset for pagination (default: 0)
        :param start_date: Filter interactions after this date
        :param end_date: Filter interactions before this date
        :param user_id: Filter interactions by user ID
        :param search_query: Search interactions by prompt content
        :return: A tuple (details, total_count)
        """
        try:
            query = self.client.table("interactions").select("*").eq("session_id", session_id)

            # Apply optional filters
            if start_date:
                query = query.gte("timestamp", start_date)
            if end_date:
                query = query.lte("timestamp", end_date)
            if user_id:
                query = query.eq("user_id", user_id)
            if search_query:
                query = query.ilike("prompt", f"%{search_query}%")

            # Add pagination
            query = query.range(offset, offset + limit - 1)

            response = query.execute()

            # Debug: Print the response object
            print(f"[DEBUG] Supabase response: {response}")
            print(f"[DEBUG] Supabase response.data: {response.data}")

            # Check if the response contains data
            if not response.data:
                raise Exception("Supabase query returned no data.")

            details = response.data
            total_count = len(details)  # Replace with total count logic if available
            return details, total_count
        except Exception as e:
            print(f"[ERROR] Failed to fetch session details: {str(e)}")
            raise Exception(f"Failed to fetch session details: {str(e)}")

    def get_filtered_session_details(self, session_id, start_date=None, end_date=None, user_id=None, search_query="", limit=10, offset=0):
        query = self.client.table("interactions").select("*").eq("session_id", session_id)

        if start_date:
            query = query.gte("timestamp", start_date)
        if end_date:
            query = query.lte("timestamp", end_date)
        if user_id:
            query = query.eq("user_id", user_id)
        if search_query:
            query = query.ilike("prompt", f"%{search_query}%")

        query = query.range(offset, offset + limit - 1)
        return query.execute().data

    def get_filtered_session_count(self, session_id, start_date=None, end_date=None, user_id=None, search_query=""):
        query = self.client.table("interactions").select("id", count="exact").eq("session_id", session_id)

        if start_date:
            query = query.gte("timestamp", start_date)
        if end_date:
            query = query.lte("timestamp", end_date)
        if user_id:
            query = query.eq("user_id", user_id)
        if search_query:
            query = query.ilike("prompt", f"%{search_query}%")

        return query.execute().count
    
    def get_sessions(self, limit=10, offset=0, search_query=""):
        """
        Fetch session summaries with a count of questions.

        :param limit: Number of records to fetch
        :param offset: Offset for pagination
        :param search_query: Filter sessions by search query
        :return: A list of session summaries
        """
        try:
            response = self.client.rpc("get_session_summary", {
                "limit_param": limit,
                "offset_param": offset,
                "search_query": search_query
            }).execute()

            if response.error:
                raise Exception(f"Supabase RPC call failed: {response.error}")

            return response.data
        except Exception as e:
            raise Exception(f"Failed to fetch sessions: {str(e)}")

    def get_sessions_with_filters(self, search_query="", limit=10, offset=0):
        """
        Fetch sessions with optional filters and pagination.

        :param search_query: Search term to filter by question content
        :param limit: Number of sessions to fetch (default: 10)
        :param offset: Offset for pagination (default: 0)
        :return: A tuple (sessions, total_count)
        """
        try:
            query = (
                self.client.table("interactions")
                .select("session_id, count(id) as question_count")
                .group_by("session_id")
            )

            # Apply search filter
            if search_query:
                query = query.ilike("prompt", f"%{search_query}%")

            # Add pagination
            query = query.range(offset, offset + limit - 1)

            response = query.execute()

            if response.error:
                raise Exception(f"Supabase query failed: {response.error}")

            sessions = response.data
            total_count = len(sessions)  # Replace with actual count if available
            return sessions, total_count
        except Exception as e:
            raise Exception(f"Failed to fetch sessions: {str(e)}")     