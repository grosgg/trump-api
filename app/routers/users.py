"""Users routes"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth import fastapi_users
from app.schemas import UserCreate, UserRead, UserCharge
from app.database import User, get_db
from app.logger import logger

current_user = fastapi_users.current_user()
router = APIRouter(prefix="/users", tags=["users"])

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix=""
)


@router.get("/me")
async def get_user(
    user: User = Depends(current_user)
) -> UserRead:
    """Get current user"""
    return UserRead(**user.__dict__)


@router.post("/charge")
async def charge_user(
    charge: UserCharge,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db)
) -> UserRead:
    """Add cash to user account"""

    logger.info("User %s is charging %s cash", user.id, charge.amount)
    user.cash = getattr(user, 'cash') + charge.amount
    await db.commit()
    await db.refresh(user)
    logger.info("User %s has %s cash", user.id, user.cash)

    return UserRead(**user.__dict__)
