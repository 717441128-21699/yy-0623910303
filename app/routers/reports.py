from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.database import get_db
from app.models.project import Project
from app.models.event import WarningEvent
from app.models.rule import WarningRule

router = APIRouter(prefix="/reports", tags=["每日预警清单与统计"])


@router.get("/daily", summary="按客户维度生成每日预警清单")
def get_daily_report(
    date: Optional[str] = Query(None, description="日期 YYYY-MM-DD，默认今天"),
    project_id: Optional[int] = Query(None, description="指定项目ID，默认全部项目"),
    db: Session = Depends(get_db),
):
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式错误，请使用 YYYY-MM-DD")
    else:
        target_date = datetime.utcnow()

    day_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)

    projects_query = db.query(Project)
    if project_id:
        projects_query = projects_query.filter(Project.id == project_id)
    projects = projects_query.filter(Project.status == "active").all()

    report_items = []
    for project in projects:
        events_query = db.query(WarningEvent).filter(
            WarningEvent.project_id == project.id,
            WarningEvent.event_date >= day_start,
            WarningEvent.event_date < day_end,
        )
        events = events_query.order_by(WarningEvent.propagation_score.desc()).all()

        risk_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        type_counts = {}
        need_review_count = 0
        reviewed_count = 0

        for ev in events:
            if ev.risk_level in risk_counts:
                risk_counts[ev.risk_level] += 1
            if ev.need_manual_review:
                need_review_count += 1
            if ev.status == "reviewed":
                reviewed_count += 1
            for mr in (ev.matched_rules or []):
                rt = mr.get("rule_type", "unknown")
                type_counts[rt] = type_counts.get(rt, 0) + 1

        event_list = []
        for ev in events:
            event_list.append(
                {
                    "id": ev.id,
                    "title": ev.title,
                    "content_preview": (ev.content or "")[:200],
                    "source_url": ev.source_url,
                    "source_type": ev.source_type,
                    "publish_time": ev.publish_time,
                    "author": ev.author,
                    "risk_level": ev.risk_level,
                    "hit_reasons": ev.hit_reasons or [],
                    "suggested_tags": ev.suggested_tags or [],
                    "propagation_score": ev.propagation_score,
                    "forward_count": ev.forward_count,
                    "comment_count": ev.comment_count,
                    "like_count": ev.like_count,
                    "need_manual_review": bool(ev.need_manual_review),
                    "status": ev.status,
                }
            )

        report_items.append(
            {
                "project_id": project.id,
                "project_name": project.name,
                "client_name": project.client_name,
                "industry": project.industry,
                "region": project.region,
                "summary": {
                    "total_events": len(events),
                    "risk_counts": risk_counts,
                    "rule_type_counts": type_counts,
                    "need_manual_review_count": need_review_count,
                    "reviewed_count": reviewed_count,
                    "pending_review_count": need_review_count - reviewed_count
                    if need_review_count >= reviewed_count
                    else 0,
                },
                "events": event_list,
            }
        )

    return {
        "report_date": day_start.strftime("%Y-%m-%d"),
        "generated_at": datetime.utcnow().isoformat(),
        "total_projects": len(report_items),
        "projects": report_items,
    }


@router.get("/stats", summary="全局统计概览")
def get_global_stats(
    days: int = Query(7, ge=1, le=365, description="统计最近N天"),
    db: Session = Depends(get_db),
):
    start_date = datetime.utcnow() - timedelta(days=days)

    total_projects = db.query(func.count(Project.id)).filter(Project.status == "active").scalar() or 0
    total_rules = (
        db.query(func.count(WarningRule.id)).filter(WarningRule.is_enabled == 1).scalar() or 0
    )

    events = (
        db.query(WarningEvent).filter(WarningEvent.event_date >= start_date).all()
    )

    risk_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    total_need_review = 0
    total_reviewed = 0
    project_counts: Dict[int, int] = {}

    for ev in events:
        if ev.risk_level in risk_counts:
            risk_counts[ev.risk_level] += 1
        if ev.need_manual_review:
            total_need_review += 1
        if ev.status == "reviewed":
            total_reviewed += 1
        project_counts[ev.project_id] = project_counts.get(ev.project_id, 0) + 1

    project_stats = []
    for pid, cnt in sorted(project_counts.items(), key=lambda x: x[1], reverse=True):
        p = db.query(Project).filter(Project.id == pid).first()
        if p:
            project_stats.append(
                {
                    "project_id": p.id,
                    "project_name": p.name,
                    "client_name": p.client_name,
                    "event_count": cnt,
                }
            )

    return {
        "period_days": days,
        "period_start": start_date.isoformat(),
        "active_projects": total_projects,
        "enabled_rules": total_rules,
        "total_events": len(events),
        "risk_distribution": risk_counts,
        "events_need_review": total_need_review,
        "events_reviewed": total_reviewed,
        "top_projects": project_stats[:10],
    }
