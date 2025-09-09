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
            suit=physical_card.suit,
            rank=physical_card.rank,
            game_id=game.id,
            physical_card_id=physical_card.id,
            location_type=CardLocation.DECK,
            holder_id=None,
            position=i
        )
        db.add(game_card)
    await db.commit()
    await shuffle_deck(game, db)


async def evaluate_game_status(game: Game, db: AsyncSession) -> GameStatus:
    """Evaluate game status depending on participations"""

    participations = await db.scalars(
        select(Participation).where(Participation.game_id == game.id))

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

    # Otherwise, the game is ready
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


async def start_round(game: Game, db: AsyncSession) -> None:
    """Start a new round"""
    participations = await db.scalars(
        select(Participation).where(Participation.game_id == game.id))

    setattr(game, 'hands_played', game.hands_played + 1)
    await db.commit()
    await deal_initial_hands(game, list(participations), db)


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

    # Distribute 2 cards to each player
    for participation in participations:
        for _ in range(2):
            game_card = game_cards.pop()
            setattr(game_card, 'holder_id', participation.id)
            setattr(game_card, 'location_type', CardLocation.PLAYER_HAND)

    # Distribute 2 cards to the dealer
    for _ in range(2):
        game_card = game_cards.pop()
        setattr(game_card, 'holder_id', game.id)
        setattr(game_card, 'location_type', CardLocation.DEALER_HAND)
    await db.commit()

    await check_naturals(game, participations, db)


async def check_naturals(game: Game, participations: list[Participation], db: AsyncSession) -> None:
    """Check for naturals"""
    dealer_hand = list(await db.execute(
        select(GameCard.id, PhysicalCard.rank)
        .join(PhysicalCard, GameCard.physical_card_id == PhysicalCard.id)
        .where(GameCard.game_id == game.id)
        .where(GameCard.location_type == CardLocation.DEALER_HAND)
        .where(GameCard.holder_id == game.id)
    ))

    for participation in participations:
        player_hand = list(await db.execute(
            select(GameCard.id, PhysicalCard.rank)
            .join(PhysicalCard, GameCard.physical_card_id == PhysicalCard.id)
            .where(GameCard.game_id == game.id)
            .where(GameCard.location_type == CardLocation.PLAYER_HAND)
            .where(GameCard.holder_id == participation.id)
        ))


def hand_value(hand: list[GameCard]) -> int:
    """Calculate the value of a hand"""
