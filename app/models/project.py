from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    client_name = Column(String(200), nullable=False, index=True)
    industry = Column(String(100), nullable=True)
    region = Column(String(200), nullable=True)
    key_entities = Column(JSON, default=list, nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="active", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    rules = relationship("WarningRule", back_populates="project", cascade="all, delete-orphan")
    events = relationship("WarningEvent", back_populates="project", cascade="all, delete-orphan")
