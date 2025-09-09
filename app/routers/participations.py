"""Participations routes"""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import fastapi_users
from app.schemas import ParticipationCreate, ParticipationRead, ParticipationReadWithGameCards, ParticipationBet, GameCardRead
from app.database import get_db
from app.models import User, Game, Participation, GameCard
from app.enums import GameStatus, ParticipationStatus, CardLocation
from app.blackjack import evaluate_game_status, start_round

current_user = fastapi_users.current_user()
router = APIRouter(prefix="/participations", tags=["participations"])


@router.get("")
async def get_participations(
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db)
) -> list[ParticipationRead]:
    """Get all participations"""
    participations = await db.scalars(
        select(Participation).where(Participation.user_id == user.id)
    )

    return [ParticipationRead(**participation.__dict__) for participation in participations]


@router.get("/{participation_id}")
async def get_participation(
    participation_id: uuid.UUID,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a participation"""
    result = await db.execute(
        select(Participation)
        .where(Participation.id == participation_id)
    )
    participation = result.scalar_one_or_none()
    if not participation:
        raise HTTPException(status_code=404, detail="Participation not found")

    if getattr(user, 'id') != getattr(participation, 'user_id'):
        raise HTTPException(status_code=401, detail="Unauthorized")

    result = await db.execute(
        select(GameCard)
        .where(GameCard.holder_id == participation.id)
        .where(GameCard.location_type == CardLocation.PLAYER_HAND)
    )
    game_cards = result.scalars().all()

    game_cards_data = [GameCardRead(**game_card.__dict__)
                       for game_card in game_cards]
    participation_data = {**participation.__dict__,
                          'game_cards': game_cards_data}
    return ParticipationReadWithGameCards(**participation_data)


@router.post("")
async def create_participation(
    participation: ParticipationCreate,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db)
) -> ParticipationRead:
    """Create a participation"""

    game = await db.get(Game, participation.game_id)

    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    if getattr(game, 'status') != GameStatus.READY:
        raise HTTPException(
            status_code=400, detail="Game is not accepting participants")

    if getattr(user, 'cash') < participation.cash:
        raise HTTPException(status_code=400, detail="Not enough cash")

    participations = await db.scalars(
        select(Participation).where(Participation.game_id == game.id))
    participations_list = list(participations)
    max_position = -1 if not participations_list else max((getattr(participation, 'position'))
                                                          for participation in participations_list)

    new_participation = Participation(
        position=max_position + 1,
        cash=participation.cash,
        game_id=game.id,
        user_id=user.id
    )
    db.add(new_participation)

    user.cash = getattr(user, 'cash') - participation.cash

    await db.commit()
    await db.refresh(new_participation)

    return ParticipationRead(**new_participation.__dict__)


@router.delete("/{participation_id}", status_code=204)
async def delete_participation(
    participation_id: uuid.UUID,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db)
):
    """Quit a game"""

    participation = await db.get(Participation, participation_id)

    if not participation:
        raise HTTPException(status_code=404, detail="Participation not found")

    if getattr(user, 'id') != getattr(participation, 'user_id'):
        raise HTTPException(status_code=401, detail="Unauthorized")

    game = await db.get(Game, participation.game_id)

    if not game:
        raise HTTPException(
            status_code=404, detail="Game not found for this participation")

    if getattr(game, 'status') != GameStatus.READY:
        raise HTTPException(
            status_code=400, detail="Game is on going")

    setattr(participation, 'status', ParticipationStatus.QUIT)
    setattr(game, 'status', evaluate_game_status(game, db))

    await db.commit()

    return None


@router.post("/{participation_id}/bet")
async def bet(
    participation_id: uuid.UUID,
    participation_bet: ParticipationBet,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db)
):
    """Bet on a game"""

    participation = await db.get(Participation, participation_id)

    if not participation:
        raise HTTPException(status_code=404, detail="Participation not found")

    if getattr(user, 'id') != getattr(participation, 'user_id'):
        raise HTTPException(status_code=401, detail="Unauthorized")

    if getattr(participation, 'status') != ParticipationStatus.PLAYING:
        raise HTTPException(
            status_code=400, detail="Participation is terminated")

    game = await db.get(Game, participation.game_id)

    if not game:
        raise HTTPException(
            status_code=404, detail="Game not found for this participation")

    if getattr(game, 'status') != GameStatus.READY:
        raise HTTPException(
            status_code=400, detail="Game is not accepting bets")

    setattr(participation, 'bet', participation_bet.bet)

    previous_status = getattr(game, 'status')
    setattr(game, 'status', await evaluate_game_status(game, db))

    if previous_status == GameStatus.READY and getattr(game, 'status') == GameStatus.PLAYING:
        await start_round(game, db)
        await db.refresh(participation)

    return ParticipationRead(**participation.__dict__)
