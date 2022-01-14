import sqlite3

import pytest

from utils import find_words_by_history, find_words_by_chars


@pytest.fixture
def setup_database():
    """
    Fixture to set up the database with real data
    """
    connection = sqlite3.connect("google-words.db")
    cursor = connection.cursor()
    yield cursor
    connection.close()


def test_connection(setup_database):
    cursor = setup_database
    cursor.execute("select count(*) from words;")
    assert cursor.fetchone()[0] == 20000


class TestCorrect:
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
    ])
    def test_char_mix_with_and_without_position(
            self, setup_database, length, chars, expected):
        cursor = setup_database
        cursor.execute(find_words_by_chars(length, chars))
        results = [item[0] for item in cursor.fetchall()]
        assert results == expected
