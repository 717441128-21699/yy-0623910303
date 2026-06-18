from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.config import settings
from app.database import engine, Base
from app.routers import projects, rules, events, reviews, reports

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="面向舆情服务公司分析师的后端预警服务，提供客户项目创建、预警规则管理、事件回传判别、人工复核和每日预警清单功能。",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = ".".join([str(x) for x in err["loc"] if x != "body"]) or "请求参数"
        msg = err["msg"]
        errors.append({"field": field, "message": msg})

    detail_msg = "；".join([f"{e['field']}: {e['message']}" for e in errors])

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": 422,
            "message": f"参数校验失败: {detail_msg}",
            "errors": errors,
        },
    )


@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    errors = []
    for err in exc.errors():
        field = ".".join([str(x) for x in err["loc"]]) or "参数"
        msg = err["msg"]
        errors.append({"field": field, "message": msg})

    detail_msg = "；".join([f"{e['field']}: {e['message']}" for e in errors])

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": 422,
            "message": f"数据校验失败: {detail_msg}",
            "errors": errors,
        },
    )


app.include_router(projects.router, prefix=settings.API_V1_PREFIX)
app.include_router(rules.router, prefix=settings.API_V1_PREFIX)
app.include_router(events.router, prefix=settings.API_V1_PREFIX)
app.include_router(reviews.router, prefix=settings.API_V1_PREFIX)
app.include_router(reports.router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["系统"])
def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "api_prefix": settings.API_V1_PREFIX,
    }


@app.get("/health", tags=["系统"])
def health_check():
    return {"status": "ok"}
