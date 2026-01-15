from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
from app.api import auth, users, cafes, tables, slots, booking, media, dishes, actions
from app.core.auth import get_current_user
from app.utils.logger import logger
from app.config import settings

app = FastAPI(
    title="Система бронирования мест в кафе",
    description="API для управления бронированием мест в кафе",
    version="0.0.4",
    docs_url="/docs",  # Стандартный Swagger
    redoc_url=None  # Отключаем встроенный ReDoc, используем кастомный
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(cafes.router)
app.include_router(tables.router)
app.include_router(slots.router)
app.include_router(booking.router)
app.include_router(media.router)
app.include_router(dishes.router)
app.include_router(actions.router)

@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    logger.info("Application started")
    logger.info(f"Database URL: {settings.DATABASE_URL}")
    logger.info(f"Media directory: {settings.MEDIA_DIR}")


@app.on_event("shutdown")
async def shutdown_event():
    """Очистка при остановке"""
    logger.info("Application shutdown")


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Booking System API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    return {"status": "healthy"}


@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_json():
    """Возвращает OpenAPI спецификацию в формате JSON"""
    from fastapi.responses import Response
    openapi_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "openapi.json")
    if os.path.exists(openapi_path):
        with open(openapi_path, "r", encoding="utf-8") as f:
            content = f.read()
        return Response(
            content=content,
            media_type="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET",
                "Access-Control-Allow-Headers": "*",
            }
        )
    # Если файл не найден, возвращаем стандартную спецификацию FastAPI
    return app.openapi()


@app.get("/swagger", response_class=HTMLResponse, include_in_schema=False)
async def get_swagger_html():
    """Возвращает HTML страницу Swagger UI"""
    html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "index_swagger.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Swagger UI not found</h1>")


@app.get("/redoc", response_class=HTMLResponse, include_in_schema=False)
async def get_redoc_html():
    """Возвращает HTML страницу ReDoc"""
    html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "index_redoc.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>ReDoc not found</h1>")

