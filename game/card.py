"""
game/cards.py

This file defines a `Card` class that makes up a `Deck` class which
represents a French deck of cards [^0]. Each `Card` will have a Tablić
`value` and `score` used to tabulate overall player score.

References:
    [0] https://en.wikipedia.org/wiki/French-suited_playing_cards
"""

import random

from typing import Any, Iterable


_CARD_SCORE = [
#   A, 2, 3, 4, 5, 6, 7, 8, 9, 10, J, Q, K
    1, 0, 0, 0, 0, 0, 0, 0, 0,  1, 1, 1, 1,  # Spades
    1, 0, 0, 0, 0, 0, 0, 0, 0,  1, 1, 1, 1,  # Hearts
    1, 1, 0, 0, 0, 0, 0, 0, 0,  1, 1, 1, 1,  # Clubs
    1, 0, 0, 0, 0, 0, 0, 0, 0,  2, 1, 1, 1,  # Diamonds
]
_CARD_VALUES = 4 * [
    # Aces are 1 or 11 points.
    (1, 11),

    # Cards 2 through 9 have the same value as the card.
    (2,), (3,), (4,),  (5,),  (6,),  (7,), (8,), (9,), (10,),

    # Jacks, Queens, and Kings are valued 12, 13, and 14 respectively.
    (12,), (13,), (14,),
]

_CARDSTR_NUM = list("A23456789") + ["10"] + list("JQK")
_CARDSTR_SUIT = "♠♥♣♦"

_NCARDS = 52
_NSUITS = 4


assert len(_CARD_SCORE) == _NCARDS
assert len(_CARD_VALUES) == _NCARDS
assert len(_CARDSTR_NUM) * len(_CARDSTR_SUIT) == _NCARDS


class Card(object):
    def __init__(self, id: int) -> None:
        if id not in range(_NCARDS):
            raise ValueError(f"Invalid card '{id}'.")

        self._id = id
        self.score = _CARD_SCORE[id]
        self.value = _CARD_VALUES[id]

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Card):
            return self._id == other._id
        return self._id == other

    def __repr__(self) -> str:
        return f"Card({self.value!r}{self.suit!r})"

    def __str__(self) -> str:
        idx_suit = (self._id // (_NCARDS // _NSUITS)) % _NSUITS
        idx_value = self._id % (_NCARDS // _NSUITS)

        suit = _CARDSTR_SUIT[idx_suit]
        value = _CARDSTR_NUM[idx_value]
        return f"[{value}{suit}]"


class Deck(object):
    def __init__(self) -> None:
        self.reset()

    def _validate_can_draw(self, n: int) -> None:
        if n < 1:
            raise ValueError(f"must draw at least 1 card, not '{n}'.")

        ncards = len(self._cards)
        if n > ncards:
            raise ValueError(f"requested {n} cards, only {ncards} available.")

    def __str__(self) -> str:
        return "".join(str(card) for card in self._cards)

    def cut_and_draw(self, n: int) -> Iterable[Card]:
        """
        Cut the deck at a random location and draw `n` cards from the
        bottom of the cut half. Move the cut half of the deck to the
        bottom of the other half. The top of the other half becomes the
        top of the deck.

        :param n: Number of cards to draw.
        :returns: Returns an iterable with the drawn cards.
        """
        self._validate_can_draw(n)

        cut = random.randint(0, len(self._cards) - 1)
        self._cards = self._cards[-cut:] + self._cards[:-cut]

        return tuple(self._cards.pop(0) for _ in range(n))

    def draw(self, n: int) -> Iterable[Card]:
        """
        Draw `n` cards from the top of the deck.

        :param n: Number of cards to draw.
        :returns: Returns an iterable with the drawn cards.
        """
        self._validate_can_draw(n)
        return tuple(self._cards.pop() for _ in range(n))

    def reset(self) -> None:
        """
        Reset the deck so it has all of its original cards in order.
        """
        self._cards = [Card(i) for i in range(_NCARDS)]

    def shuffle(self) -> None:
        """Shuffle the current cards in the deck."""
        random.shuffle(self._cards)
