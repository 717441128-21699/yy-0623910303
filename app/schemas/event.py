from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class EventPropagationData(BaseModel):
    forward_count: int = Field(0, description="转发数")
    comment_count: int = Field(0, description="评论数")
    like_count: int = Field(0, description="点赞数")
    read_count: int = Field(0, description="阅读数")


class WarningEventCreate(BaseModel):
    project_id: int = Field(..., description="目标项目ID")
    title: Optional[str] = Field(None, max_length=500, description="标题")
    content: str = Field(..., description="文本内容")
    source_url: Optional[str] = Field(None, max_length=1000, description="原文链接")
    source_type: Optional[str] = Field(None, max_length=100, description="来源类型(微博/公众号/论坛等)")
    publish_time: Optional[datetime] = Field(None, description="发布时间")
    author: Optional[str] = Field(None, max_length=200, description="作者")
    propagation: Optional[EventPropagationData] = Field(None, description="传播数据")


class RiskAssessmentResult(BaseModel):
    risk_level: str = Field(..., description="风险等级")
    hit_reasons: List[str] = Field(default_factory=list, description="命中原因")
    suggested_tags: List[str] = Field(default_factory=list, description="建议标签")
    matched_rules: List[dict] = Field(default_factory=list, description="命中的规则详情")
    need_manual_review: bool = Field(False, description="是否需要人工复核")


class WarningEvent(BaseModel):
    id: int
    project_id: int
    title: Optional[str]
    content: str
    source_url: Optional[str]
    source_type: Optional[str]
    publish_time: Optional[datetime]
    author: Optional[str]
    forward_count: int
    comment_count: int
    like_count: int
    read_count: int
    propagation_score: float
    risk_level: Optional[str]
    hit_reasons: List[str]
    suggested_tags: List[str]
    matched_rules: List[dict]
    need_manual_review: int
    status: str
    event_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class WarningEventWithAssessment(WarningEvent):
    assessment: RiskAssessmentResult
