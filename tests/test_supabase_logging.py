from app.services.supabase_logging import SupabaseLogger
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, ANY

def test_get_or_create_session(mock_supabase):
    # Mock SupabaseLogger instance
    logger = SupabaseLogger(supabase_client=mock_supabase)

    # Case 1: Active session within the last 15 minutes
    active_time = (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = {
        "data": [{"session_id": "active-session", "last_active": active_time}]
    }

    session_id = logger.get_or_create_session("user-123")
    assert session_id == "active-session"

    # Case 2: Inactive session (over 15 minutes)
    inactive_time = (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat()
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = {
        "data": [{"session_id": "inactive-session", "last_active": inactive_time}]
    }

    session_id = logger.get_or_create_session("user-123")
    assert session_id != "inactive-session"  # A new session should be created

    # Case 3: No session exists
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = {"data": []}
    session_id = logger.get_or_create_session("user-123")
    assert session_id is not None

    # Verify insert method was called for the new session
    mock_supabase.table.return_value.insert.assert_called()

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
        "metadata": {"ip": "127.0.0.1"}
    })

    mock_supabase.table.return_value.insert.assert_called_once()