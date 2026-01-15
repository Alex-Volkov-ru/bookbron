from sqlalchemy import Column, Integer, Date, ForeignKey, String, Text, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    cafe_id = Column(Integer, ForeignKey("cafes.id"), nullable=False, index=True)
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=False, index=True)
    slot_id = Column(Integer, ForeignKey("slots.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    status = Column(SQLEnum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    note = Column(Text, nullable=True)
    reminder_sent = Column(Boolean, default=False, nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="bookings")
    cafe = relationship("Cafe", back_populates="bookings")
    table = relationship("Table", back_populates="bookings")
    slot = relationship("Slot", back_populates="bookings")
    dishes = relationship("BookingDish", back_populates="booking", cascade="all, delete-orphan")

