from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


EVENT_STATUS_PENDING = "pending"
EVENT_STATUS_REVIEWED = "reviewed"
EVENT_STATUS_IGNORED = "ignored"


class WarningEvent(Base):
    __tablename__ = "warning_events"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    title = Column(String(500), nullable=True)
    content = Column(Text, nullable=False)
    source_url = Column(String(1000), nullable=True)
    source_type = Column(String(100), nullable=True)
    publish_time = Column(DateTime, nullable=True)
    author = Column(String(200), nullable=True)
    forward_count = Column(Integer, default=0, nullable=False)
    comment_count = Column(Integer, default=0, nullable=False)
    like_count = Column(Integer, default=0, nullable=False)
    read_count = Column(Integer, default=0, nullable=False)
    propagation_score = Column(Float, default=0.0, nullable=False)

    risk_level = Column(String(20), nullable=True, index=True)
    hit_reasons = Column(JSON, default=list, nullable=True)
    suggested_tags = Column(JSON, default=list, nullable=True)
    matched_rules = Column(JSON, default=list, nullable=True)
    need_manual_review = Column(Integer, default=0, nullable=False)

    status = Column(String(20), default=EVENT_STATUS_PENDING, nullable=False, index=True)
    event_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    project = relationship("Project", back_populates="events")
    reviews = relationship("ReviewRecord", back_populates="event", cascade="all, delete-orphan")
