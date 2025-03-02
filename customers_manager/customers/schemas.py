from pydantic import BaseModel


class CreateVisitRequest(BaseModel):
    name: str
    phone_nbr: str
    date: str
    slot: int


class DeleteCustomerRequest(BaseModel):
    user_id: int


class SetSlotStatusRequest(BaseModel):
    status: str
    slot_id: int


class DeleteSlotRequest(BaseModel):
    slot_id: int


class CreateWorkdayRequest(BaseModel):
    date: str
    day_status: str


class DeleteWorkdayRequest(BaseModel):
    workday_id: int
