from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.project import Project
from app.schemas import project as schemas

router = APIRouter(prefix="/projects", tags=["客户项目管理"])


@router.post("", response_model=schemas.Project, summary="创建客户项目")
def create_project(project_in: schemas.ProjectCreate, db: Session = Depends(get_db)):
    project = Project(
        name=project_in.name,
        client_name=project_in.client_name,
        industry=project_in.industry,
        region=project_in.region,
        key_entities=project_in.key_entities or [],
        description=project_in.description,
        status=project_in.status or "active",
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=List[schemas.Project], summary="获取项目列表")
def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = Query(None, description="按状态筛选"),
    client_name: Optional[str] = Query(None, description="按客户名称模糊搜索"),
    db: Session = Depends(get_db),
):
    query = db.query(Project)
    if status:
        query = query.filter(Project.status == status)
    if client_name:
        query = query.filter(Project.client_name.contains(client_name))
    projects = query.order_by(Project.updated_at.desc()).offset(skip).limit(limit).all()
    return projects


@router.get("/{project_id}", response_model=schemas.Project, summary="获取项目详情")
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project


@router.put("/{project_id}", response_model=schemas.Project, summary="更新项目")
def update_project(
    project_id: int, project_in: schemas.ProjectUpdate, db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    update_data = project_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", summary="删除项目")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    db.delete(project)
    db.commit()
    return {"message": "项目已删除", "id": project_id}
