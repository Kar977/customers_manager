import pytest
from fastapi.testclient import TestClient
from customers_manager.main import app
#from customers_manager.database_structure.database import get_db
#import httpx
#from unittest.mock import patch, AsyncMock
#from unittest import mock
#from customers_manager.customers.conftest import mock_db_session

client = TestClient(app)


"""def test_read_root():
    response = client.get("/customers/")
    assert response.status_code == 200"""

@pytest.mark.asyncio
async def test_create_workday_v2(mock_empty_db_session):
    response = client.post("/customers/workday/", json={"date": "12.01.2025", "day_status": "open"})
    assert response.status_code == 201

    mock_empty_db_session.add.assert_called()
    mock_empty_db_session.commit.assert_called()


#@pytest.mark.parametrize("mock_db_session", [pytest.param(False, id="empty_db")], indirect=True)
@pytest.mark.asyncio
async def test_create_workday(mock_empty_db_session):
    response = client.post("/customers/workday/", json={"date": "12.01.2025", "day_status": "open"})
    assert response.status_code == 201

    mock_empty_db_session.add.assert_called()
    mock_empty_db_session.commit.assert_called()


#@patch("customers_manager.customers.rabbitmq.rabbitmq.connect")
@pytest.mark.asyncio
async def test_delete_workday(mock_db_session_with_existing_workday):
    response = client.request("DELETE", "/customers/workday/", json={"workday_id": 1})

    assert response.status_code == 202
    assert response.json() == {"action": "workday_deleted", "workday_id": "1"}

