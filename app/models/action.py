from sqlalchemy import Column, Integer, Text, String, Boolean, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

# Association table для связи many-to-many между Action и Cafe
cafe_actions = Table(
    "cafe_actions",
    Base.metadata,
    Column("action_id", Integer, ForeignKey("actions.id"), primary_key=True),
    Column("cafe_id", Integer, ForeignKey("cafes.id"), primary_key=True),
)


class Action(Base):
    __tablename__ = "actions"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    photo = Column(String, nullable=True)  # UUID изображения
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    cafes = relationship("Cafe", secondary=cafe_actions, back_populates="actions")

