import pytest
from httpx import AsyncClient, ASGITransport

from main import app
from src import di
from tests.mocks import mock_file_repo, mock_alert_repo, mock_files_adapter


def get_mock_alert_repo():
    return mock_alert_repo


def get_mock_file_repo():
    return mock_file_repo


def get_mock_file_adapter():
    return mock_files_adapter


app.dependency_overrides[di.get_alert_repository] = get_mock_alert_repo
app.dependency_overrides[di.get_file_repository] = get_mock_file_repo
app.dependency_overrides[di.get_file_adapter] = get_mock_file_adapter


@pytest.fixture(scope="session")
async def client():
    async with AsyncClient(
        transport=ASGITransport(app),
        base_url="http://test"
    ) as client:
        yield client

