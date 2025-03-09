from customers.services.exceptions import (
    ResourceDoesNotExistException,
    WrongStatusException,
    ResourceAlreadyExistException,
)
from database_structure.models import Customer, Slot, WorkDay, SlotToHour
from fastapi.responses import JSONResponse
from sqlalchemy.sql import exists

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from datetime import datetime


class VisitationManager:

    def __init__(self):
        self.customers_manager = CustomersManager()
        self.workday_manager = WorkdayManager()

    async def reserve_visitation(self, name, phone_nbr, date, slot, db: AsyncSession):
        date = datetime.strptime(date, "%d.%m.%Y").date()
        customer_obj = await self.customers_manager.get_or_create_customer(
            name, int(phone_nbr), db
        )
        return await self.workday_manager.create_reservation(
            date, slot, customer_obj, db
        )

    async def read_all_available_hours_on_specific_date(self, date, db: AsyncSession):
        workday_obj = await self.workday_manager.get_all_slot_nbr_if_available_or_fail(
            date, db
        )
        return await self.workday_manager.convert_slot_list_into_hours(workday_obj, db)

    async def get_all_available_slots(self, db: AsyncSession):

        available_slots_per_date_dict = {}

        stmt = select(WorkDay, Slot, SlotToHour).where(
            and_(
                Slot.slot_status == "available",
                WorkDay.id == Slot.workday_id,
                Slot.slot_nbr == SlotToHour.slot_nbr,
            )
        )

        result = await db.execute(stmt)
        available_slots = result.all()

        for obj in available_slots:
            date_str = str(obj[0].date)
            if date_str not in available_slots_per_date_dict:
                available_slots_per_date_dict[date_str] = [obj[2].hour]
            else:
                available_slots_per_date_dict[date_str].append(obj[2].hour)

        return available_slots_per_date_dict


class CustomersManager:

    def __init__(self):
        pass

    async def get_or_create_customer(self, name, phone_nbr, db: AsyncSession):
        stmt = select(Customer).where(
            and_(
                Customer.name == name,
                Customer.phone_number == phone_nbr,
            )
        )

        result = await db.execute(stmt)
        found_user = result.scalars().first()

        if found_user is None:
            customer = Customer(name=name, phone_number=phone_nbr)
            db.add(customer)
            await db.commit()
            await db.refresh(customer)
            return customer

        return found_user

    async def delete_customer_and_release_slots(self, id_nbr, db: AsyncSession):
        stmt = select(Customer).where(Customer.id == id_nbr)

        result = await db.execute(stmt)
        customer = result.scalars().first()

        if customer is None:
            raise ResourceDoesNotExistException(
                resource_name="customer", unit="ID", identification_mark=str(id_nbr)
            )

        second_stmt = select(Slot).where(Slot.customer_id == customer.id)

        second_result = await db.execute(second_stmt)
        slots_with_the_customer_reservation = second_result.scalars().all()

        slots_deleted = len(slots_with_the_customer_reservation)

        for slot in slots_with_the_customer_reservation:
            slot.slot_status = "available"

        await db.delete(customer)
        await db.commit()

        return JSONResponse(
            {
                "action": "customer deleted",
                "customer_id": id_nbr,
                "slots_deleted": slots_deleted,
            },
            status_code=200,
        )


class WorkdayManager:

    async def get_workday_if_exsist_and_open_or_fail(self, date, db: AsyncSession):

        stmt = select(exists().where(WorkDay.date == date))
        result = await db.execute(stmt)

        workday = result.scalar()

        if workday is False:
            raise ResourceDoesNotExistException(
                resource_name="WorkDay", unit="date", identification_mark=str(date)
            )

        stmt = select(WorkDay).where(WorkDay.date == date)
        result = await db.execute(stmt)
        workday = result.scalars().first()

        if workday.day_status == "closed":
            raise WrongStatusException(resource_name="workday", status="closed")

        return workday

    async def get_slot_if_available_or_fail(self, workday, slot_nbr, db: AsyncSession):

        stmt = select(Slot).where(
            Slot.workday_id == workday.id, Slot.slot_nbr == slot_nbr
        )

        result = await db.execute(stmt)
        slot = result.scalars().first()

        if slot is None:
            raise ResourceDoesNotExistException(
                resource_name="slot", unit="WorkDay ID", identification_mark=workday.id
            )
        if slot.slot_status == "unavailable":
            raise WrongStatusException(resource_name="slot", status="unavailable")
        return slot

    async def get_all_slot_nbr_if_available_or_fail(self, date, db: AsyncSession):

        date = datetime.strptime(date, "%d.%m.%Y").date()
        workday = await self.get_workday_if_exsist_and_open_or_fail(date, db)
        stmt = select(Slot).where(
            and_(Slot.workday_id == workday.id, Slot.slot_status == "available")
        )

        results = await db.execute(stmt)
        available_slots = results.scalars().all()

        if available_slots is None:
            raise ResourceDoesNotExistException(
                resource_name="slot",
                unit="available status and date",
                identification_mark=str(date),
            )

        available_slots_list = []

        for slot in available_slots:
            available_slots_list.append(slot.slot_nbr)

        return available_slots_list

    async def convert_slot_list_into_hours(self, slots: list, db: AsyncSession):

        hours_list = []

        for slot in slots:
            stmt = select(SlotToHour).where(SlotToHour.slot_nbr == slot)
            result = await db.execute(stmt)
            hour_query = result.scalars().first()

            hours_list.append(hour_query.hour)

        return hours_list

    async def create_reservation(self, date, slot_nbr, customer_obj, db: AsyncSession):

        workday_obj = await self.get_workday_if_exsist_and_open_or_fail(date, db)

        if type(workday_obj) is JSONResponse:
            return workday_obj

        slot_obj = await self.get_slot_if_available_or_fail(workday_obj, slot_nbr, db)

        if type(slot_obj) is JSONResponse:
            return slot_obj

        slot_obj.slot_status = "unavailable"
        slot_obj.customer_id = customer_obj.id
        await db.commit()

        stmt = select(SlotToHour).where(SlotToHour.slot_nbr == slot_nbr)
        result = await db.execute(stmt)
        hour_of_booked_visit = result.scalars().first()

        return JSONResponse(
            {
                "action": "visitation reserved",
                "customer_id": f"{customer_obj.id}",
                "hour": f"{hour_of_booked_visit.hour}",
                "date": f"{date}",
                "slot_nbr": f"{slot_nbr}",
            }
        )

    async def get_all_workdays_obj_if_open(self, db: AsyncSession):
        stmt = select(WorkDay).where(WorkDay.day_status == "open")

        result = await db.execute(stmt)
        open_days = result.scalars().all()

        open_days_list = []

        if open_days is None:
            return []

        for day in open_days:
            open_days_list.append(day)

        return open_days_list

    async def put_new_slot_status(self, slot_id, slot_status, db: AsyncSession):

        stmt = select(Slot).where(Slot.id == slot_id)

        result = await db.execute(stmt)
        slot_obj = result.scalars().first()

        if not slot_obj:
            raise ResourceDoesNotExistException(
                resource_name="slot", unit="ID", identification_mark=str(slot_id)
            )
        if slot_status != "available" or "unavailable":
            raise WrongStatusException(resource_name="slot", status=slot_status)

        slot_obj.slot_status = slot_status
        slot_obj.customer_id = None

        await db.commit()

        return JSONResponse(
            {"detail": f"resource with ID = {slot_id} updated successfully"},
            status_code=200,
        )

    async def delete_slot(self, slot_id, db: AsyncSession):
        stmt = select(Slot).where(Slot.id == slot_id)

        result = await db.execute(stmt)
        slot_obj = result.scalars().first()

        if not slot_obj:
            raise ResourceDoesNotExistException(
                resource_name="slot", unit="ID", identification_mark=str(slot_id)
            )

        await db.delete(slot_obj)
        await db.commit()

        return JSONResponse({"action": "slot deleted", "slot_id": f"{slot_id}"})

    async def create_workday(self, date, db: AsyncSession, day_status="open"):

        date = datetime.strptime(date, "%d.%m.%Y").date()

        stmt = select(WorkDay).where(WorkDay.date == date)

        result = await db.execute(stmt)
        found_workday = result.scalars().first()

        if found_workday:
            raise ResourceAlreadyExistException(
                resource_name="workday", unit="date", identification_mark=str(date)
            )

        new_workday = WorkDay(date=date, day_status=day_status)
        db.add(new_workday)
        await db.commit()
        await db.refresh(new_workday)

        return JSONResponse(
            {
                "action": "workday_created",
                "workday_id": f"{new_workday.id}",
                "date": f"{date}",
            },
            status_code=201,
        )

    async def delete_workday(self, workday_id, db: AsyncSession):

        stmt = select(WorkDay).where(WorkDay.id == workday_id)

        result = await db.execute(stmt)
        found_workday = result.scalars().first()

        if not found_workday:
            raise ResourceDoesNotExistException(
                resource_name="workday", unit="ID", identification_mark=str(workday_id)
            )

        await db.delete(found_workday)
        await db.commit()

        return JSONResponse(
            {"action": "workday_deleted", "workday_id": f"{workday_id}"},
            status_code=202,
        )

visitation_manager_obj = VisitationManager()
customers_manager_obj = CustomersManager()
workday_manager_obj = WorkdayManager()
