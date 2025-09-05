"""Enums for standardization"""
import enum


class CardSuit(enum.Enum):
    """Card suits"""
    HEARTS = "hearts"
    CLUBS = "clubs"
    DIAMONDS = "diamonds"
    SPADES = "spades"


class CardRank(enum.Enum):
    """Card ranks"""
    ACE = "ace"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "jack"
    QUEEN = "queen"
    KING = "king"


class CardLocation(enum.Enum):
    """Card location types"""
    DECK = "deck"
    DEALER_HAND = "dealer_hand"
    PLAYER_HAND = "player_hand"
    DISCARD = "discard"


class GameStatus(enum.Enum):
    """Game statuses"""
    READY = "ready"
    PLAYING = "playing"
    FINISHED = "finished"


class GameVariant(enum.Enum):
    """Game variants"""
    ONE_DECK = "one_deck"
    TWO_DECKS = "two_decks"


class ParticipationStatus(enum.Enum):
    """Participation statuses"""
    PLAYING = "playing"
    QUIT = "quit"
