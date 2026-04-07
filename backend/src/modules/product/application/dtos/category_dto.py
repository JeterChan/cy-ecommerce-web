from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class CategoryResponseDTO(BaseModel):
    id: int
    name: str
    slug: str
    model_config = ConfigDict(from_attributes=True)


class CategoryCreateDTO(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="分類名稱")
    slug: str = Field(
        ...,
        min_length=1,
        max_length=50,
        pattern=r"^[a-z0-9-]+$",
        description="分類 slug，小寫英數字和連字號",
    )


class CategoryUpdateDTO(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    slug: Optional[str] = Field(
        None, min_length=1, max_length=50, pattern=r"^[a-z0-9-]+$"
    )
