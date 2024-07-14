from fastapi import FastAPI

from customers import routers as customer_router

app = FastAPI()

app.include_router(customer_router.router)