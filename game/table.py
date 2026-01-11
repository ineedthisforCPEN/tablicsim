"""
game/table.py

This file defines the `Table` class. This class defines the common play
area for the game and enforces the rules of Tablić.
"""

import itertools
import math

from collections.abc import Collection, Iterable

from .card import Card


TakenCards = Collection[Collection[Card]]


class IllegalMoveException(ValueError): ...


class IllegalStateException(ValueError): ...


class Table(object):
    def __init__(self) -> None:
        self.reset()

    def __str__(self) -> str:
        return "".join(str(c) for c in self.cards)

    def _cards_sum_to(self, cards: TakenCards, values: tuple[int, ...]) -> bool:
        for card_values in itertools.product(*[card.value for card in cards]):
            if sum(card_values) in values:
                return True
        return False

    def _validate_game_state(self, card: Card) -> None:
        if card in self.cards:
            raise IllegalStateException(f"{card} already on table - {self}")
        if card in self.history:
            raise IllegalStateException(f"{card} already played")

    def place(self, card: Card) -> None:
        self._validate_game_state(card)
        self.cards.append(card)
        self.history.append(card)

    def reset(self) -> None:
        self.cards = []
        self.history = []
        self.last = None

    def show_table(self) -> str:
        n = math.ceil(math.sqrt(len(self.cards)))
        header = "[EMPTY TABLE]" if n == 0 else "[TABLE]"

        print(f"{header} -- LAST: {self.last or 'None'}")
        for i, card in enumerate(self.cards):
            print(f"{str(card):>6s}")
            if i % n == n - 1:
                print()

    def take(self, played: Card, taken: TakenCards) -> tuple[Iterable[Card], bool]:
        """
        Play a given card (`played`) and collect the cards in `taken`.
        The `taken` variable is a collection of a collection of cards.
        Each sub-collection will be checked against `played` to make
        sure their value(s) sum up to the value of `played`.

        This method should be used by `Player` implementations to
        interact with the table. The table ensures that the following
        game rules are followed:

            RULE 1: There must be at least one card in `taken`.

            RULE 2: The `played` card cannot be in `taken`.

            RULE 3: Each card in `taken` must be on the table.

            RULE 4: Each card in `taken` must be unique.

            RULE 5: The sum of each collection of cards in `taken` must
                    equal the value of `played`.

        :param played: The card played by a `Player`.
        :param taken: The card(s) taken by a `Player`.
        :returns: A tuple with two items. The first item is an
        interable that contains all cards a user can add to their
        collection. The second item is a boolean that is True if the
        `Table` is cleared, and False otherwise.
        :raises IllegalMoveException: The move causes an illegal game
        state. This is likely the fault of the simulator.
        :raises IllegalMoveException: The move is not allowed by the
        game rules. This is likely the fault of the player.
        """
        self._validate_game_state(played)
        flat = list(itertools.chain.from_iterable(taken))

        # RULE 1
        if len(flat) < 1:
            raise IllegalMoveException("player cannot take own card")

        # RULE 2
        if played in flat:
            raise IllegalMoveException(f"card {played} played and taken")

        # RULE 3, 4
        if len(flat) > len(self.cards):
            raise IllegalMoveException(
                "player cannot take more cards than are on the table."
            )

        for i, card in enumerate(flat):
            # RULE 3
            if card not in self.cards:
                raise IllegalMoveException(f"{card} not on table - {self}")

            # RULE 4
            if card in flat[i + 1:]:
                raise IllegalMoveException(f"took card {card} more than once")

        # RULE 5
        for cards in taken:
            if not self._cards_sum_to(cards, played.value):
                cards = "".join(str(c) for c in self.cards)
                raise IllegalMoveException(f"cannot take {cards} with {played}")

        # Make sure we track `played` in our game history and remove any taken
        # cards from the table.
        self.history.append(played)
        for card in flat:
            self.cards.remove(card)

        cleared = bool(len(self.cards) == 0)
        return [played, *flat], cleared
