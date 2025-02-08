from app.services.supabase_logging import SupabaseLogger
from datetime import datetime, timedelta
from unittest.mock import MagicMock, ANY
from unittest.mock import MagicMock
import pytest

def test_reuse_active_session(mock_supabase):
    # Mock SupabaseLogger instance
    logger = SupabaseLogger(supabase_client=mock_supabase)

    # Mock active session data
    active_time = (datetime.now() - timedelta(minutes=10)).isoformat()
    mock_response = MagicMock()
    mock_response.data = [{"session_id": "active-session", "last_active": active_time, "created_at": active_time}]
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response

    # Mock update response
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = {
        "status": "success"
    }

    # Call the method
    session_id = logger.get_or_create_session(user_id="user-123", session_id="active-session")

    # Ensure the session ID matches the active session
    assert session_id == "active-session"

    # Verify the update method was called
    mock_supabase.table.return_value.update.assert_called_once_with({
        "last_active": ANY  # Match any valid timestamp
    })
    print("[DEBUG] Test passed: Existing session reused.")


def test_create_new_session_when_inactive(mock_supabase):
    # Mock SupabaseLogger instance
    logger = SupabaseLogger(supabase_client=mock_supabase)

    # Mock inactive session data (last active > 6 hours ago)
    inactive_time = (datetime.now() - timedelta(hours=6, minutes=1)).isoformat()
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = {
        "data": [{"session_id": "inactive-session", "last_active": inactive_time}]
    }

    # Call the method
    session_id = logger.get_or_create_session("user-123")

    # Ensure a new session is created
    assert session_id != "inactive-session"  # A new session should be created
    print("[DEBUG] Test passed: New session created for inactive user.")

def test_create_new_session_when_no_session_exists(mock_supabase):
    # Mock SupabaseLogger instance
    logger = SupabaseLogger(supabase_client=mock_supabase)

    # Mock no session data
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = {"data": []}

    # Call the method
    session_id = logger.get_or_create_session("user-123")

    # Ensure a new session is created
    assert session_id is not None
    assert isinstance(session_id, str)

    # Verify the insert method is called with the correct data
    mock_supabase.table.return_value.insert.assert_called_once_with({
        "session_id": ANY,  # Dynamically generated
        "user_id": "user-123",
        "last_active": ANY,  # Valid timestamp
        "created_at": ANY,   # Valid timestamp
    })
    print("[DEBUG] Test passed: New session created with correct data.")


def test_log_interaction(mock_supabase):
    # Mock SupabaseLogger instance
    logger = SupabaseLogger(supabase_client=mock_supabase)

    logger.log_interaction(
        user_id="user-123",
        session_id="session-456",
        prompt="Hello?",
        response="Hi!",
        source_pdf="faq",
        metadata={"ip": "127.0.0.1"}
    )

    # Ensure the insert method is called on the mock
    mock_supabase.table.return_value.insert.assert_called_once_with({
        "user_id": "user-123",
        "session_id": "session-456",
        "timestamp": ANY,  # Match any timestamp
        "prompt": "Hello?",
        "response": "Hi!",
        "source_pdf": "faq",
        "section_reference": None,  # Include the default field
        "metadata": {"ip": "127.0.0.1"},
        "is_compliant": True  # Include the default field
        })
    print("[DEBUG] Test passed: Interaction logged successfully.")

    mock_supabase.table.return_value.insert.assert_called_once()


def test_log_interaction_foreign_key_error(mock_supabase):
    # Mock SupabaseLogger instance
    logger = SupabaseLogger(supabase_client=mock_supabase)

    # Simulate foreign key constraint violation
    mock_supabase.table.return_value.insert.side_effect = Exception(
        "insert or update on table 'interactions' violates foreign key constraint 'fk_session'"
    )

    # Attempt to log interaction with a non-existent session_id
    with pytest.raises(Exception, match="violates foreign key constraint"):
        logger.log_interaction(
            user_id="user-123",
            session_id="invalid-session",
            prompt="Hello?",
            response="Hi!",
            source_pdf="faq",
            metadata={"ip": "127.0.0.1"}
        )

    print("[DEBUG] Test passed: Foreign key constraint violation properly handled.")

def test_log_interaction_invalid_input(mock_supabase):
    logger = SupabaseLogger(supabase_client=mock_supabase)

    # Test with invalid user_id
    with pytest.raises(ValueError, match="Invalid user_id provided"):
        logger.log_interaction(
            user_id="",  # Invalid user_id
            session_id="valid-session",
            prompt="Hello?",
            response="Hi!"
        )

    # Test with invalid session_id
    with pytest.raises(ValueError, match="Invalid session_id provided"):
        logger.log_interaction(
            user_id="valid-user",
            session_id="",  # Invalid session_id
            prompt="Hello?",
            response="Hi!"
        )
    print("[DEBUG] Test passed: Invalid input handled successfully.")