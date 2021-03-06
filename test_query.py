import sqlite3

import pytest

from utils import find_words_by_chars
from utils import SearchByChars
# from utils import find_words_by_history


@pytest.fixture
def setup_database():
    """
    Fixture to set up the database with real data
    """
    connection = sqlite3.connect("words.db")
    cursor = connection.cursor()
    yield cursor
    connection.close()


def mock_apply_query(sql_string):
    connection = sqlite3.connect("words.db")
    cursor = connection.cursor()
    cursor.execute(sql_string)
    results = [item[0] for item in cursor.fetchall()]
    try:
        return results
    finally:
        connection.close()


def test_connection(setup_database):
    cursor = setup_database
    cursor.execute("select count(*) from words;")
    assert cursor.fetchone()[0] > 0


class TestCharsLength:
    """
    edge case:
        length is [0, 15]
        length is less than correct
        length is less than present
        length is more than 26 - absent
    usual case:
        length equals correct
        length equals present
        length equals 26 - absent
        length more than correct
        length more than present
        length less than 26 - absent
    others:
        only length, no query
    """
    @pytest.mark.parametrize("length, chars, expected", [
        (1, "a", ["a"]),
        (2, "o1f2", ["of"]),
        (3, "t1h2e3", ["the"]),
        (4, "t1h2a3t4", ["that"]),
        (5, "w1h2i3c4h5", ["which"]),
        (6, "s1h2o3u4l5d6", ["should"]),
        (7, "between", ["between"]),
        (8, "children", ["children"]),
        (9, "different", ["different"]),
        (10, "government", ["government"]),
        (11, "i1n2f3o4r5m6a7tion_sv", ["information"]),
        (12, "r1e2lationship", ["relationship"]),
        (13, "i1n2t3e4r5n6a7tional", ["international"]),
        (14, "responsibility", ["responsibility"]),
        (15, "c1h2a3r4a5c6teristics", ["characteristics"]),
    ])
    def test_length_range(self, monkeypatch, length, chars, expected):
        monkeypatch.setattr('utils.apply_query', mock_apply_query)

        search = SearchByChars(length=length)
        search.process_input(chars)
        results = search.get_suggestions()

        assert results == expected


class TestCharsSaperator:
    """
    illegal saperator raise exception
    multipul legal saperator raise exception

    single legal saperator works as charm
    single legal saperator with different length works as charm

    single legal saperator with negation string works as charm
    single legal saperator without negation string works as charm
    single legal saperator with multi negation string works as charm
    """
    @pytest.mark.parametrize("length, chars", [
        (5, "a1p2p3l4.e"),
        (5, "a1p2p3l4&e"),
        (5, "a1p2p3l4)e"),
    ])
    def test_seperator_illegel(self, setup_database, length, chars):
        with pytest.raises(
                AssertionError, match="Separator can only be in"):
            find_words_by_chars(length, chars)

    @pytest.mark.parametrize("length, chars", [
        (5, "a1p2p3l4__e"),
        (5, "a1p2p3l4_e_"),
        (5, "a1p2p3l_4_e_"),
    ])
    def test_seperator_more_than_1(self, setup_database, length, chars):
        with pytest.raises(AssertionError, match="More than 1 separator!"):
            find_words_by_chars(length, chars)

    @pytest.mark.parametrize("length, chars, expected", [
        (3, "wh_y", ["who", "how"]),
        (3, "wh+y", ["who", "how"]),
        (3, "wh*y", ["who", "how"]),
        (3, "wh/y", ["who", "how"]),
        (3, "wh|y", ["who", "how"]),
        (4, "hom_w", ["home", "homo"]),
        (4, "hom+w", ["home", "homo"]),
        (4, "hom*w", ["home", "homo"]),
        (4, "hom/w", ["home", "homo"]),
        (4, "hom|w", ["home", "homo"]),
        (5, "a1p2p3l4_e", ["apply", ]),
        (5, "a1p2p3l4+e", ["apply", ]),
        (5, "a1p2p3l4*e", ["apply", ]),
        (5, "a1p2p3l4/e", ["apply", ]),
        (5, "a1p2p3l4|e", ["apply", ]),
    ])
    def test_different_separator(
            self, setup_database, length, chars, expected):
        cursor = setup_database
        cursor.execute(find_words_by_chars(length, chars))
        results = [item[0] for item in cursor.fetchall()]
        assert results == expected


class TestCharsCorrect:
    """
    correct string works good
    multi correct chars work good
    chars without position work good
    mixing of with or without position works good
    """
    @pytest.mark.parametrize("length, chars, expected", [
        (3, "t1h2e3", ["the"]),
        (3, "a1n2d3", ["and"]),
        (3, "f1o2r3", ["for"]),
        (3, "y1o2u3", ["you"]),
        (4, "l1o2v3e4", ["love"]),
        (5, "a1p2p3l4e5", ["apple"]),
        (5, "h1e2l3l4o5", ["hello"]),
        (10, "u1n2i3v4e5r6s7i8t9y10", ["university"]),
        (10, "m1a2n3a4g5e6m7e8n9t10", ["management"]),
        (10, "t1e2c3h4n5o6l7o8g9y10", ["technology"]),
    ])
    def test_char_with_position(self, setup_database, length, chars, expected):
        cursor = setup_database
        cursor.execute(find_words_by_chars(length, chars))
        results = [item[0] for item in cursor.fetchall()]
        assert results == expected

    @pytest.mark.parametrize("length, chars, expected", [
        (5, "kpeo", ["poker", "spoke"]),
        (5, "about", ["about"]),
        (5, "other", ["other"]),
        (5, "their", ["their"]),
        (10, "university", ["university"]),
        (10, "government", ["government"]),
        (10, "technology", ["technology"]),
    ])
    def test_char_without_position(
            self, setup_database, length, chars, expected):
        cursor = setup_database
        cursor.execute(find_words_by_chars(length, chars))
        results = [item[0] for item in cursor.fetchall()]
        assert results == expected

    @pytest.mark.parametrize("length, chars, expected", [
        (3, "an2d", ["and", "dna"]),
        (5, "a1bout", ["about"]),
        (10, "t1echnology", ["technology"]),
        (10, "mana4gement", ["management", "engagement"]),
        (10, "mana4gem7ent", ["management", "engagement"]),
        (10, "mana4gem7ent10", ["management", "engagement"]),
        (10, "m1ana4gem7ent10", ["management", ]),
    ])
    def test_char_mix_with_and_without_position(
            self, setup_database, length, chars, expected):
        cursor = setup_database
        cursor.execute(find_words_by_chars(length, chars))
        results = [item[0] for item in cursor.fetchall()]
        assert results == expected


class TestCharsPresent:
    """
    edge case:
        conflict with correct
        conflict with negation str
    usual case:
        1 present
        multi present
        all present
        1 present with 1 position
        1 present with multi positions
        multi present with multi positions
        all present with multi positions
        possible position is only one
        possible position is multi
        impossible position is only one
        impossible position is multi
    """
    pass


class TestCharsNegationStr:
    @pytest.mark.parametrize("length, chars, expected", [
        (3, "bn_icoe", ["nba", "ban", "abn"]),
        (5, "a1p2p3l4_e", ["apply", ]),
    ])
    def test_negation_str(self, setup_database, length, chars, expected):
        cursor = setup_database
        cursor.execute(find_words_by_chars(length, chars))
        results = [item[0] for item in cursor.fetchall()]
        assert results == expected

    @pytest.mark.parametrize("length, chars, expected", [
        (4, "hom_ww", ["home", "homo"]),
        (4, "lk_aoushcmyn", ["like", "kill"]),
        (4, "lk_aoauosshcmyn", ["like", "kill"]),
    ])
    def test_repeat_negation_chars(
            self, setup_database, length, chars, expected):
        cursor = setup_database
        cursor.execute(find_words_by_chars(length, chars))
        results = [item[0] for item in cursor.fetchall()]
        assert results == expected


class TestHistoryLength:
    pass
