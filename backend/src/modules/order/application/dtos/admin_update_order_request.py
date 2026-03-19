from pydantic import BaseModel, Field
from typing import Optional

class AdminUpdateOrderRequest(BaseModel):
    status: Optional[str] = Field(default=None, description="新狀態 (例如: SHIPPED, COMPLETED, CANCELLED)")
    admin_note: Optional[str] = Field(default=None, description="管理員內部備註")
