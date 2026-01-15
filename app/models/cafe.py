from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Table, ForeignKey, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

# Association table для связи many-to-many между Cafe и User (менеджеры)
cafe_managers = Table(
    "cafe_managers",
    Base.metadata,
    Column("cafe_id", Integer, ForeignKey("cafes.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
)


class Cafe(Base):
    __tablename__ = "cafes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    address = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    photo = Column(String, nullable=True)  # UUID изображения
    active = Column(Boolean, default=True, nullable=False)
    work_start_time = Column(Time, nullable=True)  # Время начала работы (например, 09:00)
    work_end_time = Column(Time, nullable=True)  # Время окончания работы (например, 22:00)
    slot_duration_minutes = Column(Integer, nullable=True, default=60)  # Длительность слота в минутах (30, 40, 60)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    managers = relationship("User", secondary=cafe_managers, back_populates="managed_cafes")
    tables = relationship("Table", back_populates="cafe")
    slots = relationship("Slot", back_populates="cafe")
    bookings = relationship("Booking", back_populates="cafe")
    dishes = relationship("Dish", back_populates="cafes", secondary="cafe_dishes")
    actions = relationship("Action", back_populates="cafes", secondary="cafe_actions")

