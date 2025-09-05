"""Authentication routes"""
from fastapi import APIRouter
from app.auth import fastapi_users, auth_backend

router = APIRouter(prefix="/auth", tags=["auth"])

# Include authentication routes
router.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix=""
)
