import pytest

from game.card import Card
from game.exceptions import IllegalStrategyException
from game.player import Player, TakenCards
from game.table import Table


CARD_POINTS_SUM = 22


@pytest.fixture
def table() -> Table:
    t = Table()
    t.last = Card(0)    # Last card is A♠

    # Place cards 1-4 (2♠, 3♠, 4♠, 5♠) onto the table.
    for i in range(4):
        t.place(Card(i + 1))

    return t


class MinimalPlayer(Player):
    def strategy(self, table: Table) -> tuple[Card, TakenCards]:
        return Card(0), []


class TestPlayerInitialize(object):
    def test_unimplemented(self) -> None:
        class IncompletePlayer(Player): ...

        with pytest.raises(TypeError):
            Player()
        with pytest.raises(TypeError):
            IncompletePlayer()

    def test_implemented(self) -> None:
        player = MinimalPlayer()

        assert player._clears == 0
        assert player._collection == []
        assert player._hand == []


class TestPlayerReceiveCards(object):
    @pytest.mark.parametrize("ncards", [0, 1, 3])
    def test_receive_empty_hand(self, ncards: int, table) -> None:
        cards = [Card(i) for i in range(ncards)]
        player = MinimalPlayer()
        player.receive_cards(cards)
        assert player._hand == cards

    @pytest.mark.parametrize("ncards", [0, 1, 3])
    def test_receive_not_empty_hand(self, ncards: int, table) -> None:
        player = MinimalPlayer()
        player._hand = [Card(i) for i in range(ncards)]
        player.receive_cards(Card(i) for i in range(ncards, 2 * ncards))
        assert player._hand == [Card(i) for i in range(2 * ncards)]


class TestPlayerReset(object):
    def test_reset(self) -> None:
        player = MinimalPlayer()
        player._clears = 1
        player._collection = [Card(0)]
        player._hand = [Card(0)]
        player.reset()

        assert player._clears == 0
        assert player._collection == []
        assert player._hand == []


class TestPlayerScore(object):
    def test_no_cards_no_clears(self) -> None:
        assert MinimalPlayer().score == 0

    def test_cards_standard(self) -> None:
        cards = [Card(i) for i in range(52)]
        player = MinimalPlayer()

        for card in cards:
            if card.score == 0:
                player._collection.append(card)

        assert player.score == 0
        player._clears = 4
        assert player.score == 4

    def test_cards_with_points(self) -> None:
        cards = [Card(i) for i in range(52)]
        player = MinimalPlayer()

        for card in cards:
            if card.score > 0:
                player._collection.append(card)

        assert player.score == CARD_POINTS_SUM
        player._clears = 4
        assert player.score == CARD_POINTS_SUM + 4


class TestPlayerPlay(object):
    def test_play_illegal_not_in_hand(self, table) -> None:
        class IllegalStrategyPlayer(Player):
            def strategy(self, table: Table) -> tuple[Card, TakenCards]:
                return Card(0), []

        with pytest.raises(IllegalStrategyException):
            IllegalStrategyPlayer().play(table)

    def test_play_illegal_not_collection(self, table) -> None:
        class IllegalStrategyPlayer(Player):
            def strategy(self, table: Table) -> tuple[Card, TakenCards]:
                return Card(0), Card(1)

        player = IllegalStrategyPlayer()
        player.receive_cards([Card(0)])

        with pytest.raises(IllegalStrategyException):
            player.play(table)

    def test_play_illegal_not_collection_collection(self, table) -> None:
        class IllegalStrategyPlayer(Player):
            def strategy(self, table: Table) -> tuple[Card, TakenCards]:
                return Card(0), [Card(1)]

        player = IllegalStrategyPlayer()
        player.receive_cards([Card(0)])

        with pytest.raises(IllegalStrategyException):
            player.play(table)

    def test_play_illegal_move(self, table) -> None:
        class IllegalStrategyPlayer(Player):
            def strategy(self, table: Table) -> tuple[Card, TakenCards]:
                return Card(0), [[Card(1)]]

        player = IllegalStrategyPlayer()
        player.receive_cards([Card(0)])

        with pytest.raises(Exception):
            player.play(table)

    def test_play_legal_place(self, table) -> None:
        class PlaceOnlyPlayer(Player):
            def strategy(self, table: Table) -> tuple[Card, TakenCards]:
                return self._hand[0], []

        played = Card(0)
        player = PlaceOnlyPlayer()
        player.receive_cards([played])
        player.play(table)

        assert player._clears == 0
        assert player._collection == []
        assert player._hand == []

        assert played in table.cards
        assert played in table.history

    def test_play_legal_take(self, table) -> None:
        played = Card(14)   # 2♥
        taken = Card(1)     # 2♠

        class Take2SpadePlayer(Player):
            def strategy(self, table: Table) -> tuple[Card, TakenCards]:
                return played, [[taken]]

        player = Take2SpadePlayer()
        player.receive_cards([played])
        player.play(table)

        assert player._clears == 0
        assert player._hand == []
        assert played in player._collection
        assert taken in player._collection

        assert taken not in table.cards
        assert played in table.history

    def test_play_legal_take_all(self, table) -> None:
        class TakeAllPlayer(Player):
            def strategy(self, table: Table) -> tuple[Card, TakenCards]:
                return Card(6), [[Card(1), Card(4)], [Card(2), Card(3)]]

        played = Card(6)    # 7♠ to take everything.
        player = TakeAllPlayer()
        player.receive_cards([played])
        player.play(table)

        assert player._clears == 1
        assert player._hand == []

        for i in [1, 2, 3, 4, 6]:
            assert Card(i) in player._collection

        assert table.cards == []
        assert played in table.history
