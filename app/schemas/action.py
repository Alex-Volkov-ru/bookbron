from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ActionBase(BaseModel):
    description: str = Field(..., min_length=1)
    photo: Optional[str] = None  # UUID изображения


class ActionCreate(ActionBase):
    cafe_ids: Optional[List[int]] = []


class ActionUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=1)
    photo: Optional[str] = None
    cafe_ids: Optional[List[int]] = None
    active: Optional[bool] = None


class ActionResponse(ActionBase):
    id: int
    active: bool
    created_at: datetime
    updated_at: datetime
    cafe_ids: List[int] = []

    class Config:
        from_attributes = True

