import pytest

from game.card import Card, Deck


DEFAULT_LEN = 52
DEFAULT_DRAW = 3
DEFAULT_CARDS = [Card(i) for i in range(DEFAULT_LEN)]


@pytest.fixture
def deck() -> Deck:
    return Deck()


class TestDeckInitialize(object):
    def test_valid(self, deck) -> None:
        assert deck._cards == [Card(i) for i in range(DEFAULT_LEN)]


class TestDeckDataModel(object):
    def test_str(self, deck) -> None:
        suits = "♠♥♣♦"
        values = list("A23456789") + ["10"] + list("JQK")
        expected = [f"[{v}{s}]" for s in suits for v in values]
        assert str(deck) == "".join(expected)


class TestDeckCutAndDraw(object):
    @pytest.mark.parametrize("n", [-1, 0, DEFAULT_LEN + 1])
    def test_invalid(self, n: int, deck) -> None:
        with pytest.raises(ValueError):
            deck.draw(n)

    def test_cut_and_draw(self, deck) -> None:
        drawn = deck.cut_and_draw(4)
        cut_index = deck._cards[0]._id

        assert drawn == tuple(Card(cut_index - i) for i in range(4, 0, -1))
        assert len(deck._cards) == DEFAULT_LEN - 4

        expected_cards = [Card(i) for i in range(cut_index, DEFAULT_LEN)]
        expected_cards += [Card(i) for i in range(cut_index - 4)]
        assert deck._cards == expected_cards


class TestDeckDraw(object):
    @pytest.mark.parametrize("n", [-1, 0, DEFAULT_LEN + 1])
    def test_invalid(self, n: int, deck) -> None:
        with pytest.raises(ValueError):
            deck.draw(n)

    @pytest.mark.parametrize("n", [1, 13, DEFAULT_DRAW, DEFAULT_LEN])
    def test_draw_n(self, n: int, deck) -> None:
        drawn = deck.draw(n)
        assert len(deck._cards) == DEFAULT_LEN - n
        assert drawn == tuple(Card(DEFAULT_LEN - i - 1) for i in range(n))

        for card in drawn:
            assert card not in deck._cards


class TestDeckReset(object):
    def test_reset(self, deck) -> None:
        deck._cards = []
        assert deck._cards != DEFAULT_CARDS
        deck.reset()
        assert deck._cards == DEFAULT_CARDS


class TestDeckShuffle(object):
    def test_shuffle(self, deck) -> None:
        deck.shuffle()
        assert len(deck._cards) == DEFAULT_LEN
        assert deck._cards != DEFAULT_CARDS

        for i in range(DEFAULT_LEN):
            assert Card(i) in deck._cards
