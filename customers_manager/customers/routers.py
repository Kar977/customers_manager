from customers.schemas import (
    CreateVisitRequest,
    DeleteCustomerRequest,
    SetSlotStatusRequest,
    CreateWorkdayRequest,
    DeleteWorkdayRequest,
    DeleteSlotRequest,
)
from customers.services.crud import (
    customers_manager_obj,
    workday_manager_obj,
    visitation_manager_obj,
)
from database_structure.database import get_db, SessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/customers")


@router.get("/slots/available/")
async def view_all_open_dates_with_at_least_one_slot_available(
    request: Request, db: AsyncSession = Depends(get_db)
):

    return await visitation_manager_obj.get_all_available_slots(db)


@router.get("/slots/available/{slot_date}")
async def view_free_slots_on_specific_day(
    request: Request, slot_date: str, db: AsyncSession = Depends(get_db)
):

    available_slots = await visitation_manager_obj.read_all_available_hours_on_specific_date(
        slot_date, db
    )
    return JSONResponse({slot_date: available_slots})


@router.post("/visit/", status_code=201)
async def create_visit(
    new_visit: CreateVisitRequest, db: AsyncSession = Depends(get_db)
):

    visit_reservation = await visitation_manager_obj.reserve_visitation(
        new_visit.name, new_visit.phone_nbr, new_visit.date, new_visit.slot, db
    )

    return visit_reservation


@router.delete("/customer/", status_code=200)
async def delete_customer(
    customer_request: DeleteCustomerRequest, db: AsyncSession = Depends(get_db)
):

    return await customers_manager_obj.delete_customer_and_release_slots(
        id_nbr=customer_request.user_id, db=db
    )


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


@router.post("/workday/", status_code=201)
async def create_workday(
    workday_request: CreateWorkdayRequest, db: AsyncSession = Depends(get_db)
):

    return await workday_manager_obj.create_workday(
        date=workday_request.date, day_status=workday_request.day_status, db=db
    )


@router.delete("/workday/", status_code=204)
async def delete_workday(
    workday_request: DeleteWorkdayRequest, db: AsyncSession = Depends(get_db)
):

    return await workday_manager_obj.delete_workday(
        workday_id=workday_request.workday_id, db=db
    )
