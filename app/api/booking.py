from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from app.database import get_db
from app.models.booking import Booking, BookingStatus
from app.models.booking_dish import BookingDish
from app.models.user import User, UserRole
from app.models.cafe import Cafe
from app.models.table import Table
from app.models.slot import Slot
from app.schemas.booking import BookingCreate, BookingUpdate, BookingResponse, BookingDishResponse
from app.core.auth import get_current_active_user, require_role
from app.services.booking_service import (
    check_booking_conflicts,
    validate_booking_date,
    validate_booking_status,
    create_booking_dishes
)
from app.utils.logger import logger

router = APIRouter(prefix="/booking", tags=["Бронирования"])


@router.get("", response_model=List[BookingResponse])
async def get_bookings(
    user_id: int = None,
    cafe_id: int = None,
    booking_date: date = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получение списка бронирований"""
    query = db.query(Booking)
    
    # Пользователь видит только свои бронирования, админы и менеджеры - все
    user_role = current_user.role if isinstance(current_user.role, str) else current_user.role.value
    if user_role == "user":
        query = query.filter(Booking.user_id == current_user.id)
    elif user_id:
        query = query.filter(Booking.user_id == user_id)
    
    if cafe_id:
        query = query.filter(Booking.cafe_id == cafe_id)
    
    if booking_date:
        query = query.filter(Booking.date == booking_date)
    
    bookings = query.offset(skip).limit(limit).all()
    
    # Преобразование для response
    result = []
    for booking in bookings:
        dishes_response = [
            BookingDishResponse(
                id=bd.id,
                dish_id=bd.dish_id,
                dish_name=bd.dish.name,
                quantity=bd.quantity,
                price=float(bd.price)
            )
            for bd in booking.dishes
        ]
        
        booking_dict = {
            **{c.name: getattr(booking, c.name) for c in booking.__table__.columns},
            "dishes": dishes_response
        }
        result.append(BookingResponse(**booking_dict))
    
    return result


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получение бронирования по ID"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Пользователь может видеть только свои бронирования
    user_role = current_user.role if isinstance(current_user.role, str) else current_user.role.value
    if user_role == "user" and booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    dishes_response = [
        BookingDishResponse(
            id=bd.id,
            dish_id=bd.dish_id,
            dish_name=bd.dish.name,
            quantity=bd.quantity,
            price=float(bd.price)
        )
        for bd in booking.dishes
    ]
    
    booking_dict = {
        **{c.name: getattr(booking, c.name) for c in booking.__table__.columns},
        "dishes": dishes_response
    }
    return BookingResponse(**booking_dict)


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Создание нового бронирования"""
    # Валидация даты
    validate_booking_date(booking_data.date)
    
    # Проверка существования кафе, стола и слота
    cafe = db.query(Cafe).filter(Cafe.id == booking_data.cafe_id).first()
    if not cafe or not cafe.active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cafe not found or inactive"
        )
    
    table = db.query(Table).filter(Table.id == booking_data.table_id).first()
    if not table or not table.active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Table not found or inactive"
        )
    
    if table.cafe_id != booking_data.cafe_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Table does not belong to this cafe"
        )
    
    slot = db.query(Slot).filter(Slot.id == booking_data.slot_id).first()
    if not slot or not slot.active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slot not found or inactive"
        )
    
    if slot.cafe_id != booking_data.cafe_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slot does not belong to this cafe"
        )
    
    # Проверка пересечений
    if check_booking_conflicts(
        db, current_user.id, booking_data.table_id, booking_data.slot_id, booking_data.date
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Этот стол и временной слот уже забронированы"
        )
    
    # Создание бронирования
    new_booking = Booking(
        user_id=current_user.id,
        cafe_id=booking_data.cafe_id,
        table_id=booking_data.table_id,
        slot_id=booking_data.slot_id,
        date=booking_data.date,
        note=booking_data.note,
        status=BookingStatus.PENDING
    )
    
    db.add(new_booking)
    db.flush()
    
    # Добавление блюд если есть
    if booking_data.dishes:
        dishes_data = [{"dish_id": d.dish_id, "quantity": d.quantity} for d in booking_data.dishes]
        create_booking_dishes(db, new_booking.id, dishes_data)
    
    db.commit()
    db.refresh(new_booking)
    
    logger.info(f"User {current_user.username} (id: {current_user.id}) created booking {new_booking.id}")
    
    # Отправка уведомления администратору (через Celery)
    from app.tasks.notifications import send_booking_notification
    send_booking_notification.delay(new_booking.id, "created")
    
    # Получение полной информации для response
    booking = db.query(Booking).filter(Booking.id == new_booking.id).first()
    dishes_response = [
        BookingDishResponse(
            id=bd.id,
            dish_id=bd.dish_id,
            dish_name=bd.dish.name,
            quantity=bd.quantity,
            price=float(bd.price)
        )
        for bd in booking.dishes
    ]
    
    booking_dict = {
        **{c.name: getattr(booking, c.name) for c in booking.__table__.columns},
        "dishes": dishes_response
    }
    return BookingResponse(**booking_dict)


@router.patch("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: int,
    booking_data: BookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Обновление бронирования"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Пользователь может изменять только свои бронирования
    user_role = current_user.role if isinstance(current_user.role, str) else current_user.role.value
    if user_role == "user" and booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Валидация статуса
    validate_booking_status(booking)
    
    update_data = booking_data.model_dump(exclude_unset=True, exclude={"dishes"})
    
    # Валидация даты если она обновляется
    if "date" in update_data:
        validate_booking_date(update_data["date"])
    
    # Проверка пересечений если меняются стол, слот или дата
    if any(key in update_data for key in ["table_id", "slot_id", "date"]):
        table_id = update_data.get("table_id", booking.table_id)
        slot_id = update_data.get("slot_id", booking.slot_id)
        booking_date = update_data.get("date", booking.date)
        
        if check_booking_conflicts(db, booking.user_id, table_id, slot_id, booking_date, booking_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This table and time slot are already booked"
            )
    
    # Обновление полей
    for field, value in update_data.items():
        setattr(booking, field, value)
    
    # Обновление блюд если они указаны
    if booking_data.dishes is not None:
        # Удаление старых блюд
        db.query(BookingDish).filter(BookingDish.booking_id == booking_id).delete()
        # Добавление новых
        if booking_data.dishes:
            dishes_data = [{"dish_id": d.dish_id, "quantity": d.quantity} for d in booking_data.dishes]
            create_booking_dishes(db, booking_id, dishes_data)
    
    db.commit()
    db.refresh(booking)
    
    logger.info(f"User {current_user.username} (id: {current_user.id}) updated booking {booking.id}")
    
    # Отправка уведомления администратору
    from app.tasks.notifications import send_booking_notification
    send_booking_notification.delay(booking.id, "updated")
    
    # Получение полной информации для response
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    dishes_response = [
        BookingDishResponse(
            id=bd.id,
            dish_id=bd.dish_id,
            dish_name=bd.dish.name,
            quantity=bd.quantity,
            price=float(bd.price)
        )
        for bd in booking.dishes
    ]
    
    booking_dict = {
        **{c.name: getattr(booking, c.name) for c in booking.__table__.columns},
        "dishes": dishes_response
    }
    return BookingResponse(**booking_dict)


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Отмена бронирования"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Пользователь может отменять только свои бронирования
    user_role = current_user.role if isinstance(current_user.role, str) else current_user.role.value
    if user_role == "user" and booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    validate_booking_status(booking)
    
    booking.status = BookingStatus.CANCELLED
    db.commit()
    
    logger.info(f"User {current_user.username} (id: {current_user.id}) cancelled booking {booking.id}")
    
    # Отправка уведомления администратору
    from app.tasks.notifications import send_booking_notification
    send_booking_notification.delay(booking.id, "cancelled")
    
    return None

