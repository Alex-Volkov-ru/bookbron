"""
Скрипт для инициализации базы данных с начальными данными
Создает администратора, менеджера и тестового пользователя
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from app.utils.logger import logger

def create_user_if_not_exists(db: Session, username: str, email: str, password: str, role: str, phone: str = None):
    """Создание пользователя если его нет"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            username=username,
            email=email,
            phone=phone,
            password_hash=get_password_hash(password),
            role=role,
            active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Created {role} user: {username} ({email})")
        return user
    else:
        logger.info(f"{role.capitalize()} user already exists: {username} ({email})")
        return user

def init_db():
    """Инициализация БД с начальными данными"""
    db: Session = SessionLocal()
    try:
        # Создание администратора
        admin = create_user_if_not_exists(
            db=db,
            username="admin",
            email="admin@example.com",
            password="admin",
            role="admin"
        )
        
        # Создание менеджера
        manager = create_user_if_not_exists(
            db=db,
            username="manager",
            email="manager@example.com",
            password="manager",
            role="manager",
            phone="+79991234567"
        )
        
        # Создание тестового пользователя
        user = create_user_if_not_exists(
            db=db,
            username="user",
            email="user@example.com",
            password="user",
            role="user",
            phone="+79991234568"
        )
        
        logger.info("Database initialized successfully")
        logger.info(f"Admin: admin@example.com / admin")
        logger.info(f"Manager: manager@example.com / manager")
        logger.info(f"User: user@example.com / user")
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_db()

