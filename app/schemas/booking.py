from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from app.models.booking import BookingStatus


class BookingDishCreate(BaseModel):
    dish_id: int
    quantity: int = Field(1, gt=0)


class BookingBase(BaseModel):
    cafe_id: int
    table_id: int
    slot_id: int
    date: date
    note: Optional[str] = None
    dishes: Optional[List[BookingDishCreate]] = []


class BookingCreate(BookingBase):
    pass


class BookingUpdate(BaseModel):
    cafe_id: Optional[int] = None
    table_id: Optional[int] = None
    slot_id: Optional[int] = None
    date: Optional[date] = None
    status: Optional[BookingStatus] = None
    note: Optional[str] = None
    dishes: Optional[List[BookingDishCreate]] = None


class BookingDishResponse(BaseModel):
    id: int
    dish_id: int
    dish_name: str
    quantity: int
    price: float

    class Config:
        from_attributes = True


class BookingResponse(BookingBase):
    id: int
    user_id: int
    status: BookingStatus
    reminder_sent: bool
    active: bool
    created_at: datetime
    updated_at: datetime
    dishes: List[BookingDishResponse] = []

    class Config:
        from_attributes = True

