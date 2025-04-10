import json
from http import HTTPStatus

from customers_manager.customers.rabbitmq import rabbitmq
from customers_manager.customers.schemas import (
    CreateVisitRequest,
    DeleteCustomerRequest,
    SetSlotStatusRequest,
    CreateWorkdayRequest,
    DeleteWorkdayRequest,
    DeleteSlotRequest,
)
from customers_manager.customers.services.crud import (
    customers_manager_obj,
    workday_manager_obj,
    visitation_manager_obj,
)
from customers_manager.database_structure.database import get_db
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/customers")


@router.get("/slots/available/") #ok
async def view_all_open_dates_with_at_least_one_slot_available(
    request: Request, db: AsyncSession = Depends(get_db)
):
    return await visitation_manager_obj.get_all_available_slots(db)


@router.get("/slots/available/{slot_date}") #ok
async def view_free_slots_on_specific_day(
    request: Request, slot_date: str, db: AsyncSession = Depends(get_db)
):

    available_slots = (
        await visitation_manager_obj.read_all_available_hours_on_specific_date(
            slot_date, db
        )
    )
    return JSONResponse({slot_date: available_slots})


@router.post("/visit/", status_code=201) #ok
async def create_visit(
    new_visit: CreateVisitRequest, db: AsyncSession = Depends(get_db)
):

    visit_reservation = await visitation_manager_obj.reserve_visitation(
        new_visit.name, new_visit.phone_nbr, new_visit.date, new_visit.slot, db
    )

    if visit_reservation.status_code == HTTPStatus(200):
        data = json.loads(visit_reservation.body)
        email_data = {
            "title": "Visit booked",
            "email_body": f"Hi,\nWe confirm your visit on {data.get('date')} at {data.get('hour')}.\nSee you at the site.",
        }

        await rabbitmq.send_email_task(email_data)

    return visit_reservation


@router.delete("/customer/", status_code=200)
async def delete_customer(
    customer_request: DeleteCustomerRequest, db: AsyncSession = Depends(get_db)
):
    delete_reservation = await customers_manager_obj.delete_customer_and_release_slots(
        id_nbr=customer_request.user_id, db=db
    )
    if delete_reservation.status_code == HTTPStatus(200):
        data = json.loads(delete_reservation.body)
        email_data = {
            "title": "Visit deleted",
            "email_body": f"Hi, \nWe are sending you confirmation that your visit on {data.get('date')} at {data.get('hour')} has been deleted.",
        }

        await rabbitmq.send_email_task(email_data)

    return delete_reservation


@router.put("/slot/status/")
async def set_slot_status(
    slot_request: SetSlotStatusRequest, db: AsyncSession = Depends(get_db)
):

    return await workday_manager_obj.put_new_slot_status(
        slot_id=slot_request.slot_id, slot_status=slot_request.slot_status, db=db
    )


@router.delete("/slot/")
async def delete_slot(
    slot_request: DeleteSlotRequest, db: AsyncSession = Depends(get_db)
):

    return await workday_manager_obj.delete_slot(slot_id=slot_request.slot_id, db=db)


@router.post("/workday/", status_code=201) #ok
async def create_workday(
    workday_request: CreateWorkdayRequest, db: AsyncSession = Depends(get_db)
):
    return await workday_manager_obj.create_workday(
        date=workday_request.date, day_status=workday_request.day_status, db=db
    )


@router.delete("/workday/", status_code=204) #ok
async def delete_workday(
    workday_request: DeleteWorkdayRequest, db: AsyncSession = Depends(get_db)
):

    return await workday_manager_obj.delete_workday(
        workday_id=workday_request.workday_id, db=db
    )
