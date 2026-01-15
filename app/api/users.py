from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.auth import get_current_active_user, require_role, get_current_user
from app.core.security import get_password_hash, decode_access_token
from app.utils.logger import logger

security = HTTPBearer(auto_error=False)

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Опциональное получение текущего пользователя (для регистрации)"""
    if not credentials:
        return None
    try:
        payload = decode_access_token(credentials.credentials)
        if payload:
            user_id = int(payload.get("sub"))
            user = db.query(User).filter(User.id == user_id).first()
            if user and user.active:
                return user
    except:
        pass
    return None

router = APIRouter(prefix="/users", tags=["Пользователи"])


@router.get("", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    role: str = None,  # Фильтр по роли (admin, manager, user)
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager"))
):
    """Получение списка пользователей"""
    query = db.query(User)
    
    if active_only:
        query = query.filter(User.active == True)
    
    # Фильтр по роли (только для админа)
    user_role = current_user.role if isinstance(current_user.role, str) else current_user.role.value
    if role and user_role == "admin":
        query = query.filter(User.role == role)
    
    users = query.offset(skip).limit(limit).all()
    logger.info(f"User {current_user.username} (id: {current_user.id}) retrieved users list")
    return users


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_active_user)
):
    """Получение информации о текущем пользователе"""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Обновление информации о текущем пользователе"""
    update_data = user_data.model_dump(exclude_unset=True)
    
    # Пользователь не может менять роль и активность через /me
    update_data.pop("role", None)
    update_data.pop("active", None)
    
    # Проверка уникальности при обновлении
    if "email" in update_data:
        existing = db.query(User).filter(User.email == update_data["email"], User.id != current_user.id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    if "username" in update_data:
        existing = db.query(User).filter(User.username == update_data["username"], User.id != current_user.id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    if "phone" in update_data and update_data["phone"]:
        existing = db.query(User).filter(User.phone == update_data["phone"], User.id != current_user.id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone already registered"
            )
    
    # Хеширование пароля если он обновляется
    if "password" in update_data:
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    logger.info(f"User {current_user.username} (id: {current_user.id}) updated their profile")
    
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получение информации о пользователе по его ID"""
    # Пользователь может видеть только свою информацию, админы и менеджеры - любую
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER] and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """Регистрация нового пользователя (доступно всем, включая неавторизированных)"""
    # Если пользователь авторизирован и админ - может задать роль, иначе только user
    if current_user and current_user.role.value == "admin":
        user_role = user_data.role if user_data.role else UserRole.USER
    else:
        user_role = UserRole.USER  # Неавторизированные и обычные пользователи создают только user
    
    # Проверка уникальности
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    if user_data.username and db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    if user_data.phone and db.query(User).filter(User.phone == user_data.phone).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone already registered"
        )
    
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        phone=user_data.phone,
        tg_id=user_data.tg_id,
        password_hash=get_password_hash(user_data.password),
        role=user_role.value if isinstance(user_role, UserRole) else user_role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    if current_user:
        logger.info(f"User {current_user.username} (id: {current_user.id}) created user {new_user.username} (id: {new_user.id})")
    else:
        logger.info(f"New user registered: {new_user.username} (id: {new_user.id})")
    
    return new_user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager"))
):
    """Обновление информации о пользователе по его ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Проверка уникальности при обновлении
    update_data = user_data.model_dump(exclude_unset=True)
    
    if "email" in update_data:
        existing = db.query(User).filter(User.email == update_data["email"], User.id != user_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    if "username" in update_data:
        existing = db.query(User).filter(User.username == update_data["username"], User.id != user_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    if "phone" in update_data and update_data["phone"]:
        existing = db.query(User).filter(User.phone == update_data["phone"], User.id != user_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone already registered"
            )
    
    # Хеширование пароля если он обновляется
    if "password" in update_data:
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))
    
    # Только админ может менять роль и активность
    if current_user.role != UserRole.ADMIN:
        update_data.pop("role", None)
        update_data.pop("active", None)
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    logger.info(f"User {current_user.username} (id: {current_user.id}) updated user {user.username} (id: {user.id})")
    
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Удаление пользователя (блокировка)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.active = False
    db.commit()
    
    logger.info(f"User {current_user.username} (id: {current_user.id}) blocked user {user.username} (id: {user.id})")
    
    return None

