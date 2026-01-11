"""
game/player.py

This file defines the base `Player` class. Each player manages their
own state (the cards they carry) and their play strategy.
"""

from abc import ABC, abstractmethod
from collections.abc import Collection, Iterable

from .card import Card
from .exceptions import IllegalStrategyException
from .table import Table


TakenCards = Collection[Collection[Card]]


class Player(ABC):
    def __init__(self) -> None:
        self.reset()

    def play(self, table: Table) -> None:
        play, take = self.strategy(table)

        if play not in self._hand:
            raise IllegalStrategyException(f"Cannot play {play}: not in hand.")
        if not isinstance(take, Collection):
            raise IllegalStrategyException(f"Cannot take {type(take)}.")
        if not all(isinstance(sub, Collection) for sub in take):
            taketype = ",".join(str(type(sub)) for sub in take)
            raise IllegalStrategyException(f"Cannot take [{taketype}].")

        self._hand.remove(play)

        if len(take) == 0 or all(len(cards) == 0 for cards in take):
            table.place(play)
        else:
            collected, cleared = table.take(play, take)
            self._clears += int(cleared)
            self._collection.extend(collected)

    def receive_cards(self, cards: Iterable[Card]) -> None:
        self._hand.extend(cards)

    def reset(self) -> None:
        """Reset the player to their original state."""
        self._clears = 0        # Number of times this player cleared a table.
        self._collection = []   # The cards collected during play.
        self._hand = []         # The cards currently in the player's hand.

    @property
    def score(self) -> int:
        return self._clears + sum(card.score for card in self._collection)

    @abstractmethod
    def strategy(self, table: Table) -> tuple[Card, TakenCards]:
        """
        Each player must define a strategy which determines which
        `Card` to play based on the player's current hand, the current
        `Table` state, and possibly the total game history. The player
        MUST ALWAYS play a single card. Players should ensure their
        move is legal, though the table will enforce this and stop a
        game for any illegal move.

        The strategy should determine which cards the player wants to
        take during their turn - a collection of a collection of cards.
        Each sub-collection contains unique cards on the `table` that
        constitue a legal move. A single `Card` can take multiple sub-
        collections of cards: for example, an ACE can take the sub-
        collections [A♠] and [2♥,9♣]. If legal, all of the cards
        can be collected. If the collection of sub-collections is
        empty, then the player will simply place their card on the
        table and not collect anythying.

        :param table: The table showing which cards can be taken and
        which cards have been played throughout the game.
        :returns: Returns a tuple with two items. The first is the card
        played by a player, the second is the collection of collection
        of cards the player wants to take.
        """
        ...
