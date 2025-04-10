from datetime import date
from unittest.mock import AsyncMock, MagicMock
import pytest
from customers_manager.database_structure.database import get_db
from customers_manager.main import app
from customers_manager.database_structure.models import WorkDay, Slot, SlotToHour, Customer


mock_session = AsyncMock()

@pytest.fixture(scope="function", autouse=True)
def mocked_app():
    async def override_get_db():
        try:
            yield mock_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db


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
    mock_workday = MagicMock()
    mock_workday.id = 1
    mock_workday.date = date(2024, 3, 30)
    mock_workday.day_status = "open"
    mock_workday.slots = []

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
def mock_db_session_with_available_slots():
    # Mock WorkDay object
    mock_workday1 = MagicMock(spec=WorkDay)
    mock_workday1.id = 1
    mock_workday1.date = date(2025, 1, 1)
    mock_workday1.day_status = "open"
    mock_workday1.slots = [1, 2, 3]

    # Mock Slot objects
    mock_slot1 = MagicMock(spec=Slot)
    mock_slot1.id = 1
    mock_slot1.slot_nbr = 1
    mock_slot1.slot_status = 'available'
    mock_slot1.customer_id = 1
    mock_slot1.workday_id = 1

    mock_slot2 = MagicMock(spec=Slot)
    mock_slot2.id = 2
    mock_slot2.slot_nbr = 2
    mock_slot2.slot_status = 'available'
    mock_slot2.customer_id = 2
    mock_slot2.workday_id = 1

    mock_slot3 = MagicMock(spec=Slot)
    mock_slot3.id = 3
    mock_slot3.slot_nbr = 3
    mock_slot3.slot_status = 'available'
    mock_slot3.customer_id = 3
    mock_slot3.workday_id = 1

    # Mock SlotToHour objects
    mock_slottohour1 = MagicMock(spec=SlotToHour)
    mock_slottohour1.id = 1
    mock_slottohour1.slot_nbr = 1
    mock_slottohour1.hour = "08:00"

    mock_slottohour2 = MagicMock(spec=SlotToHour)
    mock_slottohour2.id = 2
    mock_slottohour2.slot_nbr = 2
    mock_slottohour2.hour = "08:30"

    mock_slottohour3 = MagicMock(spec=SlotToHour)
    mock_slottohour3.id = 3
    mock_slottohour3.slot_nbr = 3
    mock_slottohour3.hour = "09:00"

    # Mocking .all() return value as a list of tuples
    mock_result = MagicMock()
    mock_result.all.return_value = [
        (mock_workday1, mock_slot1, mock_slottohour1),
        (mock_workday1, mock_slot2, mock_slottohour2),
        (mock_workday1, mock_slot3, mock_slottohour3),
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
    mock_slot1 = Slot(
        id=1,
        slot_nbr=1,
        slot_status="available",
        customer_id=1,
        workday_id=1
    )
    mock_slot_to_hour = SlotToHour(
        id=1,
        slot_nbr=1,
        hour="08:00"
    )

    first_result = MagicMock()
    first_scalars = MagicMock()
    first_scalars.all.return_value = [mock_slot1]
    first_result.scalars.return_value = first_scalars

    second_result = MagicMock()
    second_scalars = MagicMock()
    second_scalars.first.return_value = mock_slot_to_hour
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

    mock_slot_to_hour = SlotToHour(
        id=1,
        slot_nbr=1,
        hour="08:00"
    )

    second_result = MagicMock()
    second_scalars = MagicMock()
    second_scalars.first.return_value = mock_slot_to_hour
    second_result.scalars.return_value = second_result


    #mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.execute = AsyncMock(side_effect=[first_result, second_result])
    mock_session.add = AsyncMock
    mock_session.delete = AsyncMock()
    mock_session.commit = AsyncMock()

    yield mock_session
    mock_session.reset_mock()

@pytest.fixture
def mock_db_session_with_existing_customer():
    mock_slot = Slot(id=1, slot_nbr=1, slot_status="unavailable", customer_id=1, workday_id=1)
    mock_customer = Customer(id=1, name="Marco", phone_number=123123123, slots=[mock_slot])

    first_result = MagicMock()
    first_scalars = MagicMock()
    first_scalars.first.return_value = mock_customer
    first_result.scalars.return_value = first_scalars

    second_result = MagicMock()
    second_scalars = MagicMock()
    second_scalars.all.return_value = [mock_slot]
    second_result.scalars.return_value = second_scalars

    mock_session.execute = AsyncMock(side_effect=[first_result,second_result])

    yield mock_session
    mock_session.reset_mock()