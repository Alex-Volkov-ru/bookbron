"""
Расписание периодических задач Celery Beat
"""
from celery.schedules import crontab

# Расписание для отправки напоминаний (каждый день в 9:00)
beat_schedule = {
    'send-booking-reminders': {
        'task': 'send_booking_reminders',
        'schedule': crontab(hour=9, minute=0),  # Каждый день в 9:00
    },
}

