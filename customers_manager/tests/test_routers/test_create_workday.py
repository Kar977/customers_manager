import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_create_workday(mock_empty_db_session):
    response = client.post(
        "/customers/workday/", json={"date": "12.01.2025", "day_status": "open"}
    )

    assert response.status_code == 201
    assert response.json() == {
        "action": "workday_created",
        "workday_id": "None",
        "date": "2025-01-12",
    }

    mock_empty_db_session.add.assert_called()
    mock_empty_db_session.commit.assert_called()
    mock_empty_db_session.refresh.assert_called()


@pytest.mark.asyncio
async def test_create_workday_already_exists(mock_db_session_with_existing_workday):
    response = client.post(
        "/customers/workday/", json={"date": "30.03.2024", "day_status": "open"}
    )

    assert response.status_code == 409
    assert "workday" in response.text
    assert "already exist" in response.text

    mock_db_session_with_existing_workday.add.assert_not_called()
    mock_db_session_with_existing_workday.commit.assert_not_called()
    mock_db_session_with_existing_workday.refresh.assert_not_called()


@pytest.mark.asyncio
async def test_create_workday_invalid_date_format():
    with pytest.raises(ValueError) as excinfo:
        response = client.post(
            "/customers/workday/", json={"date": "12-01-2025", "day_status": "open"}
        )
        response.status_code

    assert str(excinfo.typename) == "ValueError"
    assert (
        str(excinfo.value) == "time data '12-01-2025' does not match format '%d.%m.%Y'"
    )


@pytest.mark.asyncio
async def test_create_workday_missing_date():
    response = client.post("/customers/workday/", json={"day_status": "open"})

    assert response.status_code == 422
