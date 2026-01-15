from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.cafe import Cafe
from app.models.user import User
from app.schemas.cafe import CafeCreate, CafeUpdate, CafeResponse
from app.core.auth import get_current_active_user, require_role
from app.utils.logger import logger

router = APIRouter(prefix="/cafes", tags=["Кафе"])


@router.get("", response_model=List[CafeResponse])
async def get_cafes(
    skip: int = 0,
    limit: int = 100,
    show_all: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получение списка кафе"""
    query = db.query(Cafe)
    
    # Менеджер видит только свои кафе
    user_role = current_user.role if isinstance(current_user.role, str) else current_user.role.value
    if user_role == "manager":
        query = query.filter(Cafe.managers.any(User.id == current_user.id))
    # Пользователь видит только активные
    elif user_role == "user":
        query = query.filter(Cafe.active == True)
    # Админ видит все или только активные в зависимости от show_all
    elif not show_all:
        query = query.filter(Cafe.active == True)
    
    cafes = query.offset(skip).limit(limit).all()
    
    # Преобразование для response (соответствует OpenAPI)
    result = []
    for cafe in cafes:
        # Преобразуем managers в формат UserShortInfo
        managers_list = [
            {"id": m.id, "username": m.username, "email": m.email}
            for m in cafe.managers
        ]
        cafe_dict = {
            "id": cafe.id,
            "name": cafe.name,
            "address": cafe.address,
            "phone": cafe.phone,
            "description": cafe.description,
            "photo_id": cafe.photo,  # photo -> photo_id
            "is_active": cafe.active,  # active -> is_active
            "managers": managers_list,  # manager_ids -> managers (список объектов)
            "created_at": cafe.created_at,
            "updated_at": cafe.updated_at
        }
        result.append(CafeResponse(**cafe_dict))
    
    return result


@router.get("/{cafe_id}", response_model=CafeResponse)
async def get_cafe(
    cafe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получение кафе по ID"""
    cafe = db.query(Cafe).filter(Cafe.id == cafe_id).first()
    if not cafe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cafe not found"
        )
    
    # Менеджер может видеть только свои кафе
    user_role = current_user.role if isinstance(current_user.role, str) else current_user.role.value
    if user_role == "manager" and current_user not in cafe.managers:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Пользователь может видеть только активные кафе
    user_role = current_user.role if isinstance(current_user.role, str) else current_user.role.value
    if user_role == "user" and not cafe.active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cafe not found"
        )
    
    # Преобразуем managers в формат UserShortInfo
    managers_list = [
        {"id": m.id, "username": m.username, "email": m.email}
        for m in cafe.managers
    ]
    cafe_dict = {
        "id": cafe.id,
        "name": cafe.name,
        "address": cafe.address,
        "phone": cafe.phone,
        "description": cafe.description,
        "photo_id": cafe.photo,  # photo -> photo_id
        "is_active": cafe.active,  # active -> is_active
        "managers": managers_list,  # manager_ids -> managers (список объектов)
        "created_at": cafe.created_at,
        "updated_at": cafe.updated_at
    }
    return CafeResponse(**cafe_dict)


@router.post("", response_model=CafeResponse, status_code=status.HTTP_201_CREATED)
async def create_cafe(
    cafe_data: CafeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))  # Только админ может создавать кафе
):
    """Создание нового кафе"""
    new_cafe = Cafe(
        name=cafe_data.name,
        address=cafe_data.address,
        phone=cafe_data.phone,
        description=cafe_data.description,
        photo=cafe_data.photo_id,  # Используем photo_id из схемы
        work_start_time=cafe_data.work_start_time,
        work_end_time=cafe_data.work_end_time,
        slot_duration_minutes=cafe_data.slot_duration_minutes
    )
    
    # Добавление менеджеров (используем managers_id из схемы)
    if cafe_data.managers_id:
        managers = db.query(User).filter(User.id.in_(cafe_data.managers_id)).all()
        new_cafe.managers = managers
    
    db.add(new_cafe)
    db.commit()
    db.refresh(new_cafe)
    
    logger.info(f"User {current_user.username} (id: {current_user.id}) created cafe {new_cafe.name} (id: {new_cafe.id})")
    
    # Преобразуем managers в формат UserShortInfo
    managers_list = [
        {"id": m.id, "username": m.username, "email": m.email}
        for m in new_cafe.managers
    ]
    cafe_dict = {
        "id": new_cafe.id,
        "name": new_cafe.name,
        "address": new_cafe.address,
        "phone": new_cafe.phone,
        "description": new_cafe.description,
        "photo_id": new_cafe.photo,  # photo -> photo_id
        "is_active": new_cafe.active,  # active -> is_active
        "managers": managers_list,  # manager_ids -> managers (список объектов)
        "created_at": new_cafe.created_at,
        "updated_at": new_cafe.updated_at
    }
    return CafeResponse(**cafe_dict)


@router.patch("/{cafe_id}", response_model=CafeResponse)
async def update_cafe(
    cafe_id: int,
    cafe_data: CafeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager"))
):
    """Обновление кафе"""
    cafe = db.query(Cafe).filter(Cafe.id == cafe_id).first()
    if not cafe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cafe not found"
        )
    
    # Проверка прав (менеджер может управлять только своими кафе)
    user_role = current_user.role if isinstance(current_user.role, str) else current_user.role.value
    if user_role == "manager" and current_user not in cafe.managers:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    update_data = cafe_data.model_dump(exclude_unset=True, exclude={"manager_ids"})
    
    for field, value in update_data.items():
        setattr(cafe, field, value)
    
    # Обновление менеджеров (только админ может назначать менеджеров)
    if cafe_data.manager_ids is not None:
        user_role = current_user.role if isinstance(current_user.role, str) else current_user.role.value
        if user_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Только администратор может назначать менеджеров"
            )
        managers = db.query(User).filter(User.id.in_(cafe_data.manager_ids)).all()
        cafe.managers = managers
    
    db.commit()
    db.refresh(cafe)
    
    logger.info(f"User {current_user.username} (id: {current_user.id}) updated cafe {cafe.name} (id: {cafe.id})")
    
    # Преобразуем managers в формат UserShortInfo
    managers_list = [
        {"id": m.id, "username": m.username, "email": m.email}
        for m in cafe.managers
    ]
    cafe_dict = {
        "id": cafe.id,
        "name": cafe.name,
        "address": cafe.address,
        "phone": cafe.phone,
        "description": cafe.description,
        "photo_id": cafe.photo,  # photo -> photo_id
        "is_active": cafe.active,  # active -> is_active
        "managers": managers_list,  # manager_ids -> managers (список объектов)
        "created_at": cafe.created_at,
        "updated_at": cafe.updated_at
    }
    return CafeResponse(**cafe_dict)


@router.delete("/{cafe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cafe(
    cafe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))  # Только админ может удалять кафе
):
    """Удаление кафе (деактивация)"""
    cafe = db.query(Cafe).filter(Cafe.id == cafe_id).first()
    if not cafe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cafe not found"
        )
    
    user_role = current_user.role if isinstance(current_user.role, str) else current_user.role.value
    if user_role == "manager" and current_user not in cafe.managers:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    cafe.active = False
    db.commit()
    
    logger.info(f"User {current_user.username} (id: {current_user.id}) deactivated cafe {cafe.name} (id: {cafe.id})")
    
    return None

