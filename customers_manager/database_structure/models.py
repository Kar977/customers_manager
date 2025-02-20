from database_structure.database import db_engine
from sqlalchemy import Column, Integer, String, DATE, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, validates

Base = declarative_base()

VALID_HOURS = (
    "08:00",
    "08:30",
    "09:00",
    "09:30",
    "10:00",
    "10:30",
    "11:00",
    "11:30",
    "12:00",
    "12:30",
    "13:00",
    "13:30",
    "14:00",
    "14:30",
    "15:00",
    "15:30",
    "16:00",
    "16:30",
    "17:00",
    "17:30",
)

VALID_SLOT_STATUS = ("available", "unavailable")

VALID_DAY_STATUS = ("open", "close")


class Customer(Base):

    __tablename__ = "customer"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String)
    phone_number = Column("phone_number", Integer)
    slots = relationship("Slot", backref="customer")


class Slot(Base):

    __tablename__ = "slot"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    slot_nbr = Column("slot_nbr", Integer)
    slot_status = Column("slot_status", String, default=VALID_SLOT_STATUS[0])
    customer_id = Column(Integer, ForeignKey("customer.id"))
    workday_id = Column(Integer, ForeignKey("workday.id"))

    @validates("slot_nbr")
    def validate_slot_nbr(self, key, slot_nbr):
        if not (0 < int(slot_nbr) <= 20):
            raise ValueError(
                f"Invalid slot_nbr: {slot_nbr}. Must be one in range of 1 to 20"
            )
        return slot_nbr

    @validates("slot_status")
    def validate_slot_status(self, key, slot_status):
        if slot_status not in VALID_SLOT_STATUS:
            raise ValueError(
                f"Invalid slot_status: {slot_status}. Must be one of {VALID_SLOT_STATUS}"
            )
        return slot_status


class WorkDay(Base):

    __tablename__ = "workday"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    date = Column("date", DATE)
    day_status = Column("day_status", String, default="open")
    slots = relationship("Slot", backref="workday", cascade="all,delete")

    @validates("day_status")
    def validate_day_status(self, key, day_status):
        if day_status not in VALID_DAY_STATUS:
            raise ValueError(
                f"Invalid day_status: {day_status}. Must be one of {VALID_DAY_STATUS}"
            )
        return day_status


class SlotToHour(Base):

    __tablename__ = "slottohour"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    slot_nbr = Column("slot_nbr", Integer, unique=True)
    hour = Column("hour", String, unique=True)

    @validates("slot_nbr")
    def validate_slot_nbr(self, key, slot_nbr):
        if not (0 < int(slot_nbr) <= 20):
            raise ValueError(
                f"Invalid slot_nbr: {slot_nbr}. Must be one in range of 1 to 20"
            )
        return slot_nbr

    @validates("hour")
    def validate_hour(self, key, hour):
        if hour not in VALID_HOURS:
            raise ValueError(
                f"Invalid hour: {hour}. Must be on in range of {VALID_HOURS}"
            )
        return hour


Base.metadata.create_all(bind=db_engine)
