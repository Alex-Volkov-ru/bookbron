from sqlalchemy import Column, Integer, ForeignKey, Numeric, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class BookingDish(Base):
    __tablename__ = "booking_dishes"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False, index=True)
    dish_id = Column(Integer, ForeignKey("dishes.id"), nullable=False, index=True)
    quantity = Column(Integer, default=1, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)  # Цена на момент заказа
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    booking = relationship("Booking", back_populates="dishes")
    dish = relationship("Dish", back_populates="booking_dishes")

