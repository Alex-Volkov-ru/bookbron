from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from app.database import get_db
from app.models.user import User
from app.core.auth import require_role
from app.utils.media import save_image, get_image_path
from app.utils.logger import logger

router = APIRouter(prefix="/media", tags=["Медиа"])


@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role("admin", "manager"))
):
    """Загрузка изображения (только для админов и менеджеров)"""
    try:
        image_id = await save_image(file)
        logger.info(f"User {current_user.username} (id: {current_user.id}) uploaded image {image_id}")
        return {"image_id": image_id}
    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{image_id}")
async def get_image(
    image_id: str,
    db: Session = Depends(get_db)
):
    """Получение изображения по ID"""
    image_path = get_image_path(image_id)
    
    if not image_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    return FileResponse(
        path=image_path,
        media_type="image/jpeg",
        filename=f"{image_id}.jpg"
    )

