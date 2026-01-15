from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, time


class SlotBase(BaseModel):
    start_time: time
    end_time: time


class SlotCreate(SlotBase):
    pass


class SlotUpdate(BaseModel):
    cafe_id: Optional[int] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    active: Optional[bool] = None


class SlotResponse(BaseModel):
    id: int
    cafe_id: int
    start_time: time
    end_time: time
    active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

