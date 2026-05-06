import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.logging_config import logger
from app.core.database import engine, Base, ensure_database_exists
from app.api.router import api_router
from app.core.seeding import seed_all
from app.utils.exceptions import add_exception_handlers

if not os.path.exists(settings.UPLOAD_DIR):
    os.makedirs(settings.UPLOAD_DIR)

IS_PRODUCTION = settings.ENVIRONMENT.lower() == "production"

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up application...")
    if settings.ENABLE_DB_CREATE:
        try:
            ensure_database_exists()
            Base.metadata.create_all(bind=engine)
        except Exception as e:
            logger.error(f"Database setup failed: {e}")
    if settings.AUTO_SEED:
        try:
            seed_all(reset=False)
        except Exception as e:
            logger.error(f"Auto-seeding failed: {e}")
    yield
    engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url=None if IS_PRODUCTION else "/docs",
    redoc_url=None if IS_PRODUCTION else "/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if not IS_PRODUCTION else None,
)

add_exception_handlers(app)

app.add_middleware(GZipMiddleware, minimum_size=settings.GZIP_MINIMUM_SIZE)

# In production, we trust the proxy to handle HTTPS and Host validation
if not IS_PRODUCTION:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )

app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

class ForceHTTPSMiddleware:
    def __init__(self, app):
        self.app = app
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            if b"x-forwarded-proto" in headers:
                scope["scheme"] = headers[b"x-forwarded-proto"].decode("latin1").strip()
            elif IS_PRODUCTION:
                scope["scheme"] = "https"
        return await self.app(scope, receive, send)

app.add_middleware(ForceHTTPSMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS or ["*"],
    allow_origin_regex=r"https://.*\.azurestaticapps\.net",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

app.mount(f"/{settings.UPLOAD_DIR}", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}", "status": "online"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.APP_PORT, reload=not IS_PRODUCTION)
