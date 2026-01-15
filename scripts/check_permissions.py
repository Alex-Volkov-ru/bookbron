"""
Скрипт для проверки прав пользователей
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models.user import User
from app.core.auth import require_role

def check_user_permissions():
    """Проверка прав пользователей"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        
        print("=" * 80)
        print("ПРОВЕРКА ПРАВ ПОЛЬЗОВАТЕЛЕЙ")
        print("=" * 80)
        print()
        
        for user in users:
            print(f"Пользователь: {user.username} ({user.email})")
            print(f"  ID: {user.id}")
            print(f"  Роль: \"{user.role}\" (тип: {type(user.role).__name__})")
            print(f"  Активен: {user.active}")
            
            # Проверка логики require_role
            user_role = user.role if isinstance(user.role, str) else user.role.value
            print(f"  user_role после проверки: \"{user_role}\"")
            
            # Проверка прав
            can_create_cafe = user_role in ["admin"]
            can_update_cafe = user_role in ["admin", "manager"]
            can_delete_cafe = user_role in ["admin"]
            
            print(f"  Может создавать кафе: {can_create_cafe}")
            print(f"  Может обновлять кафе: {can_update_cafe}")
            print(f"  Может удалять кафе: {can_delete_cafe}")
            print()
        
        print("=" * 80)
        print("ВЫВОДЫ:")
        print("-" * 80)
        print("1. Только АДМИН может создавать кафе (require_role('admin'))")
        print("2. АДМИН и МЕНЕДЖЕР могут обновлять кафе (require_role('admin', 'manager'))")
        print("3. Только АДМИН может удалять кафе (require_role('admin'))")
        print("=" * 80)
        
    finally:
        db.close()

if __name__ == "__main__":
    check_user_permissions()

