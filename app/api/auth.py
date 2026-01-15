from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.models.user import User
from app.schemas.token import Token, AuthData
from app.schemas.user import UserResponse
from app.core.security import verify_password, create_access_token
from app.core.auth import get_current_user
from app.config import settings
from app.utils.logger import logger

router = APIRouter(prefix="/auth", tags=["Аутентификация"])


@router.post("/login", response_model=Token)
async def login(
    auth_data: AuthData,
    db: Session = Depends(get_db)
):
    """Получение токена авторизации"""
    user = None
    
    # Пытаемся найти пользователя по email или phone
    user = db.query(User).filter(
        (User.email == auth_data.login) | (User.phone == auth_data.login)
    ).first()
    
    if not user or not verify_password(auth_data.password, user.password_hash):
        logger.warning(f"Failed login attempt for {auth_data.login}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Неверные имя пользователя или пароль",
        )
    
    if not user.active:
        logger.warning(f"Login attempt for blocked user: {user.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is blocked"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    logger.info(f"User {user.username} (id: {user.id}) logged in successfully")
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login/form", response_model=Token)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Аутентификация через OAuth2 form (для Swagger UI)"""
    user = db.query(User).filter(
        (User.email == form_data.username) | (User.phone == form_data.username)
    ).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is blocked"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}



