from pytest import raises, mark
from rangeparser import *


# from worse to best (suit matter)
DEUCE_COMBOS = (
    Combo('2d2c'), Combo('2h2c'), Combo('2h2d'),
    Combo('2s2c'), Combo('2s2d'), Combo('2s2h')
)

THREE_COMBOS = (
    Combo('3d3c'), Combo('3h3c'), Combo('3h3d'),
    Combo('3s3c'), Combo('3s3d'), Combo('3s3h')
)

# from worse to best (suit matter)
TEN_COMBOs = (
    Combo('TdTc'), Combo('ThTc'), Combo('ThTd'),
    Combo('TsTc'), Combo('TsTd'), Combo('TsTh')
)


class TestHandsResultsAfterParse:
    def test_pairs_simple(self):
        assert Range('22').hands == (Hand('22'),)
        assert Range('22').combos == DEUCE_COMBOS

    def test_combo_simple(self):
        assert Range('2s2c').hands == (Hand('22'),)
        assert Range('2s2c').combos == (Combo('2c2s'),)

    def test_pairs_multiple(self):
        assert Range('22 33').hands == (Hand('22'), Hand('33'))
        assert Range('33 22').hands == (Hand('22'), Hand('33'))

    def test_pairs_with_plus(self):
        assert Range('88+').hands == (Hand('88'), Hand('99'), Hand('TT'), Hand('JJ'), Hand('QQ'),
                                      Hand('KK'), Hand('AA'))
        assert Range('22+').hands == PAIR_HANDS

    def test_pairs_with_dash(self):
        assert Range('22-55').hands == (Hand('22'), Hand('33'), Hand('44'), Hand('55'))
        assert Range('22-33').hands == (Hand('22'), Hand('33'))

    def test_pairs_with_dash_reverse(self):
        assert Range('55-22').hands == (Hand('22'), Hand('33'), Hand('44'), Hand('55'))
        assert Range('33-22').hands == (Hand('22'), Hand('33'))

    def test_multiple_offsuit_hands(self):
        assert Range('AKo 84o').hands == (Hand('84o'), Hand('AKo'))

    def test_hands_without_suit(self):
        assert Range('AK 48').hands == (Hand('84o'), Hand('84s'), Hand('AKo'), Hand('AKs'))

    def test_dash_offsuit(self):
        assert Range('J8o-J4o').hands == (Hand('J4o'), Hand('J5o'), Hand('J6o'),
                                          Hand('J7o'), Hand('J8o'))

    def test_dash_suited(self):
        assert Range('J8s-J4s').hands == (Hand('J4s'), Hand('J5s'), Hand('J6s'),
                                          Hand('J7s'), Hand('J8s'))

    def test_pairs_backward(self):
        assert Range('44-').hands == (Hand('22'), Hand('33'), Hand('44'))

    def test_empty_range(self):
        assert Range().hands == tuple()
        assert Range().combos == tuple()

        assert Range('').hands == tuple()
        assert Range('').combos == tuple()


class TestCombosResultsAfterParse:
    def test_pairs_simple(self):
        """Test if pairs get all the combos."""
        assert Range('22').combos == DEUCE_COMBOS

    def test_pairs_multiple(self):
        assert Range('22 33').combos == DEUCE_COMBOS + THREE_COMBOS

    def test_pairs_with_dash(self):
        assert Range('22-33').combos == DEUCE_COMBOS + THREE_COMBOS

    def test_pairs_with_dash_are_equal_with_spaces(self):
        assert Range('22-33').combos == Range('22 33').combos
        assert Range('55-33').combos == Range('33 44 55').combos


class TestCaseInsensitive:
    def test_pairs(self):
        assert Range('aA') == Range('AA')
        assert Range('TT') == Range('tt')

    def test_offsuit(self):
        assert Range('AkO') == Range('AKo')

    def test_suited(self):
        assert Range('AKs') == Range('kaS')


class TestPercentages:
    def test_one_pair(self):
        assert Range('22').percent == 0.45

    def test_one_suited_card(self):
        assert Range('AKs').percent == 0.3

    def test_one_offsuit_card(self):
        assert Range('Ako').percent == 0.9

    def test_pair_range(self):
        assert Range('88+').percent == 3.17

    def test_pair_and_offsuit(self):
        assert Range('22 AKo').percent == 1.36

    def test_full_range(self):
        assert Range('XX').percent == 100


class TestNumberOfCombos:
    """Test number of hand combos by suits."""

    def test_one_pair(self):
        assert len(Range('22')) == 6
        assert len(Range('QQ')) == 6

    def test_pair_range(self):
        assert len(Range('22-55')) == 24
        assert len(Range('55-22')) == 24

    def test_one_suited_hand(self):
        assert len(Range('AKs')) == 4
        assert len(Range('76s')) == 4

    def test_one_offsuit_card(self):
        assert len(Range('AKo')) == 12

    def test_full_range(self):
        assert len(Range('XX')) == 1326


class TestComposeHands:
    """Test different constructors and composition of hands."""

    def test_pairs_from_hands(self):
        assert Range.from_hands({Hand('AA'), Hand('KK'), Hand('QQ')}) == Range('QQ+')

    def test_from_combos(self):
        range = Range.from_combos(DEUCE_COMBOS)
        assert range == Range('22')
        assert range.combos == DEUCE_COMBOS
        assert range.hands == (Hand('22'),)

    @mark.xfail
    def test_from_percent(self):
        assert Range.from_percent(0.9) == Range('KK+')

    @mark.xfail
    def test_from_percent_comparison(self):
        # both represents 0.9%, but they should not be equal
        assert Range('AKo') != Range.from_percent(0.9)


class TestRangeEquality:
    """Tests if two range objects are equal."""

    def test_pairs_with_dash_equals_pairs_with_dash_reverse(self):
        assert Range('33-22').hands == Range('22-33').hands

    def test_offsuit_multiple_with_AK(self):
        assert Range('AKo 22+ 45 33') == Range('22+ AKo 54')

    def test_empty_range(self):
        assert Range() == Range('')


class TestValueChecks:
    def test_invalid_pair(self):
        with raises(ValueError):
            Range('HH')

    def test_invalid_offsuit(self):
        with raises(ValueError):
            Range('KKo')

    def test_multiple_ranges_one_invalid(self):
        with raises(ValueError):
            Range('22+ AKo JK2')

    def test_invalid_combos(self):
        with raises(ValueError):
            Range('AsKq')


class TestComparisons:
    def test_ranges_with_lesser_hands_are_smaller(self):
        assert Range('33+') < Range('22+')
        assert Range('22+') > Range('33+')

        assert Range('AKo, JKs') > Range('AKo')

    def test_ranges_only_equal_if_they_are_the_same(self):
        assert Range('Ak') == Range('Aks, AKo')
        assert Range('33+') == Range('44+, 33')

    def test_ranges_with_different_hands_are_not_equal(self):
        assert Range('AKs') != Range('KJs')
        assert Range('AKo') != Range('KJo')
        assert Range('22') != Range('44')


class TestNormalization:
    def test_empty_range_is_empty(self):
        assert str(Range('')) == ''
        assert repr(Range('')) == "Range('')"

        assert str(Range()) == ''
        assert repr(Range()) == "Range('')"

    def test_one_pair(self):
        assert str(Range('22')) == '22'

    def test_two_pairs(self):
        assert str(Range('22 44')) == '44, 22'

    def test_one_offsuit_hand(self):
        assert str(Range('AKo')) == 'AKo'

    def test_one_combination(self):
        assert str(Range('AsKc')) == 'A♠K♣'

    def test_offsuit_and_suited(self):
        assert str(Range('AK')) == 'AKs, AKo'

    def test_suited_hand(self):
        assert str(Range('AKs')) == 'AKs'

    def test_one_pair_and_one_hand(self):
        assert str(Range('22 AKo')) == '22, AKo'
        assert str(Range('22 AKs')) == '22, AKs'

    def test_one_pair_and_suited_and_offsuit(self):
        assert str(Range('22 AKo AKs')) == '22, AKs, AKo'
        assert str(Range('22 AK')) == '22, AKs, AKo'

    def test_one_pair_and_one_combo(self):
        assert str(Range('22 AsKh')) == '22, A♠K♥'

    def test_pair_range(self):
        assert str(Range('33-66')) == '66-33'

    def test_mixed_pairs_ranges_and_combos(self):
        assert str(Range('44+, KJs KJo JsQc AcKc')) == '44+, A♣K♣, KJs, KJo, Q♣J♠'

    def test_very_complicated_range(self):
        assert str(Range('44-88, AA-KK, KJs KcJh JsQc AcKc 74s-76s')) == \
            'KK+, 88-44, A♣K♣, KJs, 74s+, K♣J♥, Q♣J♠'

    def test_negative(self):
        assert str(Range('55-22')) == '55-'

    def test_full_range(self):
        assert str(Range('XX')) == 'XX'

    def test_X_in_range(self):
        assert str(Range('KX')) == 'K2s+, K2o+'

    def test_rep_pieces(self):
        assert Range('KX').rep_pieces == ['K2s+', 'K2o+']