import sys
from loguru import logger
from app.config import settings

# Удаление стандартного обработчика
logger.remove()

# Добавление обработчика для консоли
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
    level=settings.LOG_LEVEL,
    colorize=True
)

# Добавление обработчика для файла
logger.add(
    settings.LOG_FILE,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
    level=settings.LOG_LEVEL,
    rotation=settings.LOG_ROTATION,
    retention=settings.LOG_RETENTION,
    compression="zip"
)

