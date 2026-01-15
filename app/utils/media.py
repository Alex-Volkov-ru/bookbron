import uuid
import os
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException
from PIL import Image
import io
from app.config import settings

MAX_SIZE_MB = settings.MAX_IMAGE_SIZE_MB
MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024
MEDIA_DIR = Path(settings.MEDIA_DIR)
MEDIA_DIR.mkdir(parents=True, exist_ok=True)


def generate_image_id() -> str:
    """Генерация UUID4 для ID изображения"""
    return str(uuid.uuid4())


async def save_image(file: UploadFile) -> str:
    """Сохранение изображения и возврат его ID"""
    # Проверка типа файла
    if file.content_type not in ["image/jpeg", "image/jpg", "image/png"]:
        raise HTTPException(
            status_code=400,
            detail="Only JPG and PNG images are supported"
        )
    
    # Чтение файла
    contents = await file.read()
    
    # Проверка размера
    if len(contents) > MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"Image size exceeds {MAX_SIZE_MB}MB limit"
        )
    
    # Генерация ID
    image_id = generate_image_id()
    
    # Конвертация в JPG
    try:
        image = Image.open(io.BytesIO(contents))
        # Конвертация RGBA в RGB если необходимо
        if image.mode in ("RGBA", "LA", "P"):
            rgb_image = Image.new("RGB", image.size, (255, 255, 255))
            if image.mode == "P":
                image = image.convert("RGBA")
            rgb_image.paste(image, mask=image.split()[-1] if image.mode in ("RGBA", "LA") else None)
            image = rgb_image
        elif image.mode != "RGB":
            image = image.convert("RGB")
        
        # Сохранение в JPG
        image_path = MEDIA_DIR / f"{image_id}.jpg"
        image.save(image_path, "JPEG", quality=95)
        
        return image_id
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error processing image: {str(e)}"
        )


def get_image_path(image_id: str) -> Optional[Path]:
    """Получение пути к изображению по ID"""
    image_path = MEDIA_DIR / f"{image_id}.jpg"
    if image_path.exists():
        return image_path
    return None


def delete_image(image_id: str) -> bool:
    """Удаление изображения"""
    image_path = MEDIA_DIR / f"{image_id}.jpg"
    if image_path.exists():
        image_path.unlink()
        return True
    return False

