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


def test_correct(setup_database):
    cursor = setup_database
    cursor.execute(find_words_by_chars(5, 'a1p2p3l4e5'))
    results = [item[0] for item in cursor.fetchall()]
    assert results == ["apple"]
