from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.utils.db import Base


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)  # deadline_approaching, deadline_overdue, task_completed, etc.
    title = Column(String, nullable=False)
    message = Column(Text, nullable=True)
    is_read = Column(Boolean, default=False)
    priority = Column(String, default="low")  # low, medium, high
    todo_id = Column(Integer, ForeignKey("todos.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    todo = relationship("Todo", back_populates="notifications")
