from fastapi.responses import JSONResponse
from sqlalchemy.sql import exists

from customers.services.exceptions import (
    ResourceDoesNotExistException,
    WrongStatusException,
    ResourceAlreadyExistException,
)
from database_structure.models import Customer, Slot, WorkDay, SlotToHour


class VisitationManager:

    def __init__(self):
        self.customers_manager = CustomersManager()
        self.workday_manager = WorkdayManager()

    def reserve_visitation(self, name, phone_nbr, date, slot, db):

        customer_obj = self.customers_manager.get_or_create_customer(
            name, phone_nbr, db
        )
        return self.workday_manager.create_reservation(date, slot, customer_obj, db)

    def read_all_available_hours_on_specific_date(self, date, db):
        workday_obj = self.workday_manager.get_all_slot_nbr_if_available_or_fail(
            date, db
        )
        return self.workday_manager.convert_slot_list_into_hours(workday_obj, db)

    def get_all_available_slots(self, db):

        available_slots_per_date_dict = {}

        available_slots = (
            db.query(WorkDay, Slot, SlotToHour)
            .filter(Slot.slot_status == "available")
            .filter(WorkDay.id == Slot.workday_id)
            .filter(Slot.slot_nbr == SlotToHour.slot_nbr)
            .all()
        )

        for obj in available_slots:

            if str(obj[0].date) not in available_slots_per_date_dict.keys():
                available_slots_per_date_dict[str(obj[0].date)] = [obj[2].hour]
            else:
                available_slots_per_date_dict[str(obj[0].date)].append(obj[2].hour)

        return available_slots_per_date_dict


class CustomersManager:

    def __init__(self):
        pass

    def get_or_create_customer(self, name, phone_nbr, db):
        found_user = (
            db.query(Customer)
            .filter(Customer.name == name, Customer.phone_number == phone_nbr)
            .first()
        )
        if found_user is None:
            customer = Customer(name=name, phone_number=phone_nbr)
            db.add(customer)
            db.commit()
            return customer

        return found_user

    def delete_customer_and_release_slots(self, id_nbr, db):
        customer = db.query(Customer).filter(Customer.id == id_nbr).first()

        if customer is None:
            raise ResourceDoesNotExistException(
                resource_name="customer", unit="ID", identification_mark=str(id_nbr)
            )

        slots_with_the_customer_reservation = (
            db.query(Slot).filter(Slot.customer_id == customer.id).all()
        )

        slots_deleted = len(slots_with_the_customer_reservation)

        for slot in slots_with_the_customer_reservation:
            slot.slot_status = "available"

        db.delete(customer)
        db.commit()

        return JSONResponse(
            {
                "action": "customer deleted",
                "customer_id": id_nbr,
                "slots_deleted": slots_deleted,
            },
            status_code=200,
        )


class WorkdayManager:

    def get_workday_if_exsist_and_open_or_fail(self, date, db):

        workday = db.query(exists().where(WorkDay.date == date)).scalar()

        if workday is False:
            raise ResourceDoesNotExistException(
                resource_name="WorkDay", unit="date", identification_mark=str(date)
            )

        workday = db.query(WorkDay).filter(WorkDay.date == date).first()

        if workday.day_status == "closed":
            raise WrongStatusException(resource_name="workday", status="closed")

        return workday

    def get_slot_if_available_or_fail(self, workday, slot_nbr, db):

        slot = (
            db.query(Slot)
            .filter(Slot.workday_id == workday.id, Slot.slot_nbr == slot_nbr)
            .first()
        )

        if slot is None:
            raise ResourceDoesNotExistException(
                resource_name="slot", unit="WorkDay ID", identification_mark=workday.id
            )
        if slot.slot_status == "unavailable":
            raise WrongStatusException(resource_name="slot", status="unavailable")
        return slot

    def get_all_slot_nbr_if_available_or_fail(self, date, db):

        workday = self.get_workday_if_exsist_and_open_or_fail(date, db)
        available_slots = (
            db.query(Slot)
            .filter(Slot.workday_id == workday.id, Slot.slot_status == "available")
            .all()
        )

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

    def convert_slot_list_into_hours(self, slots: list, db):

        hours_list = []

        for slot in slots:
            hour_query = (
                db.query(SlotToHour).filter(SlotToHour.slot_nbr == slot).first()
            )
            hours_list.append(hour_query.hour)

        return hours_list

    def create_reservation(self, date, slot_nbr, customer_obj, db):

        workday_obj = self.get_workday_if_exsist_and_open_or_fail(date, db)

        if type(workday_obj) is JSONResponse:
            return workday_obj

        slot_obj = self.get_slot_if_available_or_fail(workday_obj, slot_nbr, db)

        if type(slot_obj) is JSONResponse:
            return slot_obj

        slot_obj.slot_status = "unavailable"
        slot_obj.customer_id = customer_obj.id
        db.commit()

        hour_of_booked_visit = (
            db.query(SlotToHour).filter(SlotToHour.slot_nbr == slot_nbr).first()
        )

        return JSONResponse(
            {
                "action": "visitation reserved",
                "customer_id": f"{customer_obj.id}",
                "hour": f"{hour_of_booked_visit.hour}",
                "date": f"{date}",
                "slot_nbr": f"{slot_nbr}",
            }
        )

    def get_all_workdays_obj_if_open(self, db):
        open_days = db.query(WorkDay).filter(WorkDay.day_status == "open").all()

        open_days_list = []

        if open_days is None:
            return []

        for day in open_days:
            open_days_list.append(day)

        return open_days_list

    def put_slot_to_available(self, slot_id, db):

        slot_obj = db.query(Slot).filter(Slot.id == slot_id).first()

        if not slot_obj:
            raise ResourceDoesNotExistException(
                resource_name="slot", unit="ID", identification_mark=str(slot_id)
            )
        if slot_obj.slot_status == "available":
            raise WrongStatusException(resource_name="slot", status="available")

        slot_obj.slot_status = "available"
        slot_obj.customer_id = None

        db.commit()

        return JSONResponse(
            {"detail": f"resource with ID = {slot_id} updated successfully"},
            status_code=200,
        )

    def delete_slot(self, slot_id, db):
        slot_obj = db.query(Slot).filter(Slot.id == slot_id).first()

        if not slot_obj:
            raise ResourceDoesNotExistException(
                resource_name="slot", unit="ID", identification_mark=str(slot_id)
            )

        db.delete(slot_obj)
        db.commit()

        return JSONResponse({"action": "slot deleted", "slot_id": f"{slot_id}"})

    def create_workday(self, date, db, day_status="open"):

        found_workday = db.query(WorkDay).filter(WorkDay.date == date).first()
        if found_workday:
            raise ResourceAlreadyExistException(
                resource_name="workday", unit="date", identification_mark=str(date)
            )

        new_workday = WorkDay(date=date, day_status=day_status)
        db.add(new_workday)
        db.commit()

        return JSONResponse(
            {
                "action": "workday_created",
                "workday_id": f"{new_workday.id}",
                "date": f"{date}",
            },
            status_code=202,
        )

    def delete_workday(self, workday_id, db):

        found_workday = db.query(WorkDay).filter(WorkDay.id == workday_id).first()

        if not found_workday:
            raise ResourceDoesNotExistException(
                resource_name="workday", unit="ID", identification_mark=str(workday_id)
            )

        db.delete(found_workday)
        db.commit()

        return JSONResponse(
            {"action": "workday_deleted", "workday_id": f"{workday_id}"},
            status_code=202,
        )


visitation_manager_obj = VisitationManager()
customers_manager_obj = CustomersManager()
workday_manager_obj = WorkdayManager()
