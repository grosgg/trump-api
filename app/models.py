"""Database models"""
import uuid
from datetime import datetime, timezone

from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import Column, ForeignKey, UniqueConstraint, Uuid, DateTime, Integer, String, Enum
from sqlalchemy.orm import DeclarativeBase

from app.enums import GameStatus, GameVariant, ParticipationStatus, CardSuit, CardRank, CardLocation


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models"""
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    """User table based on FastAPI-Users"""
    __tablename__ = "users"

    created_at = Column(DateTime(timezone=True), nullable=False,
                        default=lambda: datetime.now(timezone.utc))
    cash = Column(Integer, nullable=False, default=0)


class Game(Base):
    """Game table"""
    __tablename__ = "games"

    id = Column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    variant = Column(Enum(GameVariant), nullable=False,
                     default=GameVariant.ONE_DECK)
    status = Column(Enum(GameStatus), nullable=False,
                    default=GameStatus.READY)
    hands_played = Column(Integer, nullable=False, default=0)
    bank = Column(Integer, nullable=False, default=1000)
    created_at = Column(DateTime(timezone=True), nullable=False,
                        default=lambda: datetime.now(timezone.utc))


class Participation(Base):
    """Participation table"""
    __tablename__ = "participations"

    id = Column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    position = Column(Integer, nullable=False, default=0)
    status = Column(Enum(ParticipationStatus), nullable=False,
                    default=ParticipationStatus.PLAYING)
    bet = Column(Integer, nullable=False, default=0)
    cash = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False,
                        default=lambda: datetime.now(timezone.utc))
    game_id = Column(Uuid, ForeignKey(
        "games.id", ondelete="SET NULL"))
    user_id = Column(Uuid, ForeignKey(
        "users.id", ondelete="SET NULL"))


class PhysicalCard(Base):
    """Physical Card table"""
    __tablename__ = "physical_cards"

    id = Column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    suit = Column(Enum(CardSuit), nullable=False)
    rank = Column(Enum(CardRank), nullable=False)
    deck_number = Column(Integer, nullable=False)

    UniqueConstraint("suit", "rank", "deck_number")


class GameCard(Base):
    """Game Card table"""
    __tablename__ = "game_cards"

    id = Column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    game_id = Column(Uuid, ForeignKey(
        "games.id", ondelete="SET NULL"))
    physical_card_id = Column(Uuid, ForeignKey(
        "physical_cards.id", ondelete="SET NULL"))
    location_type = Column(Enum(CardLocation), nullable=False)
    holder_id = Column(Uuid, nullable=True)
    position = Column(Integer, nullable=False, default=0)
