from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
from app.models.booking import Booking, BookingStatus
from app.models.table import Table
from app.models.slot import Slot
from app.models.dish import Dish
from app.models.booking_dish import BookingDish


def check_booking_conflicts(
    db: Session,
    user_id: int,
    table_id: int,
    slot_id: int,
    booking_date: date,
    exclude_booking_id: int = None
) -> bool:
    """Проверка пересечений бронирований"""
    # Получение слота для проверки времени
    slot = db.query(Slot).filter(Slot.id == slot_id).first()
    if not slot:
        return False
    
    # Поиск существующих бронирований на тот же стол, дату и время
    query = db.query(Booking).filter(
        and_(
            Booking.table_id == table_id,
            Booking.slot_id == slot_id,
            Booking.date == booking_date,
            Booking.status != BookingStatus.CANCELLED,
            Booking.active == True
        )
    )
    
    if exclude_booking_id:
        query = query.filter(Booking.id != exclude_booking_id)
    
    existing_booking = query.first()
    
    return existing_booking is not None


def validate_booking_date(booking_date: date) -> None:
    """Проверка что дата бронирования не в прошлом"""
    today = date.today()
    if booking_date < today:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя забронировать стол на прошедшую дату"
        )


def validate_booking_status(booking: Booking) -> None:
    """Проверка что бронирование можно изменить"""
    if booking.status in [BookingStatus.COMPLETED, BookingStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя изменить завершенное или отмененное бронирование"
        )
    
    # Проверка что дата не в прошлом
    if booking.date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя изменить прошедшее бронирование"
        )


def create_booking_dishes(
    db: Session,
    booking_id: int,
    dishes_data: list
) -> list:
    """Создание записей о блюдах в бронировании"""
    booking_dishes = []
    
    for dish_data in dishes_data:
        dish = db.query(Dish).filter(Dish.id == dish_data["dish_id"]).first()
        if not dish:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dish {dish_data['dish_id']} not found"
            )
        
        booking_dish = BookingDish(
            booking_id=booking_id,
            dish_id=dish.id,
            quantity=dish_data["quantity"],
            price=dish.price
        )
        booking_dishes.append(booking_dish)
        db.add(booking_dish)
    
    return booking_dishes

