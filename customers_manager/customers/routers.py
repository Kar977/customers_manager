from customers.schemas import (
    CreateVisitRequest,
    DeleteCustomerRequest,
    SetSlotAvailableRequest,
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
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/customers")


@router.get("/slots/all/available/")
async def view_all_open_dates_with_at_least_one_slot_available(
    request: Request, db: SessionLocal = Depends(get_db)
):

    return visitation_manager_obj.get_all_available_slots(db)


@router.get("/slots/{slot_date}/available/")
async def view_free_slots_on_specific_day(
    request: Request, slot_date: str, db: SessionLocal = Depends(get_db)
):

    available_slots = visitation_manager_obj.read_all_available_hours_on_specific_date(
        slot_date, db
    )
    return JSONResponse({slot_date: available_slots})


@router.post("/visit/", status_code=201)
async def create_visit(
    new_visit: CreateVisitRequest, db: SessionLocal = Depends(get_db)
):

    visit_reservation = visitation_manager_obj.reserve_visitation(
        new_visit.name, new_visit.phone_nbr, new_visit.date, new_visit.slot, db
    )

    return visit_reservation


@router.delete("/customer/", status_code=200)
async def delete_customer(
    customer_request: DeleteCustomerRequest, db: SessionLocal = Depends(get_db)
):

    return customers_manager_obj.delete_customer_and_release_slots(
        id_nbr=customer_request.user_id, db=db
    )


@router.put("/slot/set/available/")
async def set_slot_available(
    slot_request: SetSlotAvailableRequest, db: SessionLocal = Depends(get_db)
):

    return workday_manager_obj.put_slot_to_available(
        slot_id=slot_request.slot_id, db=db
    )


@router.delete("/slot/")
async def delete_slot(
    slot_request: DeleteSlotRequest, db: SessionLocal = Depends(get_db)
):

    return workday_manager_obj.delete_slot(slot_id=slot_request.slot_id, db=db)


@router.post("/workday/", status_code=201)
async def create_workday(
    workday_request: CreateWorkdayRequest, db: SessionLocal = Depends(get_db)
):

    return workday_manager_obj.create_workday(
        date=workday_request.date, day_status=workday_request.day_status, db=db
    )


@router.delete("/workday/", status_code=204)
async def delete_workday(
    workday_request: DeleteWorkdayRequest, db: SessionLocal = Depends(get_db)
):

    return workday_manager_obj.delete_workday(
        workday_id=workday_request.workday_id, db=db
    )
