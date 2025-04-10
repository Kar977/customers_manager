import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from customers_manager.customers.services.crud import WorkdayManager
from customers_manager.customers.rabbitmq import RabbitMQConnection

from customers_manager.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_create_visit(mock_db_session_with_no_customer, monkeypatch):

    mock_workday = MagicMock()
    mock_workday.id = 1

    mock_slot = MagicMock
    mock_slot.slot_status = "available"
    mock_slot.id = 1

    async def mock_get_workday(*args, **kwargs):
        return mock_workday

    monkeypatch.setattr(
        WorkdayManager,
        "get_workday_if_exsist_and_open_or_fail",
        mock_get_workday,
    )

    async def mock_get_slot(*args, **kwargs):
        return mock_slot

    monkeypatch.setattr(
        WorkdayManager,
        "get_slot_if_available_or_fail",
        mock_get_slot)

    async def mock_send_email(*args, **kwargs):
        return None
    monkeypatch.setattr(RabbitMQConnection, "send_email_task", mock_send_email)

    response = client.request("POST", "customers/visit/", json={
        "name": "Adam",
        "phone_nbr": "123123123",
        "date": "01.01.2025",
        "slot": 1
    }
                              )

    assert response.status_code == 200
    assert 'action' and 'visitation reserved' in response.text
