"""FastAPI 应用入口。"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import analysis, contents, copywriter, creators, crawl_jobs, projects
from app.api.v1.copy import router as copy_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.session import init_db

settings = get_settings()
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.db.session import SessionLocal
    from app.services.project import create_user, get_user_by_email

    init_db()
    db = SessionLocal()
    try:
        if not get_user_by_email(db, "admin@v2.local"):
            create_user(db, "admin@v2.local", "hashed-placeholder", "Admin")
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router, prefix="/api/v1")
app.include_router(creators.router, prefix="/api/v1")
app.include_router(contents.router, prefix="/api/v1")
app.include_router(crawl_jobs.router, prefix="/api/v1")
app.include_router(analysis.router, prefix="/api/v1")
app.include_router(copywriter.router, prefix="/api/v1")
app.include_router(copy_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}
