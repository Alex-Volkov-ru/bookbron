from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

# Association table для связи many-to-many между Dish и Cafe
cafe_dishes = Table(
    "cafe_dishes",
    Base.metadata,
    Column("dish_id", Integer, ForeignKey("dishes.id"), primary_key=True),
    Column("cafe_id", Integer, ForeignKey("cafes.id"), primary_key=True),
)


class Dish(Base):
    __tablename__ = "dishes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    photo = Column(String, nullable=True)  # UUID изображения
    price = Column(Numeric(10, 2), nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    cafes = relationship("Cafe", secondary=cafe_dishes, back_populates="dishes")
    booking_dishes = relationship("BookingDish", back_populates="dish")

