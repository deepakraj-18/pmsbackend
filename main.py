import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.api.router import api_router

from app.utils.exceptions import add_exception_handlers
from app.models.masters import UserStatus, Skill, Status, Priority
from app.models.roles import Role
from app.models.user import User, user_team_link
from app.models.team import Team
from app.models.template import ProjectTemplate, TemplateTask
from app.models.project import Project, ProjectMember
from app.models.task import Task
from app.models.issue import Issue
from app.models.timelog import TimeLog
from app.models.milestone import Milestone
from app.models.task_list import TaskList
from app.models.document import Document
from app.models.project_group import ProjectGroup
from app.models.audit import AuditFieldsMapping, AuditLogs, AuditLogDetails, AuditMetaDataInfo
from app.models.master import MasterLookup
from app.models.timesheet import Timesheet
from app.models.agent import ProjectPhase, AgentRun, TestCase, TestReport
from fastapi.staticfiles import StaticFiles

if not os.path.exists("uploads"):
    os.makedirs("uploads")

IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
    engine.dispose()

app = FastAPI(
    title    = settings.PROJECT_NAME,
    version  = settings.VERSION,
    lifespan = lifespan,
    docs_url    = None if IS_PRODUCTION else "/docs",
    redoc_url   = None if IS_PRODUCTION else "/redoc",
    openapi_url = f"{settings.API_V1_STR}/openapi.json" if not IS_PRODUCTION else None,
)

add_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin",
        "X-Requested-With",
        "ConsistencyLevel",
        "X-Forwarded-For",
        "X-Forwarded-Proto",
    ],
    expose_headers=["Content-Disposition"],
    max_age=600,
)

app.add_middleware(GZipMiddleware, minimum_size=settings.GZIP_MINIMUM_SIZE)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)

app.mount(f"/{settings.UPLOAD_DIR}", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}", "status": "online"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.APP_PORT, reload=True)