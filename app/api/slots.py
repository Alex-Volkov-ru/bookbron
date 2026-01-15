from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import time, timedelta
from app.database import get_db
from app.models.slot import Slot
from app.models.cafe import Cafe
from app.models.user import User
from app.schemas.slot import SlotCreate, SlotUpdate, SlotResponse
from app.core.auth import get_current_active_user, require_role
from app.utils.logger import logger

router = APIRouter(prefix="/cafe/{cafe_id}/slots", tags=["Временные слоты"])


@router.get("", response_model=List[SlotResponse])
async def get_slots(
    cafe_id: int,
    show_all: bool = False,
    active_only: bool = False,
    booking_date: str = None,  # Дата для фильтрации забронированных слотов
    table_id: int = None,  # ID стола для фильтрации
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Список временных слотов в кафе"""
    from datetime import date
    from app.models.booking import Booking, BookingStatus
    
    # Проверка существования кафе
    cafe = db.query(Cafe).filter(Cafe.id == cafe_id).first()
    if not cafe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Кафе не найдено"
        )
    
    query = db.query(Slot).filter(Slot.cafe_id == cafe_id)
    
    # Фильтрация по active_only (приоритет над show_all)
    if active_only:
        query = query.filter(Slot.active == True)
    elif not show_all:
        # Для пользователей показываем только активные, для админов и менеджеров - все если show_all=True
        user_role = current_user.role if isinstance(current_user.role, str) else current_user.role.value
        if user_role not in ["admin", "manager"]:
            query = query.filter(Slot.active == True)
    
    slots = query.all()
    
    # Для пользователей фильтруем забронированные слоты на указанную дату и стол
    user_role = current_user.role if isinstance(current_user.role, str) else current_user.role.value
    if user_role == "user" and booking_date and table_id:
        try:
            booking_date_obj = date.fromisoformat(booking_date)
            # Получаем ID забронированных слотов
            booked_slot_ids = db.query(Booking.slot_id).filter(
                Booking.cafe_id == cafe_id,
                Booking.table_id == table_id,
                Booking.date == booking_date_obj,
                Booking.status != BookingStatus.CANCELLED,
                Booking.active == True
            ).distinct().all()
            booked_ids = [row[0] for row in booked_slot_ids]
            # Фильтруем слоты, исключая забронированные
            slots = [s for s in slots if s.id not in booked_ids]
        except ValueError:
            pass  # Неверный формат даты, возвращаем все слоты
    
    return slots


@router.get("/{slot_id}", response_model=SlotResponse)
async def get_slot(
    slot_id: int,
    db: Session = Depends(get_db)
):
    """Получение слота по ID"""
    slot = db.query(Slot).filter(Slot.id == slot_id).first()
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Слот не найден"
        )
    return slot


@router.post("", response_model=SlotResponse, status_code=status.HTTP_201_CREATED)
async def create_slot(
    cafe_id: int,
    slot_data: SlotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager"))
):
    """Новый временной слот в кафе"""
    # Проверка существования кафе
    cafe = db.query(Cafe).filter(Cafe.id == cafe_id).first()
    if not cafe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Кафе не найдено"
        )
    
    # Проверка прав менеджера
    user_role = current_user.role if isinstance(current_user.role, str) else current_user.role.value
    if user_role == "manager" and current_user not in cafe.managers:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    
    # Проверка корректности времени
    if slot_data.start_time >= slot_data.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Время начала должно быть раньше времени окончания"
        )
    
    new_slot = Slot(
        cafe_id=cafe_id,
        start_time=slot_data.start_time,
        end_time=slot_data.end_time
    )
    
    db.add(new_slot)
    db.commit()
    db.refresh(new_slot)
    
    logger.info(f"User {current_user.username} (id: {current_user.id}) created slot {new_slot.id} for cafe {cafe.name}")
    
    return new_slot


@router.post("/generate", response_model=List[SlotResponse], status_code=status.HTTP_201_CREATED)
async def generate_slots(
    cafe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager"))
):
    """Автоматическое создание слотов на основе рабочего времени кафе"""
    cafe = db.query(Cafe).filter(Cafe.id == cafe_id).first()
    if not cafe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Кафе не найдено"
        )
    
    # Проверка прав менеджера
    user_role = current_user.role if isinstance(current_user.role, str) else current_user.role.value
    if user_role == "manager" and current_user not in cafe.managers:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    
    if not cafe.work_start_time or not cafe.work_end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="У кафе не указано рабочее время. Укажите work_start_time и work_end_time"
        )
    
    duration_minutes = cafe.slot_duration_minutes or 60
    
    # Генерируем слоты
    slots = []
    current_time = cafe.work_start_time
    end_time = cafe.work_end_time
    
    while current_time < end_time:
        # Вычисляем время окончания слота
        current_datetime = datetime.combine(date.today(), current_time)
        end_datetime = current_datetime + timedelta(minutes=duration_minutes)
        slot_end_time = end_datetime.time()
        
        # Если слот выходит за пределы рабочего времени, обрезаем
        if slot_end_time > end_time:
            slot_end_time = end_time
        
        # Проверяем, не существует ли уже такой слот
        existing = db.query(Slot).filter(
            Slot.cafe_id == cafe_id,
            Slot.start_time == current_time,
            Slot.end_time == slot_end_time
        ).first()
        
        if not existing:
            new_slot = Slot(
                cafe_id=cafe_id,
                start_time=current_time,
                end_time=slot_end_time
            )
            db.add(new_slot)
            slots.append(new_slot)
        
        # Переходим к следующему слоту
        current_datetime = end_datetime
        current_time = current_datetime.time()
    
    db.commit()
    
    # Обновляем объекты для возврата
    for slot in slots:
        db.refresh(slot)
    
    logger.info(f"User {current_user.username} (id: {current_user.id}) generated {len(slots)} slots for cafe {cafe.name}")
    
    return slots


@router.patch("/{slot_id}", response_model=SlotResponse)
async def update_slot(
    slot_id: int,
    slot_data: SlotUpdate,
    cafe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager"))
):
    """Обновление слота"""
    slot = db.query(Slot).filter(Slot.id == slot_id).first()
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Слот не найден"
        )
    
    cafe = db.query(Cafe).filter(Cafe.id == slot.cafe_id).first()
    
    # Проверка прав менеджера
    user_role = current_user.role if isinstance(current_user.role, str) else current_user.role.value
    if user_role == "manager" and current_user not in cafe.managers:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    
    # Проверка cafe_id если он обновляется
    if slot_data.cafe_id is not None:
        new_cafe = db.query(Cafe).filter(Cafe.id == slot_data.cafe_id).first()
        if not new_cafe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Кафе не найдено"
            )
        if user_role == "manager" and current_user not in new_cafe.managers:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав"
            )
    
    # Проверка корректности времени
    start_time = slot_data.start_time if slot_data.start_time is not None else slot.start_time
    end_time = slot_data.end_time if slot_data.end_time is not None else slot.end_time
    if start_time >= end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Время начала должно быть раньше времени окончания"
        )
    
    update_data = slot_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(slot, field, value)
    
    db.commit()
    db.refresh(slot)
    
    logger.info(f"User {current_user.username} (id: {current_user.id}) updated slot {slot.id}")
    
    return slot


@router.delete("/{slot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_slot(
    slot_id: int,
    cafe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager"))
):
    """Удаление слота (деактивация)"""
    slot = db.query(Slot).filter(Slot.id == slot_id).first()
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Слот не найден"
        )
    
    cafe = db.query(Cafe).filter(Cafe.id == slot.cafe_id).first()
    
    # Проверка прав менеджера
    user_role = current_user.role if isinstance(current_user.role, str) else current_user.role.value
    if user_role == "manager" and current_user not in cafe.managers:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    
    # Деактивируем слот вместо удаления
    slot.active = False
    db.commit()
    
    logger.info(f"User {current_user.username} (id: {current_user.id}) deleted (deactivated) slot {slot.id}")
