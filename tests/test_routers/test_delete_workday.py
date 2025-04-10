import pytest
from fastapi.testclient import TestClient

from customers_manager.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_delete_workday(mock_db_session_with_existing_workday):
    response = client.request("DELETE", "/customers/workday/", json={"workday_id": 1})

    assert response.status_code == 202
    assert response.json() == {"action": "workday_deleted", "workday_id": "1"}

    mock_db_session_with_existing_workday.delete.assert_called()
    mock_db_session_with_existing_workday.commit.assert_called()

@pytest.mark.asyncio()
async def test_delete_workday_doesnt_exist(mock_empty_db_session):
    response = client.request("DELETE", "/customers/workday/", json={"workday_id": 1})

    assert response.status_code == 404

    mock_empty_db_session.delete.assert_not_called()
    mock_empty_db_session.commit.assert_not_called()

