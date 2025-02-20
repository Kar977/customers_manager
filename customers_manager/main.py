from fastapi import FastAPI
from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from customers import routers as customer_router
from customers.services.exceptions import ResourceDoesNotExistException, ResourceAlreadyExistException, \
    WrongStatusException

app = FastAPI()


def my_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"message": exc.detail})


app.include_router(customer_router.router)
app.add_exception_handler(ResourceDoesNotExistException, my_http_exception_handler)
app.add_exception_handler(ResourceAlreadyExistException, my_http_exception_handler)
app.add_exception_handler(WrongStatusException, my_http_exception_handler)
