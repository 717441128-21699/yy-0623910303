from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.event import WarningEvent, EVENT_STATUS_PENDING
from app.models.project import Project
from app.models.rule import WarningRule
from app.schemas import event as schemas
from app.services.risk_engine import risk_engine

router = APIRouter(prefix="/events", tags=["事件回传与判别"])


@router.post(
    "/ingest",
    response_model=schemas.WarningEventWithAssessment,
    summary="接收外部采集系统事件并返回风险判别结果",
)
def ingest_event(event_in: schemas.WarningEventCreate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == event_in.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="目标项目不存在")

    rules = (
        db.query(WarningRule)
        .filter(WarningRule.project_id == event_in.project_id, WarningRule.is_enabled == 1)
        .all()
    )

    forward_count = 0
    comment_count = 0
    like_count = 0
    read_count = 0
    if event_in.propagation:
        forward_count = event_in.propagation.forward_count
        comment_count = event_in.propagation.comment_count
        like_count = event_in.propagation.like_count
        read_count = event_in.propagation.read_count

    full_text = f"{event_in.title or ''}\n{event_in.content}"
    assessment, propagation_score = risk_engine.assess(
        text=full_text,
        rules=rules,
        key_entities=project.key_entities,
        forward_count=forward_count,
        comment_count=comment_count,
        like_count=like_count,
        read_count=read_count,
    )

    event = WarningEvent(
        project_id=event_in.project_id,
        title=event_in.title,
        content=event_in.content,
        source_url=event_in.source_url,
        source_type=event_in.source_type,
        publish_time=event_in.publish_time,
        author=event_in.author,
        forward_count=forward_count,
        comment_count=comment_count,
        like_count=like_count,
        read_count=read_count,
        propagation_score=propagation_score,
        risk_level=assessment.risk_level,
        hit_reasons=assessment.hit_reasons,
        suggested_tags=assessment.suggested_tags,
        matched_rules=assessment.matched_rules,
        need_manual_review=1 if assessment.need_manual_review else 0,
        status=EVENT_STATUS_PENDING,
        event_date=datetime.utcnow(),
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    result = schemas.WarningEventWithAssessment(
        id=event.id,
        project_id=event.project_id,
        title=event.title,
        content=event.content,
        source_url=event.source_url,
        source_type=event.source_type,
        publish_time=event.publish_time,
        author=event.author,
        forward_count=event.forward_count,
        comment_count=event.comment_count,
        like_count=event.like_count,
        read_count=event.read_count,
        propagation_score=event.propagation_score,
        risk_level=event.risk_level,
        hit_reasons=event.hit_reasons or [],
        suggested_tags=event.suggested_tags or [],
        matched_rules=event.matched_rules or [],
        need_manual_review=event.need_manual_review,
        status=event.status,
        event_date=event.event_date,
        created_at=event.created_at,
        assessment=assessment,
    )
    return result


@router.get("", response_model=List[schemas.WarningEvent], summary="获取预警事件列表")
def list_events(
    project_id: Optional[int] = Query(None, description="按项目ID筛选"),
    risk_level: Optional[str] = Query(None, description="按风险等级筛选"),
    status: Optional[str] = Query(None, description="按状态筛选"),
    need_manual_review: Optional[int] = Query(None, description="是否仅需人工复核"),
    start_date: Optional[datetime] = Query(None, description="开始时间"),
    end_date: Optional[datetime] = Query(None, description="结束时间"),
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    query = db.query(WarningEvent)
    if project_id:
        query = query.filter(WarningEvent.project_id == project_id)
    if risk_level:
        query = query.filter(WarningEvent.risk_level == risk_level)
    if status:
        query = query.filter(WarningEvent.status == status)
    if need_manual_review is not None:
        query = query.filter(WarningEvent.need_manual_review == need_manual_review)
    if start_date:
        query = query.filter(WarningEvent.event_date >= start_date)
    if end_date:
        query = query.filter(WarningEvent.event_date <= end_date)

    events = (
        query.order_by(WarningEvent.event_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return events


@router.get("/{event_id}", response_model=schemas.WarningEvent, summary="获取事件详情")
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(WarningEvent).filter(WarningEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="事件不存在")
    return event
