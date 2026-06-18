from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal, Any
from datetime import datetime


REVIEW_RESULTS = ["confirm", "false_positive", "upgrade", "downgrade"]

STANDARD_REMARKS = [
    "讽刺语气",
    "旧闻重发",
    "境外来源转载",
    "水军行为",
    "正常舆情",
    "内容已删除",
    "非目标主体",
]

RISK_LEVELS = ["low", "medium", "high", "critical"]

ReviewResultLiteral = Literal["confirm", "false_positive", "upgrade", "downgrade"]
RiskLevelLiteral = Literal["low", "medium", "high", "critical"]


def _format_allowed_options(options: List[str]) -> str:
    return "、".join([f"'{opt}'" for opt in options])


class ReviewRecordCreate(BaseModel):
    event_id: int = Field(..., description="事件ID")
    reviewer: str = Field(..., max_length=100, description="复核人")
    review_result: ReviewResultLiteral = Field(
        ..., description=f"复核结果，可选值: {_format_allowed_options(REVIEW_RESULTS)}"
    )
    corrected_risk_level: Optional[RiskLevelLiteral] = Field(
        None, description=f"修正后的风险等级，可选值: {_format_allowed_options(RISK_LEVELS)}"
    )
    corrected_tags: Optional[List[str]] = Field(default_factory=list, description="修正后的标签")
    remarks: Optional[List[str]] = Field(default_factory=list, description="标准备注选项")
    remark_text: Optional[str] = Field(None, description="自定义备注内容")

    @field_validator("review_result")
    @classmethod
    def validate_review_result(cls, v: Any) -> str:
        if v not in REVIEW_RESULTS:
            raise ValueError(
                f"无效的复核结果 '{v}'，仅支持以下值: {_format_allowed_options(REVIEW_RESULTS)}"
            )
        return v

    @field_validator("corrected_risk_level")
    @classmethod
    def validate_corrected_risk_level(cls, v: Any) -> Optional[str]:
        if v is None:
            return v
        if v not in RISK_LEVELS:
            raise ValueError(
                f"无效的修正风险等级 '{v}'，仅支持以下值: {_format_allowed_options(RISK_LEVELS)}"
            )
        return v

    @field_validator("remarks")
    @classmethod
    def validate_remarks(cls, v: Any) -> List[str]:
        if v is None:
            return []
        invalid_remarks = [r for r in v if r not in STANDARD_REMARKS]
        if invalid_remarks:
            raise ValueError(
                f"无效的标准备注选项 {_format_allowed_options(invalid_remarks)}，"
                f"仅支持: {_format_allowed_options(STANDARD_REMARKS)}。"
                f"自定义说明请填写 remark_text 字段。"
            )
        return v


class ReviewRecord(BaseModel):
    id: int
    event_id: int
    reviewer: str
    review_result: str
    corrected_risk_level: Optional[str]
    corrected_tags: List[str]
    remarks: List[str]
    remark_text: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
