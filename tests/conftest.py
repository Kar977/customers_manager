from datetime import date
from unittest.mock import AsyncMock, MagicMock
import pytest
from customers_manager.database_structure.database import get_db
from customers_manager.main import app
from customers_manager.database_structure.models import (
    WorkDay,
    Slot,
    SlotToHour,
    Customer,
)


mock_session = AsyncMock()


@pytest.fixture(scope="function", autouse=True)
def mocked_app():
    async def override_get_db():
        try:
            yield mock_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db


def mocked_workday_obj(
    id: int = 1,
    work_date: date = date(2025, 1, 1),
    dat_status: str = "open",
    slots: list[int] = (1, 2, 3),
):
    mock_workday = MagicMock(spec=WorkDay)
    mock_workday.id = id
    mock_workday.date = work_date
    mock_workday.day_status = dat_status
    mock_workday.slots = slots

    return mock_workday


def mocked_slot_obj(id: int = 1, slot_nbr: int = 1):
    mocked_slot = MagicMock(spec=Slot)
    mocked_slot.id = id
    mocked_slot.slot_nbr = slot_nbr
    mocked_slot.slot_status = "available"
    mocked_slot.customer_id = 1
    mocked_slot.workday_id = 1

    return mocked_slot


def mocked_slot_to_hour_obj(id: int = 1, slot_nbr: int = 1, hour: str = "08:00"):
    mock_slot_to_hour = MagicMock(spec=SlotToHour)
    mock_slot_to_hour.id = id
    mock_slot_to_hour.slot_nbr = slot_nbr
    mock_slot_to_hour.hour = hour

    return mock_slot_to_hour


@pytest.fixture
def mock_empty_db_session():
    mock_workday = None

    mock_result = AsyncMock()
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = mock_workday
    mock_result.scalars.return_value = mock_scalars

    mock_session.execute = AsyncMock(return_value=mock_result)

    mock_session.add = AsyncMock()
    mock_session.delete = AsyncMock()
    mock_session.commit = AsyncMock()

    yield mock_session
    mock_session.reset_mock()


@pytest.fixture
def mock_db_session_with_existing_workday():
    mock_result = AsyncMock()
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = mocked_workday_obj()
    mock_result.scalars.return_value = mock_scalars

    mock_session.execute = AsyncMock(return_value=mock_result)

    mock_session.add = AsyncMock()
    mock_session.delete = AsyncMock()
    mock_session.commit = AsyncMock()

    yield mock_session
    mock_session.reset_mock()


@pytest.fixture
def mock_db_session_with_available_slots():

    mock_result = MagicMock()
    mock_result.all.return_value = [
        (
            mocked_workday_obj(),
            mocked_slot_obj(id=1, slot_nbr=1),
            mocked_slot_to_hour_obj(id=1, slot_nbr=1, hour="08:00"),
        ),
        (
            mocked_workday_obj(),
            mocked_slot_obj(id=2, slot_nbr=2),
            mocked_slot_to_hour_obj(id=2, slot_nbr=2, hour="08:30"),
        ),
        (
            mocked_workday_obj(),
            mocked_slot_obj(id=3, slot_nbr=3),
            mocked_slot_to_hour_obj(id=3, slot_nbr=3, hour="09:00"),
        ),
    ]

    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()
    mock_session.delete = AsyncMock()
    mock_session.add = AsyncMock()

    yield mock_session
    mock_session.reset_mock()


@pytest.fixture
def mock_db_session_with_empty_list():
    mock_result = MagicMock()

    mock_result.all.return_value = []

    mock_session.execute = AsyncMock(return_value=mock_result)

    yield mock_session
    mock_session.reset_mock()


@pytest.fixture
def mock_db_session_with_available_slot_on_specific_day():
    first_result = MagicMock()
    first_scalars = MagicMock()
    first_scalars.all.return_value = [mocked_slot_obj()]
    first_result.scalars.return_value = first_scalars

    second_result = MagicMock()
    second_scalars = MagicMock()
    second_scalars.first.return_value = mocked_slot_to_hour_obj()
    second_result.scalars.return_value = second_scalars

    mock_session.execute = AsyncMock(side_effect=[first_result, second_result])

    mock_session.add = AsyncMock()
    mock_session.delete = AsyncMock()
    mock_session.commit = AsyncMock()

    yield mock_session
    mock_session.reset_mock()


@pytest.fixture
def mock_db_session_with_no_customer():
    first_scalars = MagicMock()
    first_scalars.first.return_value = None
    first_scalars.scalars.return_value = None

    first_result = MagicMock()
    first_result.scalars.return_value = first_scalars

    second_result = MagicMock()
    second_scalars = MagicMock()
    second_scalars.first.return_value = mocked_slot_obj()
    second_result.scalars.return_value = second_result

    mock_session.execute = AsyncMock(side_effect=[first_result, second_result])
    mock_session.add = AsyncMock
    mock_session.delete = AsyncMock()
    mock_session.commit = AsyncMock()

    yield mock_session
    mock_session.reset_mock()


@pytest.fixture
def mock_db_session_with_existing_customer():
    mock_slot = Slot(
        id=1, slot_nbr=1, slot_status="unavailable", customer_id=1, workday_id=1
    )
    mock_customer = Customer(
        id=1, name="Marco", phone_number=123123123, slots=[mock_slot]
    )

    first_result = MagicMock()
    first_scalars = MagicMock()
    first_scalars.first.return_value = mock_customer
    first_result.scalars.return_value = first_scalars

    second_result = MagicMock()
    second_scalars = MagicMock()
    second_scalars.all.return_value = [mock_slot]
    second_result.scalars.return_value = second_scalars

    mock_session.execute = AsyncMock(side_effect=[first_result, second_result])

    yield mock_session
    mock_session.reset_mock()
