
class TBException(Exception):
    def __init__(self, status_code: int, message: str, resolution: str):
        self.status_code = status_code
        self.message = message
        self.resolution = resolution

from pydantic import BaseModel
class TBResponse(BaseModel):
    message: str
    payload: dict


