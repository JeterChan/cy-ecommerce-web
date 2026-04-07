from pydantic import BaseModel


class UpdateStatusRequest(BaseModel):
    status: str
