"""Main entry point for the FastAPI application."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.routers.health import router as health_router
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.games import router as games_router
from app.routers.participations import router as participations_router
from app.logger import logger


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Startup and shutdown events"""
    logger.info("Starting up...")
    yield
    logger.info("Shutting down...")

app = FastAPI(lifespan=lifespan)
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(games_router)
app.include_router(participations_router)

app.openapi_schema = get_openapi(
    title="Trump API",
    version="1.0.0",
    description="API dealing trump cards",
    routes=app.routes,
)
