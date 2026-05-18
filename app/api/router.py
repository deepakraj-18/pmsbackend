from fastapi import APIRouter
from app.api.endpoints import (
    auth, users, teams, masters, projects, tasks, issues,
    timelogs, reports, milestones, task_lists,
    documents, templates,
    project_groups, search, graph, audit, agent
)

api_router = APIRouter()

api_router.include_router(auth.router,          prefix="/auth",           tags=["auth"])
api_router.include_router(graph.router,         prefix="/graph",          tags=["graph"])
api_router.include_router(users.router,         prefix="/users",          tags=["users"])
api_router.include_router(teams.router,         prefix="/teams",          tags=["teams"])
api_router.include_router(masters.router,       prefix="/masters",        tags=["masters"])
api_router.include_router(projects.router,      prefix="/projects",       tags=["projects"])
api_router.include_router(templates.router,     prefix="/templates",      tags=["templates"])
api_router.include_router(tasks.router,         prefix="/tasks",          tags=["tasks"])
api_router.include_router(issues.router,        prefix="/issues",         tags=["issues"])
api_router.include_router(timelogs.router,      prefix="/timelogs",       tags=["timelogs"])
api_router.include_router(milestones.router,    prefix="/milestones",     tags=["milestones"])
api_router.include_router(task_lists.router,    prefix="/tasklists",      tags=["tasklists"])
api_router.include_router(documents.router,     prefix="/documents",      tags=["documents"])
api_router.include_router(reports.router,       prefix="/reports",        tags=["reports"])
api_router.include_router(project_groups.router,prefix="/project-groups", tags=["project-groups"])
api_router.include_router(search.router,        prefix="/search",         tags=["search"])
api_router.include_router(audit.router,          prefix="/audit",          tags=["audit"])
api_router.include_router(agent.router,          prefix="",                tags=["agent"])
