from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Todo(BaseModel):
    id: int
    title: str = Field(min_length=3, max_length=100)
    description: Optional[str] = None
    completed: bool = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TodoUpdate(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    description: Optional[str] = None
    completed: bool = False