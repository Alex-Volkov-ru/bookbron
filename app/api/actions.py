from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.action import Action
from app.models.cafe import Cafe
from app.models.user import User
from app.schemas.action import ActionCreate, ActionUpdate, ActionResponse
from app.core.auth import get_current_active_user, require_role
from app.utils.logger import logger

router = APIRouter(prefix="/actions", tags=["Акции"])


@router.get("", response_model=List[ActionResponse])
async def get_actions(
    cafe_id: int = None,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Получение списка акций"""
    query = db.query(Action)
    
    if cafe_id:
        query = query.join(Cafe.actions).filter(Cafe.id == cafe_id)
    
    if active_only:
        query = query.filter(Action.active == True)
    
    actions = query.offset(skip).limit(limit).all()
    
    # Преобразование для response
    result = []
    for action in actions:
        action_dict = {
            **{c.name: getattr(action, c.name) for c in action.__table__.columns},
            "cafe_ids": [c.id for c in action.cafes]
        }
        result.append(ActionResponse(**action_dict))
    
    return result


@router.get("/{action_id}", response_model=ActionResponse)
async def get_action(
    action_id: int,
    db: Session = Depends(get_db)
):
    """Получение акции по ID"""
    action = db.query(Action).filter(Action.id == action_id).first()
    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found"
        )
    
    action_dict = {
        **{c.name: getattr(action, c.name) for c in action.__table__.columns},
        "cafe_ids": [c.id for c in action.cafes]
    }
    return ActionResponse(**action_dict)


@router.post("", response_model=ActionResponse, status_code=status.HTTP_201_CREATED)
async def create_action(
    action_data: ActionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager"))
):
    """Создание новой акции"""
    new_action = Action(
        description=action_data.description,
        photo=action_data.photo
    )
    
    # Добавление связи с кафе
    if action_data.cafe_ids:
        cafes = db.query(Cafe).filter(Cafe.id.in_(action_data.cafe_ids)).all()
        # Менеджер может привязывать только к своим кафе
        if current_user.role.value == "manager":
            user_cafe_ids = [c.id for c in current_user.managed_cafes]
            for cafe in cafes:
                if cafe.id not in user_cafe_ids:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"You can only assign actions to your cafes"
                    )
        new_action.cafes = cafes
    
    db.add(new_action)
    db.commit()
    db.refresh(new_action)
    
    logger.info(f"User {current_user.username} (id: {current_user.id}) created action {new_action.id}")
    
    action_dict = {
        **{c.name: getattr(new_action, c.name) for c in new_action.__table__.columns},
        "cafe_ids": [c.id for c in new_action.cafes]
    }
    return ActionResponse(**action_dict)


@router.patch("/{action_id}", response_model=ActionResponse)
async def update_action(
    action_id: int,
    action_data: ActionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager"))
):
    """Обновление акции"""
    action = db.query(Action).filter(Action.id == action_id).first()
    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found"
        )
    
    # Менеджер может обновлять только акции своих кафе
    if current_user.role.value == "manager":
        user_cafe_ids = [c.id for c in current_user.managed_cafes]
        action_cafe_ids = [c.id for c in action.cafes]
        if not any(cid in user_cafe_ids for cid in action_cafe_ids):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions - you can only update actions for your cafes"
            )
    
    update_data = action_data.model_dump(exclude_unset=True, exclude={"cafe_ids"})
    
    for field, value in update_data.items():
        setattr(action, field, value)
    
    # Обновление связи с кафе
    if action_data.cafe_ids is not None:
        cafes = db.query(Cafe).filter(Cafe.id.in_(action_data.cafe_ids)).all()
        # Менеджер может привязывать только к своим кафе
        if current_user.role.value == "manager":
            user_cafe_ids = [c.id for c in current_user.managed_cafes]
            for cafe in cafes:
                if cafe.id not in user_cafe_ids:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"You can only assign actions to your cafes"
                    )
        action.cafes = cafes
    
    db.commit()
    db.refresh(action)
    
    logger.info(f"User {current_user.username} (id: {current_user.id}) updated action {action.id}")
    
    action_dict = {
        **{c.name: getattr(action, c.name) for c in action.__table__.columns},
        "cafe_ids": [c.id for c in action.cafes]
    }
    return ActionResponse(**action_dict)


@router.delete("/{action_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_action(
    action_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager"))
):
    """Удаление акции (деактивация)"""
    action = db.query(Action).filter(Action.id == action_id).first()
    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found"
        )
    
    # Менеджер может удалять только акции своих кафе
    if current_user.role.value == "manager":
        user_cafe_ids = [c.id for c in current_user.managed_cafes]
        action_cafe_ids = [c.id for c in action.cafes]
        if not any(cid in user_cafe_ids for cid in action_cafe_ids):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions - you can only delete actions for your cafes"
            )
    
    action.active = False
    db.commit()
    
    logger.info(f"User {current_user.username} (id: {current_user.id}) deactivated action {action.id}")
    
    return None

