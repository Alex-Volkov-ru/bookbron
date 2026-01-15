from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.table import Table
from app.models.cafe import Cafe
from app.models.user import User
from app.schemas.table import TableCreate, TableUpdate, TableResponse, TableBulkCreate
from app.core.auth import get_current_active_user, require_role
from app.utils.logger import logger

router = APIRouter(prefix="/cafe/{cafe_id}/tables", tags=["Столы"])


@router.get("", response_model=List[TableResponse])
async def get_tables(
    cafe_id: int,
    show_all: bool = False,
    active_only: bool = False,
    booking_date: str = None,  # Дата для фильтрации забронированных столов
    slot_id: int = None,  # ID слота для фильтрации
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Список столов в кафе"""
    from datetime import date
    from app.models.booking import Booking, BookingStatus
    
    # Проверка существования кафе
    cafe = db.query(Cafe).filter(Cafe.id == cafe_id).first()
    if not cafe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Кафе не найдено"
        )
    
    query = db.query(Table).filter(Table.cafe_id == cafe_id)
    
    # Фильтрация по active_only (приоритет над show_all)
    if active_only:
        query = query.filter(Table.active == True)
    elif not show_all:
        # Для пользователей показываем только активные, для админов и менеджеров - все если show_all=True
        user_role = current_user.role if isinstance(current_user.role, str) else current_user.role.value
        if user_role not in ["admin", "manager"]:
            query = query.filter(Table.active == True)
    
    tables = query.all()
    
    # Для пользователей фильтруем забронированные столы на указанную дату и слот
    user_role = current_user.role if isinstance(current_user.role, str) else current_user.role.value
    if user_role == "user" and booking_date and slot_id:
        try:
            booking_date_obj = date.fromisoformat(booking_date)
            # Получаем ID забронированных столов
            booked_table_ids = db.query(Booking.table_id).filter(
                Booking.cafe_id == cafe_id,
                Booking.slot_id == slot_id,
                Booking.date == booking_date_obj,
                Booking.status != BookingStatus.CANCELLED,
                Booking.active == True
            ).distinct().all()
            booked_ids = [row[0] for row in booked_table_ids]
            # Фильтруем столы, исключая забронированные
            tables = [t for t in tables if t.id not in booked_ids]
        except ValueError:
            pass  # Неверный формат даты, возвращаем все столы
    
    return tables


@router.get("/{table_id}", response_model=TableResponse)
async def get_table(
    table_id: int,
    db: Session = Depends(get_db)
):
    """Получение стола по ID"""
    table = db.query(Table).filter(Table.id == table_id).first()
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Стол не найден"
        )
    return table


@router.post("", response_model=TableResponse, status_code=status.HTTP_201_CREATED)
async def create_table(
    cafe_id: int,
    table_data: TableCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager"))
):
    """Новый стол в кафе"""
    # Проверка существования кафе
    cafe = db.query(Cafe).filter(Cafe.id == cafe_id).first()
    if not cafe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cafe not found"
        )
    
    # Проверка прав менеджера
    user_role = current_user.role if isinstance(current_user.role, str) else current_user.role.value
    if user_role == "manager" and current_user not in cafe.managers:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    
    new_table = Table(
        cafe_id=cafe_id,
        seats_count=table_data.seats_count,
        description=table_data.description
    )
    
    db.add(new_table)
    db.commit()
    db.refresh(new_table)
    
    logger.info(f"User {current_user.username} (id: {current_user.id}) created table {new_table.id} for cafe {cafe.name}")
    
    return new_table


@router.patch("/{table_id}", response_model=TableResponse)
async def update_table(
    table_id: int,
    table_data: TableUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager"))
):
    """Обновление стола"""
    table = db.query(Table).filter(Table.id == table_id).first()
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Стол не найден"
        )
    
    cafe = db.query(Cafe).filter(Cafe.id == table.cafe_id).first()
    
    # Проверка прав менеджера
    user_role = current_user.role if isinstance(current_user.role, str) else current_user.role.value
    if user_role == "manager" and current_user not in cafe.managers:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    
    # Проверка cafe_id если он обновляется
    if table_data.cafe_id is not None:
        new_cafe = db.query(Cafe).filter(Cafe.id == table_data.cafe_id).first()
        if not new_cafe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cafe not found"
            )
        user_role = current_user.role if isinstance(current_user.role, str) else current_user.role.value
        if user_role == "manager" and current_user not in new_cafe.managers:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав"
            )
    
    update_data = table_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(table, field, value)
    
    db.commit()
    db.refresh(table)
    
    logger.info(f"User {current_user.username} (id: {current_user.id}) updated table {table.id}")
    
    return table


@router.delete("/{table_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_table(
    table_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager"))
):
    """Удаление стола (деактивация)"""
    table = db.query(Table).filter(Table.id == table_id).first()
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Стол не найден"
        )
    
    cafe = db.query(Cafe).filter(Cafe.id == table.cafe_id).first()
    
    if current_user.role.value == "manager" and current_user not in cafe.managers:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    
    table.active = False
    db.commit()
    
    logger.info(f"User {current_user.username} (id: {current_user.id}) deactivated table {table.id}")
    
    return None



@router.post("/bulk", response_model=List[TableResponse], status_code=status.HTTP_201_CREATED)
async def create_tables_bulk(
    cafe_id: int,
    bulk_data: TableBulkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager"))
):
    """Массовое создание столов (например, 20 столов по 2 места)"""
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
    
    # Создаем столы
    tables = []
    for i in range(bulk_data.count):
        new_table = Table(
            cafe_id=cafe_id,
            seats_count=bulk_data.seats_count,
            description=bulk_data.description or f"Стол на {bulk_data.seats_count} {'место' if bulk_data.seats_count == 1 else 'мест'}"
        )
        db.add(new_table)
        tables.append(new_table)
    
    db.commit()
    
    # Обновляем объекты для возврата
    for table in tables:
        db.refresh(table)
    
    logger.info(f"User {current_user.username} (id: {current_user.id}) created {bulk_data.count} tables for cafe {cafe.name}")
    
    return tables
