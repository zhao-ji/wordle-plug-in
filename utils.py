from contextlib import closing

import logbook
import sqlite3


SEARCH_QUERY = "select word from words where count = :length limit 5"


def apply_logging():
    from os.path import abspath, exists, dirname, join

    server_log_file = join(dirname(abspath(__file__)), "search.log")
    if not exists(server_log_file):
        open(server_log_file, "w").close()

    logbook.set_datetime_format("local")
    local_log = logbook.FileHandler(server_log_file)
    local_log.format_string = (
        u'[{record.time:%Y-%m-%d %H:%M:%S}] '
        u'lineno:{record.lineno} '
        u'{record.level_name}:{record.message}')
    local_log.push_application()


def apply_query(query_str, xargs):
    with closing(sqlite3.connect("google-words.db")) as con, \
            con, \
            closing(con.cursor()) as cursor:
        cursor.execute(query_str, xargs)
        results = cursor.fetchall()
        return [item[0] for item in results]


def forge_query(length, correct, present, negation_str):
    """
    PARAMETERS:
        length := 5
        correct := {
            # position: char,
            1: 'h',
        }
        present := {
            # char: [position, position],
            'l': [-2, -4],
        }
        negation_str := 'e'
    RETURN:
        select word from words where
            count = 5
            and word not glob '*[e]*'
            and substr(word, 1, 1) = 'h'
            and instr(word, 'l') in (3, 5)
            and substr(word, 4, 1) != 'l' and substr(word, 2, 1) != 'l'
            limit 30;
    """

    certain_positions = set()
    query_str = "select word from words where"
    if length:
        query_str += " count = {}".format(length)
    if negation_str:
        query_str += " and word not glob '*[{}]*'".format(negation_str)
    for k, v in correct.items():
        query_str += " and substr(word, {}, 1) = '{}'".format(k, v)
        certain_positions.add(k)
    for k, v in present.items():
        possible_positions = list(set(range(1, length + 1)) - set(v))
        if len(possible_positions) == 1:
            query_str += " and instr(word, '{}') = {}".format(
                k, possible_positions[0])
        elif len(possible_positions) > 1:
            query_str += " and instr(word, '{}') in {}".format(
                k, str(tuple(possible_positions)))
        for item in v:
            query_str += " and substr(word, {}, 1) != '{}'".format(item, k)
    query_str += " limit 30;"
    return query_str


def apply_cache(cache, correct, present):
    if "-" in cache:
        choice = cache.pop(0)
        positions = list(
            map(int, filter(lambda i: i, "".join(cache).split("-"))))
        present.setdefault(choice, []).extend(positions)
    elif len(cache) == 2:
        correct[int(cache[1])] = cache[0]
    elif len(cache) == 1:
        present[cache[0]] = []


def find_words_by_chars(length, query):
    """
    query := a3d-2-4*bcr
        correct := instr(word, 'a') = 3
        present := and instr(word, 'l') in (3, 5)
            and substr(word, 4, 1) != 'l' and substr(word, 2, 1) != 'l'
        absent := and word not glob '*[bcr]*'
    """
    negation_sign = None
    options = ["+", "*", "/", "|", "_"]
    separator = [c for c in query if not c.isalnum() and c != "-"]
    assert len(separator) <= 1
    if separator:
        assert separator[0] in options
        negation_sign = separator[0]

    negation_str = None
    choice_str = query
    if negation_sign:
        choice_str, not_to_be = query.split(negation_sign)
        negation_str = "".join(set(not_to_be))

    correct = {}
    present = {}
    cache = []
    for item in list(choice_str.lower()):
        if item.isalpha():
            apply_cache(cache, correct, present)
            cache = [item]
        else:
            cache.append(item)
    apply_cache(cache, correct, present)

    return forge_query(length, correct, present, negation_str)


def find_words_by_history(length, history):
    """
    history := [
        [
            {
                char: 'a',
                status: 'absent'
            },
            {
                char: 'b',
                status: 'present'
            },
        ],
        [
            {
                char: 't',
                status: 'correct'
            },
            {
                char: 'b',
                status: 'present'
            },
        ],
    ]
    """
    correct = {}
    present = {}
    absent = set()
    for row in history:
        for index, item in enumerate(row):
            if item.get("status", "") == "correct":
                correct[index + 1] = item["char"]
            elif item.get("status", "") == "present":
                present.setdefault(item["char"], []).append(-(index+1))
            elif item.get("status", "") == "absent":
                absent.add(item["char"])
    return forge_query(length, correct, present, "".join(absent))
