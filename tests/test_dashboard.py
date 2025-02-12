import pytest
from unittest.mock import MagicMock, patch
from app import create_app

@pytest.fixture
def mock_supabase():
    """Fixture to provide a mocked SupabaseLogger instance."""
    mock_logger = MagicMock()
    mock_logger.get_total_sessions.return_value = 50
    mock_logger.get_total_users.return_value = 10
    return mock_logger

@pytest.fixture
def app():
    """Provide the Flask app."""
    return create_app()

@pytest.fixture
def client(app, mock_supabase):
    """Fixture to provide a test client with patched SupabaseLogger."""
    with patch("app.routes.dashboard.logger", mock_supabase):
        yield app.test_client()

def test_dashboard_page(client):
    """Test if the dashboard page renders successfully."""
    response = client.get("/dashboard/")
    assert response.status_code == 200
    assert b"<title>Dashboard</title>" in response.data

def test_dashboard_data_success(client, mock_supabase):
    """Test successful retrieval of dashboard data."""
    response = client.get("/dashboard/api/dashboard-data")
    assert response.status_code == 200
    assert response.json == {"sessions": 50, "users": 10}

def test_dashboard_data_failure(client):
    """Test failure case when SupabaseLogger raises an exception."""
    with patch("app.routes.dashboard.logger.get_total_sessions", side_effect=Exception("Database error")):
        response = client.get("/dashboard/api/dashboard-data")
        assert response.status_code == 500
        assert response.json == {"error": "Failed to fetch dashboard data"}

def test_dashboard_data_no_sessions(client, mock_supabase):
    """Test when no sessions exist."""
    mock_supabase.get_total_sessions.return_value = 0
    response = client.get("/dashboard/api/dashboard-data")
    assert response.status_code == 200
    assert response.json == {"sessions": 0, "users": 10}

def test_dashboard_data_no_users(client, mock_supabase):
    """Test when no users exist."""
    mock_supabase.get_total_users.return_value = 0
    response = client.get("/dashboard/api/dashboard-data")
    assert response.status_code == 200
    assert response.json == {"sessions": 50, "users": 0}

def test_dashboard_data_large_numbers(client, mock_supabase):
    """Test handling of large numbers of sessions and users."""
    mock_supabase.get_total_sessions.return_value = 1_000_000
    mock_supabase.get_total_users.return_value = 500_000
    response = client.get("/dashboard/api/dashboard-data")
    assert response.status_code == 200
    assert response.json == {"sessions": 1_000_000, "users": 500_000}