"""
Скрипт для создания пользователей (админ, менеджер, пользователь)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from app.utils.logger import logger

def create_user(username: str, email: str, password: str, role: str = "user", phone: str = None):
    """Создание пользователя"""
    db: Session = SessionLocal()
    try:
        # Проверка существования
        existing = db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first()
        
        if existing:
            logger.warning(f"User with email {email} or username {username} already exists")
            return existing
        
        # Создание пользователя
        new_user = User(
            username=username,
            email=email,
            phone=phone,
            password_hash=get_password_hash(password),
            role=role,  # "admin", "manager", "user"
            active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"Created user: {username} ({email}) with role: {role}")
        return new_user
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Создание пользователя')
    parser.add_argument('--username', required=True, help='Имя пользователя')
    parser.add_argument('--email', required=True, help='Email')
    parser.add_argument('--password', required=True, help='Пароль')
    parser.add_argument('--role', choices=['admin', 'manager', 'user'], default='user', help='Роль')
    parser.add_argument('--phone', help='Телефон')
    
    args = parser.parse_args()
    
    user = create_user(
        username=args.username,
        email=args.email,
        password=args.password,
        role=args.role,
        phone=args.phone
    )
    
    print(f"✅ Пользователь создан: {user.username} ({user.email}) с ролью: {user.role}")

