from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from database_structure.models import Customer, WorkDay
from database_structure.database import get_db, SessionLocal

router = APIRouter(prefix="/customers")


@router.get("/view/available/slots/on/{slot_date}/")
async def view_free_slots_on_specific_day(request: Request, slot_date: str, db: SessionLocal = Depends(get_db)):

    available_slots_query = db.query(WorkDay).filter(WorkDay.slot_status == 'available', WorkDay.date == slot_date).all()

    available_slots_list = []

    for slot_obj in available_slots_query:
        available_slots_list.append(slot_obj.slot_nbr)

    return JSONResponse({'available slots': available_slots_list})


@router.get("/create/visit/{name}/{phone_nbr}/{date}/{slot}/")  # ToDo change GET method to POST
async def create_visit(request: Request, name: str, phone_nbr: int, date: str, slot: str, db: SessionLocal = Depends(get_db)):
    check_if_user_history_exist = db.query(Customer).filter(Customer.name == name,
                                                            Customer.phone_number == phone_nbr).first()

    if check_if_user_history_exist is None:
        print('is non -check-')
        customer = Customer(name=name, phone_number=phone_nbr)  # , slots=new_visit_obj)
        db.add(customer)
        db.commit()
    else:
        print("is existing -check-")
        customer = db.query(Customer).filter(Customer.name == name, Customer.phone_number == phone_nbr).first()
        print("details of existing customer -check- ", customer)

    print('customer id -- ', customer.id)

    check_if_visit_available = db.query(WorkDay).filter(WorkDay.date == date, WorkDay.slot_nbr == slot).first()

    if check_if_visit_available.slot_status == "unavailable":
        return JSONResponse({"status": "fail",
                             "detail": "That slot is already taken,"
                                       " choose different slot for you visit"})

    new_visit = db.query(WorkDay).filter(WorkDay.date == date, WorkDay.slot_nbr == slot).first()
    new_visit.slot_status = 'unavailable'
    new_visit.customer_id = customer.id

    db.add(new_visit)
    db.commit()

    return JSONResponse({"visit_date": str(new_visit.date), "visit_slot":new_visit.slot_nbr, "phone_number": customer.phone_number})


@router.delete("/delete/visit/{name}/{last_name}/{phone_nbr}/{date}/{slot}/")
async def delete_visit():
    pass


@router.post("move/visit/{name}/{last_name}/{phone_nbr}/{date}/{slot}/{new_date}/{new_slot}/")
async def move_visit():
    pass
