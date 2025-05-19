import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_create_workday_v2(mock_empty_db_session):
    response = client.post(
        "/customers/workday/", json={"date": "12.01.2025", "day_status": "open"}
    )
    assert response.status_code == 201

    mock_empty_db_session.add.assert_called()
    mock_empty_db_session.commit.assert_called()


@pytest.mark.asyncio
async def test_create_workday(mock_empty_db_session):
    response = client.post(
        "/customers/workday/", json={"date": "12.01.2025", "day_status": "open"}
    )
    assert response.status_code == 201

    mock_empty_db_session.add.assert_called()
    mock_empty_db_session.commit.assert_called()


@pytest.mark.asyncio
async def test_delete_workday(mock_db_session_with_existing_workday):
    response = client.request("DELETE", "/customers/workday/", json={"workday_id": 1})

    assert response.status_code == 202
    assert response.json() == {"action": "workday_deleted", "workday_id": "1"}
