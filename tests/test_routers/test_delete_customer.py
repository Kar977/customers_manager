from customers_manager.main import app
from fastapi.testclient import TestClient
import pytest
from customers_manager.customers.rabbitmq import RabbitMQConnection

client = TestClient(app)


@pytest.mark.asyncio
async def test_delete_existing_customer(mock_db_session_with_existing_customer, monkeypatch):

    async def mock_send_email(*args, **kwargs):
        return None
    monkeypatch.setattr(RabbitMQConnection, "send_email_task", mock_send_email)

    response = client.request("DELETE", "customers/customer/", json={"user_id":1})

    assert response.status_code == 200
    assert "customer deleted" in response.text
