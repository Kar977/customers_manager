from fastapi.exceptions import HTTPException


class ResourceDoesNotExistException(HTTPException):

    status_code = 404

    def __init__(self, identification_mark: str, unit: str, resource_name: str):
        detail = f"resource {resource_name} with {unit} = {identification_mark} does not exist"
        super().__init__(status_code=self.status_code, detail=detail)


class WrongStatusException(HTTPException):

    status_code = 409

    def __init__(self, resource_name: str, status: str):

        detail = f"{resource_name} has {status} status"
        super().__init__(status_code=self.status_code, detail=detail)


class ResourceAlreadyExistException(HTTPException):

    status_code = 409

    def __init__(self, resource_name: str, unit: str, identification_mark: str):
        detail = f"resource {resource_name} with {unit} = {identification_mark} already exist"
        super().__init__(status_code=self.status_code, detail=detail)
