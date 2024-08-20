from fastapi import FastAPI

from customers import routers as customer_router
from customers.services.exceptions import ResourceDoesNotExistException, ResourceAlreadyExistException, WrongStatusException
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi import Request

app = FastAPI()


def my_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"message": exc.detail})


app.include_router(customer_router.router)
app.add_exception_handler(ResourceDoesNotExistException, my_http_exception_handler)
app.add_exception_handler(ResourceAlreadyExistException, my_http_exception_handler)
app.add_exception_handler(WrongStatusException, my_http_exception_handler)
