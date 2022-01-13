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


def find_words(length, history):
    with closing(sqlite3.connect("google-words.db")) as con, \
            con, \
            closing(con.cursor()) as cursor:
        cursor.execute(SEARCH_QUERY, {"length": length})
        results = cursor.fetchall()
        return [item[0] for item in results]


if __name__ == "__main__":
    app.run(host="127.0.0.1", port="8004")
