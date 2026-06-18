from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


RULE_TYPE_POLICY_DISPUTE = "policy_dispute"
RULE_TYPE_LEADER_RELATED = "leader_related"
RULE_TYPE_GOVERNANCE_COMPLAINT = "governance_complaint"
RULE_TYPE_PUBLIC_EMERGENCY = "public_emergency"
RULE_TYPE_CUSTOM = "custom"

RISK_LEVEL_LOW = "low"
RISK_LEVEL_MEDIUM = "medium"
RISK_LEVEL_HIGH = "high"
RISK_LEVEL_CRITICAL = "critical"


class WarningRule(Base):
    __tablename__ = "warning_rules"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    rule_type = Column(String(50), nullable=False, index=True)
    keywords = Column(JSON, default=list, nullable=False)
    risk_level = Column(String(20), nullable=False, default=RISK_LEVEL_MEDIUM)
    weight = Column(Integer, default=1, nullable=False)
    suggested_tags = Column(JSON, default=list, nullable=True)
    description = Column(Text, nullable=True)
    is_enabled = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    project = relationship("Project", back_populates="rules")
