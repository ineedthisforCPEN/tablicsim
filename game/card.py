"""
game/cards.py

This file defines a `Card` from a French deck of cards[^0] and some
helper enumerations.

The `score` of a card is used to calculate a team's overall game score,
while the `value` of a card is used to determine which `Card`(s) it can
pick up (if any) during play.

References:
    [0] https://en.wikipedia.org/wiki/French-suited_playing_cards
"""

from enum import StrEnum
from typing import Any, Iterable


class CardSuit(StrEnum):
    SPADE = "♠"
    HEART = "♥"
    CLUB = "♣"
    DIAMOND = "♦"


class CardValue(StrEnum):
    ACE = "A"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"


class Card(object):
    __slots__ = ("_id", "_value", "_suit", "score", "value")

    def __init__(self, id: int) -> None:
        if id < 0:
            raise ValueError(f"Invalid card '{id}' - cannot be negative.")

        idx_suit = (id // len(CardValue)) % len(CardSuit)
        idx_value = id % len(CardValue)

        self._id = id
        self._suit = list(CardSuit)[idx_suit]
        self._value = list(CardValue)[idx_value]

        self.score = self._calculate_score()
        self.value = self._calculate_value()

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Card):
            return self._id == other._id
        return self._id == other

    def __repr__(self) -> str:
        return f"Card({self._value!r}{self._suit!r})"

    def __str__(self) -> str:
        return f"[{self._value}{self._suit}]"

    def _calculate_score(self) -> int:
        match self._value, self._suit:
            case "10", CardSuit.DIAMOND:
                return 2    # SPECIAL CASE: 10♦ has a score of 2
            case "2", CardSuit.CLUB:
                return 1    # SPECIAL CASE: 2♣ has a score of 1
            case card, _ if card in ["A", "10", "J", "Q", "K"]:
                return 1    # All aces, tens, or face cards have a score of 1
            case _:
                return 0    # All other cards have a score of 0

    def _calculate_value(self) -> Iterable[int]:
        match self._value, self._suit:
            case "A", _:
                return (1, 11,)     # Aces can have a value of 1 or 11.
            case card, _ if card in "JQK":
                valuemap = {"J": 12, "Q": 13, "K": 14}
                return (valuemap[card],)
            case _:
                return (int(card.value),)
