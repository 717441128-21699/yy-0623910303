from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.review import ReviewRecord
from app.models.event import WarningEvent, EVENT_STATUS_REVIEWED, EVENT_STATUS_IGNORED
from app.schemas import review as schemas

router = APIRouter(prefix="/reviews", tags=["人工复核"])


@router.post("", response_model=schemas.ReviewRecord, summary="提交人工复核结果")
def create_review(review_in: schemas.ReviewRecordCreate, db: Session = Depends(get_db)):
    event = db.query(WarningEvent).filter(WarningEvent.id == review_in.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="关联事件不存在")

    review = ReviewRecord(
        event_id=review_in.event_id,
        reviewer=review_in.reviewer,
        review_result=review_in.review_result,
        corrected_risk_level=review_in.corrected_risk_level,
        corrected_tags=review_in.corrected_tags or [],
        remarks=review_in.remarks or [],
        remark_text=review_in.remark_text,
    )
    db.add(review)

    if review_in.corrected_risk_level:
        event.risk_level = review_in.corrected_risk_level
    if review_in.corrected_tags:
        event.suggested_tags = review_in.corrected_tags

    if review_in.review_result == "false_positive":
        event.status = EVENT_STATUS_IGNORED
    else:
        event.status = EVENT_STATUS_REVIEWED

    event.need_manual_review = 0

    db.commit()
    db.refresh(review)
    return review


@router.get("", response_model=List[schemas.ReviewRecord], summary="获取复核记录列表")
def list_reviews(
    event_id: Optional[int] = Query(None, description="按事件ID筛选"),
    reviewer: Optional[str] = Query(None, description="按复核人筛选"),
    review_result: Optional[str] = Query(None, description="按复核结果筛选"),
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    query = db.query(ReviewRecord)
    if event_id:
        query = query.filter(ReviewRecord.event_id == event_id)
    if reviewer:
        query = query.filter(ReviewRecord.reviewer.contains(reviewer))
    if review_result:
        query = query.filter(ReviewRecord.review_result == review_result)

    reviews = (
        query.order_by(ReviewRecord.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return reviews


@router.get("/{review_id}", response_model=schemas.ReviewRecord, summary="获取复核详情")
def get_review(review_id: int, db: Session = Depends(get_db)):
    review = db.query(ReviewRecord).filter(ReviewRecord.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="复核记录不存在")
    return review
