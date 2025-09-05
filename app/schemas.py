"""API schemas"""
import uuid

from datetime import datetime
from pydantic import BaseModel
from pydantic.types import PositiveInt
from fastapi_users import schemas

from app.enums import GameVariant, GameStatus, ParticipationStatus


class UserRead(schemas.BaseUser[uuid.UUID]):
    created_at: datetime
    cash: int


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass


class UserCharge(BaseModel):
    amount: PositiveInt


class GameRead(BaseModel):
    id: uuid.UUID
    variant: GameVariant
    status: GameStatus
    hands_played: int
    bank: int
    # dealer_hand: str
    created_at: datetime


class GameCreate(BaseModel):
    variant: GameVariant


class ParticipationRead(BaseModel):
    id: uuid.UUID
    position: int
    status: ParticipationStatus
    bet: int
    cash: int
    # hand: str
    created_at: datetime
    game_id: uuid.UUID
    user_id: uuid.UUID


class ParticipationCreate(BaseModel):
    cash: int
    game_id: uuid.UUID


class ParticipationBet(BaseModel):
    bet: int
