async def send_email(email_data: dict):
    from main import send_email_task

    await send_email_task(email_data)
