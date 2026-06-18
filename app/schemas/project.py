from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ProjectBase(BaseModel):
    name: str = Field(..., max_length=200, description="项目名称")
    client_name: str = Field(..., max_length=200, description="客户名称")
    industry: Optional[str] = Field(None, max_length=100, description="所属行业")
    region: Optional[str] = Field(None, max_length=200, description="关注地域")
    key_entities: Optional[List[str]] = Field(default_factory=list, description="重点监测主体")
    description: Optional[str] = Field(None, description="项目描述")
    status: Optional[str] = Field("active", max_length=20, description="项目状态")


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    client_name: Optional[str] = Field(None, max_length=200)
    industry: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=200)
    key_entities: Optional[List[str]] = None
    description: Optional[str] = None
    status: Optional[str] = Field(None, max_length=20)


class Project(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
