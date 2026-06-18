from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


RULE_TYPES = [
    "policy_dispute",
    "leader_related",
    "governance_complaint",
    "public_emergency",
    "custom",
]

RISK_LEVELS = ["low", "medium", "high", "critical"]


class WarningRuleBase(BaseModel):
    project_id: int = Field(..., description="所属项目ID")
    name: str = Field(..., max_length=200, description="规则名称")
    rule_type: str = Field(..., max_length=50, description=f"规则类型: {', '.join(RULE_TYPES)}")
    keywords: List[str] = Field(default_factory=list, description="敏感关键词列表")
    risk_level: str = Field("medium", max_length=20, description=f"风险等级: {', '.join(RISK_LEVELS)}")
    weight: int = Field(1, ge=1, le=10, description="规则权重(1-10)")
    suggested_tags: Optional[List[str]] = Field(default_factory=list, description="建议标签")
    description: Optional[str] = Field(None, description="规则描述")
    is_enabled: Optional[int] = Field(1, description="是否启用(1启用,0禁用)")


class WarningRuleCreate(WarningRuleBase):
    pass


class WarningRuleUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    rule_type: Optional[str] = Field(None, max_length=50)
    keywords: Optional[List[str]] = None
    risk_level: Optional[str] = Field(None, max_length=20)
    weight: Optional[int] = Field(None, ge=1, le=10)
    suggested_tags: Optional[List[str]] = None
    description: Optional[str] = None
    is_enabled: Optional[int] = None


class WarningRule(WarningRuleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
