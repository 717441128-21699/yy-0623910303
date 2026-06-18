from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


REVIEW_RESULT_CONFIRM = "confirm"
REVIEW_RESULT_FALSE_POSITIVE = "false_positive"
REVIEW_RESULT_UPGRADE = "upgrade"
REVIEW_RESULT_DOWNGRADE = "downgrade"


class ReviewRecord(Base):
    __tablename__ = "review_records"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("warning_events.id"), nullable=False, index=True)
    reviewer = Column(String(100), nullable=False)
    review_result = Column(String(50), nullable=False)
    corrected_risk_level = Column(String(20), nullable=True)
    corrected_tags = Column(JSON, default=list, nullable=True)
    remarks = Column(JSON, default=list, nullable=True)
    remark_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    event = relationship("WarningEvent", back_populates="reviews")
