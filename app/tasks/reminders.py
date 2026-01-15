from datetime import datetime, timedelta
from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.booking import Booking, BookingStatus
from app.utils.logger import logger


@celery_app.task(name="send_booking_reminders")
def send_booking_reminders():
    """Отправка напоминаний о предстоящих бронированиях"""
    db = SessionLocal()
    try:
        # Находим бронирования на завтра, которым еще не отправляли напоминание
        tomorrow = datetime.now().date() + timedelta(days=1)
        
        bookings = db.query(Booking).filter(
            Booking.date == tomorrow,
            Booking.status == BookingStatus.CONFIRMED,
            Booking.reminder_sent == False,
            Booking.active == True
        ).all()
        
        for booking in bookings:
            try:
                # Здесь должна быть реальная отправка напоминания (email, telegram и т.д.)
                # Для примера просто логируем
                logger.info(
                    f"Reminder sent to user {booking.user_id} "
                    f"about booking {booking.id} on {booking.date}"
                )
                
                booking.reminder_sent = True
                db.commit()
                
            except Exception as e:
                logger.error(f"Error sending reminder for booking {booking.id}: {str(e)}")
        
        logger.info(f"Sent reminders for {len(bookings)} bookings")
        
    except Exception as e:
        logger.error(f"Error in send_booking_reminders task: {str(e)}")
    finally:
        db.close()


@celery_app.task(name="send_booking_reminder")
def send_booking_reminder(booking_id: int):
    """Отправка напоминания о конкретном бронировании"""
    db = SessionLocal()
    try:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            logger.error(f"Booking {booking_id} not found for reminder")
            return
        
        if booking.reminder_sent:
            logger.info(f"Reminder already sent for booking {booking_id}")
            return
        
        # Здесь должна быть реальная отправка напоминания
        logger.info(
            f"Reminder sent to user {booking.user_id} "
            f"about booking {booking.id} on {booking.date}"
        )
        
        booking.reminder_sent = True
        db.commit()
        
    except Exception as e:
        logger.error(f"Error sending reminder for booking {booking_id}: {str(e)}")
    finally:
        db.close()

