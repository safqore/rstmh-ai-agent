import pytest
from app import create_app
from app.services.supabase_logging import SupabaseLogger
from unittest.mock import MagicMock

@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_supabase(mocker):
    # Mock the Supabase client
    mock_client = MagicMock()
    mocker.patch("app.services.supabase_logging.SupabaseLogger", return_value=SupabaseLogger(mock_client))
    return mock_client

@pytest.fixture
def mock_qdrant(mocker):
    # Mock the Qdrant client
    mock_client = MagicMock()
    mocker.patch("app.services.qdrant_service.client", mock_client)
    return mock_client