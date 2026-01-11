import itertools
import pytest

from game.card import Card
from game.exceptions import IllegalMoveException, IllegalStateException
from game.table import Table


@pytest.fixture
def table() -> Table:
    t = Table()
    t.last = Card(0)

    # Place cards 1-4 (2, 3, 4, 5 of spades) onto the table.
    for i in range(4):
        t.place(Card(i + 1))

    return t


class TestTableInitialize(object):
    def test_initialize(self, table) -> None:
        table = Table()

        assert table.cards == []
        assert table.history == []
        assert table.last is None


class TestTablePlace(object):
    def test_legal(self) -> None:
        cards = [Card(i) for i in range(52)]
        table = Table()

        for card in cards:
            table.place(card)

            assert table.cards[-1] == card
            assert table.history[-1] == card

    def test_illegal_state_already_on_table(self):
        table = Table()
        table.place(Card(0))

        with pytest.raises(IllegalStateException):
            table.place(Card(0))

    def test_illegal_state_already_played(self):
        table = Table()
        table.history.append(Card(0))

        with pytest.raises(IllegalStateException):
            table.place(Card(0))


class TestTableReset(object):
    def test_reset(self, table) -> None:
        assert table.cards == [Card(i + 1) for i in range(4)]
        assert table.history == table.cards
        assert table.last == Card(0)

        table.reset()

        assert table.cards == []
        assert table.history == []
        assert table.last is None


class TestTableTake(object):
    def test_illegal_own_card(self, table) -> None:
        with pytest.raises(IllegalMoveException):
            table.take(Card(0), [])

        with pytest.raises(IllegalMoveException):
            table.take(Card(0), [[]])

        with pytest.raises(IllegalMoveException):
            table.take(Card(0), [[], []])

    def test_illegal_played_and_taken(self, table) -> None:
        with pytest.raises(IllegalMoveException):
            table.take(Card(0), [[Card(0)]])

    def test_illegal_not_on_table(self, table) -> None:
        with pytest.raises(IllegalMoveException):
            table.take(Card(0), [[Card(51)]])

    def test_illegal_repeated_card(self, table) -> None:
        flat = [[Card(1), Card(2), Card(1)]]
        nest = [[card] for card in flat[0]]

        with pytest.raises(IllegalMoveException):
            table.take(Card(0), flat)

        with pytest.raises(IllegalMoveException):
            table.take(Card(0), nest)

    def test_illegal_too_many_cards(self, table) -> None:
        ncards = len(table.cards) + 1
        cards_flat = [[Card(i+1) for i in range(ncards)]]
        cards_nest = [[Card(i+1)] for i in range(ncards)]

        with pytest.raises(IllegalMoveException):
            table.take(Card(0), cards_flat)

        with pytest.raises(IllegalMoveException):
            table.take(Card(0), cards_nest)

    def test_illegal_invalid_sum(self, table) -> None:
        with pytest.raises(IllegalMoveException):
            table.take(Card(0), [[Card(1)]])

    def test_valid_single_same(self) -> None:
        table = Table()

        for i in range(52):
            played, taken = Card(i), Card((i + 13) % 52)

            table.place(taken)
            cards, cleared = table.take(played, [[taken]])

            assert cards == [played, taken]
            assert cleared
            assert len(table.cards) == 0
            assert table.history[-1] == played
            table.reset()

    def test_valid_multiple_same(self) -> None:
        table = Table()

        for i in range(52):
            played = Card(i)
            taken = [Card((i + j*13) % 52) for j in range(1, 4)]

            for card in taken:
                table.place(card)

            cards, cleared = table.take(played, [[c] for c in taken])
            assert cards == [played, *taken]
            assert cleared
            assert len(table.cards) == 0
            assert table.history[-1] == played
            table.reset()

    @pytest.mark.parametrize("played,taken", [(
        # 5spade = 2spade + 3spade [simple sum]
        Card(4),
        ((Card(1), Card(2),),),
    ), (
        # 5spade = 2spade + 3spade = 2heart + 3heart [multiple sum]
        Card(4),
        (
            (Card(1), Card(2),),
            (Card(14), Card(15),),
        ),
    ), (
        # 5spade = 2spade + 3spade = 2heart + 3heart = 5heart [sum, take]
        Card(4),
        (
            (Card(1), Card(2),),
            (Card(14), Card(15),),
            (Card(17),),
        ),
    ), (
        # Aspade = 10spade + Aheart [ace 1 and 11]
        Card(0),
        ((Card(9), Card(13)),),
    ), (
        # Aspade = Aheart = Adiamond = Aclub
        Card(0),
        ((Card(13),), (Card(26),), (Card(39),),),
    )])
    def test_valid_sums(self, played: Card, taken: tuple) -> None:
        flat = list(itertools.chain.from_iterable(taken))

        table = Table()
        for card in flat:
            table.place(card)

        cards, cleared = table.take(played, taken)
        assert cards == [played, *flat]
        assert cleared
        assert len(table.cards) == 0
        assert table.history[-1] == played

    def test_valid_cards_remain(self) -> None:
        table = Table()
        table.cards = [Card(i+1) for i in range(13)]

        cards, cleared = table.take(Card(0), [[Card(13)]])
        assert cards == [Card(0), Card(13)]
        assert not cleared
        assert table.cards == [Card(i+1) for i in range(12)]
        assert table.history == [Card(0)]
