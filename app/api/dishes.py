from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.dish import Dish
from app.models.cafe import Cafe
from app.models.user import User
from app.schemas.dish import DishCreate, DishUpdate, DishResponse
from app.core.auth import get_current_active_user, require_role
from app.utils.logger import logger

router = APIRouter(prefix="/dishes", tags=["Блюда"])


@router.get("", response_model=List[DishResponse])
async def get_dishes(
    cafe_id: int = None,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Получение списка блюд"""
    query = db.query(Dish)
    
    if cafe_id:
        query = query.join(Cafe.dishes).filter(Cafe.id == cafe_id)
    
    if active_only:
        query = query.filter(Dish.active == True)
    
    dishes = query.offset(skip).limit(limit).all()
    
    # Преобразование для response
    result = []
    for dish in dishes:
        dish_dict = {
            **{c.name: getattr(dish, c.name) for c in dish.__table__.columns},
            "cafe_ids": [c.id for c in dish.cafes]
        }
        result.append(DishResponse(**dish_dict))
    
    return result


@router.get("/{dish_id}", response_model=DishResponse)
async def get_dish(
    dish_id: int,
    db: Session = Depends(get_db)
):
    """Получение блюда по ID"""
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dish not found"
        )
    
    dish_dict = {
        **{c.name: getattr(dish, c.name) for c in dish.__table__.columns},
        "cafe_ids": [c.id for c in dish.cafes]
    }
    return DishResponse(**dish_dict)


@router.post("", response_model=DishResponse, status_code=status.HTTP_201_CREATED)
async def create_dish(
    dish_data: DishCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager"))
):
    """Создание нового блюда"""
    new_dish = Dish(
        name=dish_data.name,
        description=dish_data.description,
        photo=dish_data.photo,
        price=dish_data.price
    )
    
    # Добавление связи с кафе
    if dish_data.cafe_ids:
        cafes = db.query(Cafe).filter(Cafe.id.in_(dish_data.cafe_ids)).all()
        # Менеджер может привязывать только к своим кафе
        if current_user.role.value == "manager":
            user_cafe_ids = [c.id for c in current_user.managed_cafes]
            for cafe in cafes:
                if cafe.id not in user_cafe_ids:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"You can only assign dishes to your cafes"
                    )
        new_dish.cafes = cafes
    
    db.add(new_dish)
    db.commit()
    db.refresh(new_dish)
    
    logger.info(f"User {current_user.username} (id: {current_user.id}) created dish {new_dish.name} (id: {new_dish.id})")
    
    dish_dict = {
        **{c.name: getattr(new_dish, c.name) for c in new_dish.__table__.columns},
        "cafe_ids": [c.id for c in new_dish.cafes]
    }
    return DishResponse(**dish_dict)


@router.patch("/{dish_id}", response_model=DishResponse)
async def update_dish(
    dish_id: int,
    dish_data: DishUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager"))
):
    """Обновление блюда"""
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dish not found"
        )
    
    # Менеджер может обновлять только блюда своих кафе
    if current_user.role.value == "manager":
        user_cafe_ids = [c.id for c in current_user.managed_cafes]
        dish_cafe_ids = [c.id for c in dish.cafes]
        if not any(cid in user_cafe_ids for cid in dish_cafe_ids):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions - you can only update dishes for your cafes"
            )
    
    update_data = dish_data.model_dump(exclude_unset=True, exclude={"cafe_ids"})
    
    for field, value in update_data.items():
        setattr(dish, field, value)
    
    # Обновление связи с кафе
    if dish_data.cafe_ids is not None:
        cafes = db.query(Cafe).filter(Cafe.id.in_(dish_data.cafe_ids)).all()
        # Менеджер может привязывать только к своим кафе
        if current_user.role.value == "manager":
            user_cafe_ids = [c.id for c in current_user.managed_cafes]
            for cafe in cafes:
                if cafe.id not in user_cafe_ids:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"You can only assign dishes to your cafes"
                    )
        dish.cafes = cafes
    
    db.commit()
    db.refresh(dish)
    
    logger.info(f"User {current_user.username} (id: {current_user.id}) updated dish {dish.name} (id: {dish.id})")
    
    dish_dict = {
        **{c.name: getattr(dish, c.name) for c in dish.__table__.columns},
        "cafe_ids": [c.id for c in dish.cafes]
    }
    return DishResponse(**dish_dict)


@router.delete("/{dish_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dish(
    dish_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager"))
):
    """Удаление блюда (деактивация)"""
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dish not found"
        )
    
    # Менеджер может удалять только блюда своих кафе
    if current_user.role.value == "manager":
        user_cafe_ids = [c.id for c in current_user.managed_cafes]
        dish_cafe_ids = [c.id for c in dish.cafes]
        if not any(cid in user_cafe_ids for cid in dish_cafe_ids):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions - you can only delete dishes for your cafes"
            )
    
    dish.active = False
    db.commit()
    
    logger.info(f"User {current_user.username} (id: {current_user.id}) deactivated dish {dish.name} (id: {dish.id})")
    
    return None

