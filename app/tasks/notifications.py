from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.booking import Booking
from app.models.cafe import Cafe
from app.models.user import User, UserRole
from app.utils.logger import logger


@celery_app.task(name="send_booking_notification")
def send_booking_notification(booking_id: int, action: str):
    """Отправка уведомления администратору о бронировании"""
    db = SessionLocal()
    try:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            logger.error(f"Booking {booking_id} not found for notification")
            return
        
        cafe = db.query(Cafe).filter(Cafe.id == booking.cafe_id).first()
        if not cafe:
            logger.error(f"Cafe {booking.cafe_id} not found for notification")
            return
        
        # Получение менеджеров кафе и админов
        managers = cafe.managers
        admins = db.query(User).filter(User.role == UserRole.ADMIN, User.active == True).all()
        
        recipients = list(set(managers + admins))
        
        # Здесь должна быть реальная отправка уведомления (email, telegram и т.д.)
        # Для примера просто логируем
        for recipient in recipients:
            logger.info(
                f"Notification sent to {recipient.username} (id: {recipient.id}) "
                f"about booking {booking_id} {action} by user {booking.user_id}"
            )
        
        logger.info(
            f"Booking notification sent: booking_id={booking_id}, action={action}, "
            f"recipients={len(recipients)}"
        )
        
    except Exception as e:
        logger.error(f"Error sending booking notification: {str(e)}")
    finally:
        db.close()

