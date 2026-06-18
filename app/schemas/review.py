from pydantic import BaseModel, Field
from typing import List, Optional
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


class ReviewRecordCreate(BaseModel):
    event_id: int = Field(..., description="事件ID")
    reviewer: str = Field(..., max_length=100, description="复核人")
    review_result: str = Field(..., max_length=50, description=f"复核结果: {', '.join(REVIEW_RESULTS)}")
    corrected_risk_level: Optional[str] = Field(None, max_length=20, description="修正后的风险等级")
    corrected_tags: Optional[List[str]] = Field(default_factory=list, description="修正后的标签")
    remarks: Optional[List[str]] = Field(default_factory=list, description="标准备注选项")
    remark_text: Optional[str] = Field(None, description="自定义备注内容")


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
