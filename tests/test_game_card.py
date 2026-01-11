import itertools
import pytest

from game.card import Card


class TestCardInitialize(object):
    def test_invalid(self) -> None:
        with pytest.raises(ValueError):
            Card(-1)
        with pytest.raises(ValueError):
            Card(52)

    def test_valid(self) -> None:
        for i in range(52):
            card = Card(i)
            assert card._id == i


class TestCardDataModel(object):
    def test_eq(self) -> None:
        assert Card(0) == Card(0)
        assert Card(0) == 0
        assert Card(0) != Card(1)
        assert Card(0) != 1

    def test_str(self) -> None:
        suits = "♠♥♣♦"
        values = list("A23456789") + ["10"] + list("JQK")
        expected_values = itertools.product(suits, values)

        for i, (suit, value) in enumerate(expected_values):
            assert str(Card(i)) == f"[{value}{suit}]"


class TestCardScore(object):
    SPECIAL_CASES = (27, 48,)   # 2♣ and 10♦ respectively.

    def test_score_standard(self) -> None:
        for i in range(52):
            if i in self.SPECIAL_CASES:
                continue

            card = Card(i)

            if 0 < i % 13 < 9:
                assert card.score == 0
            else:
                assert card.score == 1

    def test_score_special_2club(self) -> None:
        assert Card(27).score == 1

    def test_score_special_10diamond(self) -> None:
        assert Card(48).score == 2


class TestCardValue(object):
    def test_value(self) -> None:
        for i in range(52):
            card = Card(i)

            if i % 13 == 0:
                assert card.value == (1, 11,)
