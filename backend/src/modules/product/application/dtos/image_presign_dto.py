from pydantic import BaseModel


class ImagePresignRequest(BaseModel):
    filename: str
    content_type: str = "image/jpeg"
