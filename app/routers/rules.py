from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.rule import WarningRule
from app.models.project import Project
from app.schemas import rule as schemas

router = APIRouter(prefix="/rules", tags=["预警规则管理"])


@router.post("", response_model=schemas.WarningRule, summary="创建预警规则")
def create_rule(rule_in: schemas.WarningRuleCreate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == rule_in.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="所属项目不存在")

    rule = WarningRule(
        project_id=rule_in.project_id,
        name=rule_in.name,
        rule_type=rule_in.rule_type,
        keywords=rule_in.keywords or [],
        risk_level=rule_in.risk_level,
        weight=rule_in.weight,
        suggested_tags=rule_in.suggested_tags or [],
        description=rule_in.description,
        is_enabled=rule_in.is_enabled if rule_in.is_enabled is not None else 1,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.get("", response_model=List[schemas.WarningRule], summary="获取规则列表")
def list_rules(
    project_id: Optional[int] = Query(None, description="按项目ID筛选"),
    rule_type: Optional[str] = Query(None, description="按规则类型筛选"),
    is_enabled: Optional[int] = Query(None, description="按启用状态筛选"),
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    query = db.query(WarningRule)
    if project_id:
        query = query.filter(WarningRule.project_id == project_id)
    if rule_type:
        query = query.filter(WarningRule.rule_type == rule_type)
    if is_enabled is not None:
        query = query.filter(WarningRule.is_enabled == is_enabled)
    rules = query.order_by(WarningRule.updated_at.desc()).offset(skip).limit(limit).all()
    return rules


@router.get("/{rule_id}", response_model=schemas.WarningRule, summary="获取规则详情")
def get_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(WarningRule).filter(WarningRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    return rule


@router.put("/{rule_id}", response_model=schemas.WarningRule, summary="更新规则")
def update_rule(
    rule_id: int, rule_in: schemas.WarningRuleUpdate, db: Session = Depends(get_db)
):
    rule = db.query(WarningRule).filter(WarningRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")

    update_data = rule_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)

    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/{rule_id}", summary="删除规则")
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(WarningRule).filter(WarningRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    db.delete(rule)
    db.commit()
    return {"message": "规则已删除", "id": rule_id}
