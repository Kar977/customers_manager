"""
      check_if_workday_available = db.query(exists().where(WorkDay.date == date)).scalar()
        print('check workday', check_if_workday_available)
        print('date:', date)

        if check_if_workday_available is False:
            return JSONResponse({"status": "fail",
                                 "deatil": "WorkDay does not exists"})

        check_if_workday_available = db.query(WorkDay).filter(WorkDay.date == date).first()

        if check_if_workday_available.day_status == "closed":
            return JSONResponse({"status": "fail",
                                 "detail": "WorkDay is closed"})

        check_if_slot_available = db.query(Slot).filter(Slot.workday_id == check_if_workday_available.id,
                                                        Slot.slot_nbr == slot).first()

        print("check if slot available", check_if_slot_available)

        if check_if_slot_available is None:
            return JSONResponse({"status": "fail",
                                 "detail": "The slot does not exists"})

        if check_if_slot_available.slot_status == "unavailable":
            return JSONResponse({"status": "fail",
                                 "detail": "That slot is already taken,"
                                           " choose different slot for you visit"})

        check_if_slot_available.slot_status = "unavailable"
        check_if_slot_available.customer_id = user.id
        db.commit()

        return JSONResponse({"status": "positive",
                             "detail": f'user {user.name} booked visit on {date}, {slot} slot'})
"""