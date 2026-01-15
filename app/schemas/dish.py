from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class DishBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    photo: Optional[str] = None  # UUID изображения
    price: Decimal = Field(..., gt=0)


class DishCreate(DishBase):
    cafe_ids: Optional[List[int]] = []


class DishUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    photo: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    cafe_ids: Optional[List[int]] = None
    active: Optional[bool] = None


class DishResponse(DishBase):
    id: int
    active: bool
    created_at: datetime
    updated_at: datetime
    cafe_ids: List[int] = []

    class Config:
        from_attributes = True

