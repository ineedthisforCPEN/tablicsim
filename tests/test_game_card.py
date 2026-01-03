import itertools
import pytest

from game.card import Card, CardSuit, CardValue


CardSuits = list(CardSuit)
CardValues = list(CardValue)


class TestCardInitialize(object):
    def test_invalid(self) -> None:
        with pytest.raises(ValueError):
            Card(-1)

    def test_valid_single_deck(self) -> None:
        for i in range(52):
            card = Card(i)

            assert card._id == i
            assert card._suit == CardSuits[(i // 13) % 4]
            assert card._value == CardValues[i % 13]

    def test_valid_multi_deck(self) -> None:
        ndecks = [0, 1, 2, 100]

        for i in range(52):
            cards = [Card(52*n + i) for n in ndecks]

            for card, n in zip(cards, ndecks):
                assert card._id == 52*n + i
                assert card._suit == CardSuits[(i // 13) % 4]
                assert card._value == CardValues[i % 13]

            assert all(c._suit == cards[0]._suit for c in cards)
            assert all(c._value == cards[0]._value for c in cards)


class TestCardDataModel(object):
    def test_eq(self) -> None:
        assert Card(0) == Card(0) == 0
        assert Card(0) != Card(1) == 1
        assert Card(0) != Card(52) == 52

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

            if card._value in "23456789":
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

            if card._value == CardValue.ACE:
                assert card.value == (1, 11,)
            elif card._value == CardValue.JACK:
                assert card.value == (12,)
            elif card._value == CardValue.QUEEN:
                assert card.value == (13,)
            elif card._value == CardValue.KING:
                assert card.value == (14,)
            else:
                assert card.value == (int(card._value.value),)
