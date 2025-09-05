"""Games routes"""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth import fastapi_users
from app.schemas import GameCreate, GameRead
from app.database import get_db
from app.models import User, Game
from app.blackjack import initialize_decks

current_user = fastapi_users.current_user()
router = APIRouter(prefix="/games", tags=["games"])


@router.get("")
async def get_games(
    _user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db)
) -> list[GameRead]:
    """Get all games"""
    games = await db.scalars(select(Game))
    return [GameRead(**game.__dict__) for game in games]


@router.get("/{game_id}")
async def get_game(
    game_id: uuid.UUID,
    _user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db)
) -> GameRead:
    """Get a game"""
    game = await db.get(Game, game_id)

    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    return GameRead(**game.__dict__)


@router.post("")
async def create_game(
    game: GameCreate,
    _user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db)
) -> GameRead:
    """Create a new game"""

    new_game = Game(variant=game.variant)
    db.add(new_game)
    await db.commit()
    await db.refresh(new_game)

    await initialize_decks(new_game, db)

    return GameRead(**new_game.__dict__)
