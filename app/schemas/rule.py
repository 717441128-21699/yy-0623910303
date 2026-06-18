from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal, Any
from datetime import datetime


RULE_TYPES = [
    "policy_dispute",
    "leader_related",
    "governance_complaint",
    "public_emergency",
    "custom",
]

RISK_LEVELS = ["low", "medium", "high", "critical"]

RuleTypeLiteral = Literal[
    "policy_dispute",
    "leader_related",
    "governance_complaint",
    "public_emergency",
    "custom",
]

RiskLevelLiteral = Literal["low", "medium", "high", "critical"]


def _format_allowed_options(options: List[str]) -> str:
    return "、".join([f"'{opt}'" for opt in options])


class WarningRuleBase(BaseModel):
    project_id: int = Field(..., description="所属项目ID")
    name: str = Field(..., max_length=200, description="规则名称")
    rule_type: RuleTypeLiteral = Field(
        ..., description=f"规则类型，可选值: {_format_allowed_options(RULE_TYPES)}"
    )
    keywords: List[str] = Field(default_factory=list, description="敏感关键词列表")
    risk_level: RiskLevelLiteral = Field(
        "medium", description=f"风险等级，可选值: {_format_allowed_options(RISK_LEVELS)}"
    )
    weight: int = Field(1, ge=1, le=10, description="规则权重(1-10)")
    suggested_tags: Optional[List[str]] = Field(default_factory=list, description="建议标签")
    description: Optional[str] = Field(None, description="规则描述")
    is_enabled: Optional[int] = Field(1, description="是否启用(1启用,0禁用)")

    @field_validator("rule_type")
    @classmethod
    def validate_rule_type(cls, v: Any) -> str:
        if v not in RULE_TYPES:
            raise ValueError(
                f"无效的规则类型 '{v}'，仅支持以下值: {_format_allowed_options(RULE_TYPES)}"
            )
        return v

    @field_validator("risk_level")
    @classmethod
    def validate_risk_level(cls, v: Any) -> str:
        if v not in RISK_LEVELS:
            raise ValueError(
                f"无效的风险等级 '{v}'，仅支持以下值: {_format_allowed_options(RISK_LEVELS)}"
            )
        return v


class WarningRuleCreate(WarningRuleBase):
    pass


class WarningRuleUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    rule_type: Optional[RuleTypeLiteral] = Field(
        None, description=f"规则类型，可选值: {_format_allowed_options(RULE_TYPES)}"
    )
    keywords: Optional[List[str]] = None
    risk_level: Optional[RiskLevelLiteral] = Field(
        None, description=f"风险等级，可选值: {_format_allowed_options(RISK_LEVELS)}"
    )
    weight: Optional[int] = Field(None, ge=1, le=10)
    suggested_tags: Optional[List[str]] = None
    description: Optional[str] = None
    is_enabled: Optional[int] = None

    @field_validator("rule_type")
    @classmethod
    def validate_rule_type(cls, v: Any) -> Optional[str]:
        if v is None:
            return v
        if v not in RULE_TYPES:
            raise ValueError(
                f"无效的规则类型 '{v}'，仅支持以下值: {_format_allowed_options(RULE_TYPES)}"
            )
        return v

    @field_validator("risk_level")
    @classmethod
    def validate_risk_level(cls, v: Any) -> Optional[str]:
        if v is None:
            return v
        if v not in RISK_LEVELS:
            raise ValueError(
                f"无效的风险等级 '{v}'，仅支持以下值: {_format_allowed_options(RISK_LEVELS)}"
            )
        return v


class WarningRule(WarningRuleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
