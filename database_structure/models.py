from sqlalchemy.orm import declarative_base, relationship, validates
from sqlalchemy import Column, Integer, String, DATE, ForeignKey
from database_structure.database import db_engine, SessionLocal

Base = declarative_base()

VALID_SLOT_NUMBERS = {'slot_1': 'slot_1',
                      'slot_2': 'slot_2',
                      'slot_3': 'slot_3',
                      'slot_4': 'slot_4',
                      'slot_5': 'slot_5',
                      'slot_6': 'slot_6',
                      'slot_7': 'slot_7',
                      'slot_8': 'slot_8',
                      'slot_9': 'slot_9',
                      'slot_10': 'slot_10',
                      'slot_11': 'slot_11',
                      'slot_12': 'slot_12',
                      'slot_13': 'slot_13',
                      'slot_14': 'slot_14',
                      'slot_15': 'slot_15',
                      'slot_16': 'slot_16',
                      }

VALID_SLOT_STATUS = {'available': 'available',
                     'unavailable': 'unavailable',
                     }


class Customer(Base):

    __tablename__ = "customer"

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    name = Column('name', String)
    phone_number = Column('phone_number', Integer)
    slots = relationship('WorkDay', backref='customer')
    #slots = relationship('Slot', backref='customer')


# ToDo check on review if we are going to use only two models instead of three. If so then delete commented model
"""class Slot(Base):

    __tablename__ = "slot"

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    slot_number = Column('slot_number', Integer)
    date_slot = Column('date_slot', DATE)
    status = Column('status', String)
    #customer_id = Column(Integer, ForeignKey('customer.id'))

"""


class WorkDay(Base):

    __tablename__ = "workday"

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    date = Column('date', DATE)
    slot_nbr = Column('slot_nbr', String)  # ToDo ujednolicic nazwe do typu zmiennej
    slot_status = Column("slot_status", String, default="available")
    customer_id = Column(Integer, ForeignKey('customer.id'))

    @validates('slot_nbr')
    def validate_slot_nbr(self, key, slot_nbr):
        print(key, "--", slot_nbr)
        if slot_nbr not in VALID_SLOT_NUMBERS:
            raise ValueError("Invalid slot_nbr")
        return slot_nbr

    @validates('slot _status')
    def validate_slot_status(self, key, slot_status):
        if slot_status not in VALID_SLOT_STATUS:
            raise ValueError("Invalid slot_status")
        return slot_status


Base.metadata.create_all(bind=db_engine)

session = SessionLocal()


# ToDo move somewhere else the script for creating records with WorkDay for given dates and slots
def script(days: list, slots: list):
    for day in days:
        for slot in slots:

            slot_check = session.query(WorkDay).filter(WorkDay.date == day, WorkDay.slot_nbr == slot).first()
            if bool(slot_check):
                continue

            new_obj = WorkDay(date=day, slot_nbr=slot)
            session.add(new_obj)
            session.commit()
            session.refresh(new_obj)

    session.close()


list_days = ['01.01.2024']  # for the script purpose

list_slots = ['slot_1',  # for the script purpose
              'slot_2',
              'slot_3',
              'slot_4',
              'slot_5',
              'slot_6',
              'slot_7',
              'slot_8',
              'slot_9',
              'slot_10',
              'slot_11',
              'slot_12',
              'slot_13',
              'slot_14',
              'slot_15',
              'slot_16'
              ]

script(list_days, list_slots)

print('x')

# ToDo delete below comments after final implementation of models
"""
    slot_2 = Column('slot_2', Integer)
    slot_3 = Column('slot_3', Integer)
    slot_4 = Column('slot_4', Integer)
    slot_5 = Column('slot_5', Integer)
    slot_6 = Column('slot_6', Integer)
    slot_7 = Column('slot_7', Integer)
    slot_8 = Column('slot_8', Integer)
    slot_9 = Column('slot_9', Integer)
    slot_10 = Column('slot_10', Integer)
    slot_11 = Column('slot_11', Integer)
    slot_12 = Column('slot_12', Integer)
    slot_13 = Column('slot_13', Integer)
    slot_14 = Column('slot_14', Integer)
    slot_15 = Column('slot_15', Integer)
    slot_16 = Column('slot_16', Integer)
"""
