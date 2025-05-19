from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from customers.services.crud import WorkdayManager
from main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_list_available_slots(mock_db_session_with_available_slots):

    response = client.get("/customers/slots/available/")

    assert response.status_code == 200
    assert response.json() == {"2025-01-01": ["08:00", "08:30", "09:00"]}

    mock_db_session_with_available_slots.execute.assert_called()


@pytest.mark.asyncio
async def test_list_available_slots_with_empty_data(mock_db_session_with_empty_list):
    response = client.get("/customers/slots/available/")

    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.asyncio
async def test_list_available_slots_on_specific_day(
    mock_db_session_with_available_slot_on_specific_day, monkeypatch
):
    mock_workday = MagicMock()
    mock_workday.id = 1

    async def mock_get_workday(*args, **kwargs):
        return mock_workday

    monkeypatch.setattr(
        WorkdayManager,
        "get_workday_if_exsist_and_open_or_fail",
        mock_get_workday,
    )

    response = client.get("/customers/slots/available/01.01.2025")

    assert response.status_code == 200
