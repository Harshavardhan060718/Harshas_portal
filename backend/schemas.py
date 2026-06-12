from pydantic import BaseModel, EmailStr
from typing import Optional

# Base schema with shared attributes
class RecordBase(BaseModel):
    full_name: str
    email: str
    job_title: str
    department: str = "Engineering"
    salary: Optional[int] = None
    status: str = "Active"
    notes: Optional[str] = None

# Schema for incoming POST data (creation)
class RecordCreate(RecordBase):
    pass

# Schema for outgoing GET data (response)
class RecordResponse(RecordBase):
    id: str

    # Support compatibility for both Pydantic v1 and v2 ORM mapping
    class Config:
        orm_mode = True
        from_attributes = True
