"""Blackjack game logic"""
import random
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Game, Participation, PhysicalCard, GameCard
from app.enums import GameStatus, ParticipationStatus, CardLocation


async def initialize_decks(game: Game, db: AsyncSession) -> None:
    """Initialize cards for a game"""
    if getattr(game, 'status') != GameStatus.READY:
        return

    # Check if there is any game_card for this game
    game_cards = await db.scalars(
        select(GameCard).where(GameCard.game_id == game.id)
    )
    if list(game_cards):
        return

    # Get all physical cards
    physical_cards = list(await db.scalars(
        select(PhysicalCard).where(PhysicalCard.deck_number == 1)
    ))

    # Create game cards
    for i, physical_card in enumerate(physical_cards):
        print(i, physical_card.id)
        game_card = GameCard(
            game_id=game.id,
            physical_card_id=physical_card.id,
            location_type=CardLocation.DECK,
            holder_id=None,
            position=i
        )
        db.add(game_card)
    await db.commit()
    await shuffle_deck(game, db)


def evaluate_game_status(game: Game, participations: list[Participation]) -> GameStatus:
    """Evaluate game status depending on participations"""

    # Game cannot be reopened
    if getattr(game, 'status') == GameStatus.FINISHED:
        return GameStatus.FINISHED

    # Close the game when all participants have quit
    if all(getattr(participation, 'status') == ParticipationStatus.QUIT
           for participation in participations):
        return GameStatus.FINISHED

    # Set the game as playing when all participants have placed a bet
    active_participations = [
        participation for participation in participations
        if getattr(participation, 'status') == ParticipationStatus.PLAYING
    ]

    if all(getattr(participation, 'bet') > 0
           for participation in active_participations):
        return GameStatus.PLAYING

    # Otherwise, the game is pending
    return GameStatus.READY


async def shuffle_deck(game: Game, db: AsyncSession) -> None:
    """Shuffle the game deck"""
    game_cards = list(await db.scalars(
        select(GameCard).where(GameCard.game_id ==
                               game.id and GameCard.location_type == CardLocation.DECK)
    ))
    random.shuffle(game_cards)

    for i, game_card in enumerate(game_cards):
        setattr(game_card, "position", i)
    await db.commit()


async def deal_initial_hands(
        game: Game, participations: list[Participation], db: AsyncSession) -> None:
    """Deal intial hands to participants and dealer"""
    # Get the decks and distribute 2 random cards to each player
    game_cards = list(await db.scalars(
        select(GameCard)
        .where(GameCard.game_id ==
               game.id and GameCard.location_type == CardLocation.DECK)
        .order_by(GameCard.position)
    ))
    for participation in participations:
        for _ in range(2):
            game_card = game_cards.pop()
            setattr(game_card, 'holder_id', participation.id)
            setattr(game_card, 'location_type', CardLocation.PLAYER_HAND)
    await db.commit()
