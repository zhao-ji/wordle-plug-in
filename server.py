#!/usr/bin/env python
# coding: utf-8

from contextlib import closing

from flask import Flask, request, jsonify
from flask_api import status
import logbook
import sqlite3

# import sentry_sdk
# from sentry_sdk.integrations.flask import FlaskIntegration
# sentry_sdk.init(
#     dsn="https://185976c83698461c95db2c658d7f1fca@o374324.ingest.sentry.io/5197511",
#     integrations=[FlaskIntegration()]
# )
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


apply_logging()
app = Flask(__name__)


@app.route("/", methods=['POST'])
def search():
    content = request.get_json()
    # ip = request.headers.get("X-Real-IP", "")
    # logbook.info(" {} {}".format(ip, text.encode("utf-8")))
    if not all(["length" in content, "history" in content]):
        return "Request error!", status.HTTP_400_BAD_REQUEST
    return jsonify(find_words(content["length"], content["history"]))


@app.route("/", methods=['GET'])
def easy_search():
    query = request.args.get("q", "")
    length = int(request.args.get("l", 0))
    ip = request.headers.get("X-Real-IP", "")
    logbook.info(" {}, length: {}, query: {} ".format(
        ip, length, query.encode("utf-8")))
    if not query or not length:
        return jsonify(['their', 'could', 'among'])
    return jsonify(easy_find_words(length, query))


def find_words(length, history):
    with closing(sqlite3.connect("google-words.db")) as con, \
            con, \
            closing(con.cursor()) as cursor:
        cursor.execute(SEARCH_QUERY, {"length": length})
        results = cursor.fetchall()
        return [item[0] for item in results]


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


def easy_find_words(length, query):
    """
    select word from words where
        count  = :length
        and instr(word, 'p') = 3
        and instr(word, 'e')  in (1,3,5)
        and word not glob '*[xyz]*'
        limit 30;

    query := a3d-2*bcr
        correct := instr(word, 'a') = 3
        present := and instr(word, 'd') in (1,4,5)
            and instr(word, 'd') not in (2, 3)
        absent := and word not glob '*[bcr]*'
    """
    negation_sign = None
    if "+" in query:
        negation_sign = "+"
    elif "*" in query:
        negation_sign = "*"
    elif "/" in query:
        negation_sign = "/"
    elif "|" in query:
        negation_sign = "|"
    elif "_" in query:
        negation_sign = "_"

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

    certain_positions = set()
    query_str = "select word from words where"
    if length:
        query_str += " count = {}".format(length)
    if negation_str:
        query_str += " and word not glob '*[{}]*'".format(negation_str)
    for k, v in correct.items():
        query_str += " and instr(word, '{}') = {}".format(v, k)
        certain_positions.add(k)
    for k, v in present.items():
        possible_positions = list(set(
            range(1, length + 1)
        ) - certain_positions - set(v))
        impossible_positions = list(certain_positions | set(v))
        if len(possible_positions) == 1:
            query_str += " and instr(word, '{}') = {}".format(
                k, possible_positions[0])
        elif len(possible_positions) > 1:
            query_str += " and instr(word, '{}') in {}".format(
                k, str(tuple(possible_positions)))
        if len(impossible_positions) == 0:
            pass
        elif len(impossible_positions) == 1:
            query_str += " and instr(word, '{}') != {}".format(
                k, impossible_positions[0])
        if len(impossible_positions) > 1:
            query_str += " and instr(word, '{}') not in {}".format(
                k, str(tuple(impossible_positions)))
    query_str += " limit 30;"

    with closing(sqlite3.connect("google-words.db")) as con, \
            con, \
            closing(con.cursor()) as cursor:
        logbook.info(query_str)
        cursor.execute(query_str)
        results = cursor.fetchall()
        logbook.info(", ".join([item[0] for item in results]))
        return [item[0] for item in results]


if __name__ == "__main__":
    app.run(host="127.0.0.1", port="8005")
