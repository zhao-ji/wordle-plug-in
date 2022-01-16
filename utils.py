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


def apply_query(query_str, xargs=None):
    with closing(sqlite3.connect("google-words.db")) as con, \
            con, \
            closing(con.cursor()) as cursor:
        cursor.execute(query_str, xargs or {})
        results = cursor.fetchall()
        return [item[0] for item in results]


def forge_query(correct, present, negation_str, length=5, top=100000, limit=20):
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
            count = 5 and id <= 100000
            and word not glob '*[e]*'
            and substr(word, 1, 1) = 'h'
            and instr(word, 'l') in (3, 5)
            and substr(word, 4, 1) != 'l' and substr(word, 2, 1) != 'l'
            order by id limit 20;
    """

    certain_positions = set()
    query_str = "select word from words where count = {} and id <= {}".format(
        length, top)
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
    query_str += " order by id limit {};".format(limit)
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


def find_words_by_chars(query):
    """
    query := a3d-2-4*bcr
        correct := instr(word, 'a') = 3
        present := and instr(word, 'l') in (3, 5)
        absent := and word not glob '*[bcr]*'
    """
    negation_sign = None
    options = ["+", "*", "/", "|", "_"]
    separator = [c for c in query if not c.isalnum() and c != "-"]
    assert len(separator) <= 1, "More than 1 separator!"
    if separator:
        assert separator[0] in options, "Separator can only be in [+*/|_]!"
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

    return correct, present, negation_str


def find_words_by_history(history):
    """
    a+p-p-l~e~,h-e+l~l~o-
    """
    correct = {}
    present = {}
    absent = set()
    for row in history.split(","):
        lists = list(row)
        char_list = lists[::2]
        sign_list = lists[1::2]
        for index, [char, status] in enumerate(zip(char_list, sign_list)):
            if status == "+":
                correct[index + 1] = char
            elif status == "~":
                present.setdefault(char, []).append(index+1)
            elif status == "-":
                absent.add(char)
    return correct, present, "".join(absent)


def find_words_by_history_in_json(history):
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
                present.setdefault(item["char"], []).append(index+1)
            elif item.get("status", "") == "absent":
                absent.add(item["char"])
    return correct, present, "".join(absent)


class BaseSearch:

    def __init__(self, length=5, top=100000, limit=20):
        self.length = length
        self.limit = limit
        self.top = top

    def process_input(self, input):
        self.correct = {}
        self.present = {}
        self.negation_str = ""

    def check(self):
        if len(self.correct) > self.length:
            return False
        return True

    def get_suggestions(self):
        if not self.check():
            return []

        query = forge_query(
            self.correct, self.present, self.negation_str,
            self.length, self.top, self.limit)

        suggestions = apply_query(query)

        return suggestions


class SearchByChars(BaseSearch):

    def process_input(self, query):
        self.correct, self.present, self.negation_str = \
            find_words_by_chars(query)


class SearchByHistory(BaseSearch):

    def process_input(self, query):
        self.correct, self.present, self.negation_str = \
            find_words_by_history(query)


class SearchByHistoryInJSON(BaseSearch):

    def process_input(self, query):
        self.correct, self.present, self.negation_str = \
            find_words_by_history_in_json(query)
