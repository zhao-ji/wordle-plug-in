#!/usr/bin/env python
# coding: utf-8

import time

from flask import g
from flask import Flask, jsonify, request
from flask_api import status
import logbook

from utils import apply_logging
from utils import SearchByChars
from utils import SearchByHistoryInJSON
from utils import SearchByHistory

# import sentry_sdk
# from sentry_sdk.integrations.flask import FlaskIntegration
# sentry_sdk.init(
#     dsn="https://185976c83698461c95db2c658d7f1fca@o374324.ingest.sentry.io/5197511",
#     integrations=[FlaskIntegration()]
# )


apply_logging()
app = Flask(__name__)


@app.before_request
def record_request_start_time():
    g.start = time.time()


@app.after_request
def record_response_time(response):
    time_cost = time.time() - g.start
    logbook.info("Response time: {}.".format(time_cost))
    if ((response.response) and
            (200 <= response.status_code < 300) and
            (response.content_type.startswith('application/json'))):
        response.headers["Response-Time"] = time_cost
    return response


@app.route("/history/", methods=['POST'])
def search_by_history_post():
    content = request.get_json()
    history = content.get("history", None)
    length = int(content.get("length", 5))
    top = int(content.get("top", 100000))
    limit = int(content.get("limit", 20))
    if not all([length, history or history == []]):
        return "Request error!", status.HTTP_400_BAD_REQUEST

    ip = request.headers.get("X-Real-IP", "")
    logbook.info(
        "from: {}, length: {}, top: {}, limit: {}, history: {}."
        .format(ip, length, top, limit, str(history)))

    if not all([length > 0, top > 0, limit > 0]):
        return jsonify([
            'their', 'could', 'among', 'which', 'there',
            'would', 'other', 'these', 'about', 'first',
            'after', 'where', 'those', 'state', 'being',
            'years', 'under', 'world', 'three', 'while',
            'great',
        ])

    search = SearchByHistoryInJSON(length, top, limit)
    search.process_input(history)
    words = search.get_suggestions()
    logbook.info("from: {}, query result: {}.".format(ip, ", ".join(words)))
    return jsonify(words)


@app.route("/history/", methods=['GET'])
def search_by_history():
    history = request.args.get("h", "")
    length = int(request.args.get("l", 5))
    top = int(request.args.get("top", 100000))
    limit = int(request.args.get("limit", 20))

    ip = request.headers.get("X-Real-IP", "")
    logbook.info(
        "from: {}, length: {}, history: {} , top: {}, limit: {}."
        .format(ip, length, history, top, limit))

    if not all([history, length > 0, top > 0, limit > 0]):
        return jsonify([
            'their', 'could', 'among', 'which', 'there',
            'would', 'other', 'these', 'about', 'first',
            'after', 'where', 'those', 'state', 'being',
            'years', 'under', 'world', 'three', 'while',
            'great',
        ])

    search = SearchByHistory(length, top, limit)
    search.process_input(history)
    words = search.get_suggestions()
    logbook.info("from:{}, query result: {}.".format(ip, ", ".join(words)))
    return jsonify(words)


@app.route("/", methods=['GET'])
def search():
    query = request.args.get("q", "")
    length = int(request.args.get("l", 5))
    top = int(request.args.get("top", 100000))
    limit = int(request.args.get("limit", 20))

    ip = request.headers.get("X-Real-IP", "")
    logbook.info(
        "from: {}, length: {}, query: {} , top: {}, limit: {}."
        .format(ip, length, query, top, limit))

    if not all([query, length > 0, top > 0, limit > 0]):
        return jsonify([
            'their', 'could', 'among', 'which', 'there',
            'would', 'other', 'these', 'about', 'first',
            'after', 'where', 'those', 'state', 'being',
            'years', 'under', 'world', 'three', 'while',
            'great',
        ])

    search = SearchByChars(length, top, limit)
    search.process_input(query)
    words = search.get_suggestions()
    logbook.info("from:{}, query result: {}.".format(ip, ", ".join(words)))
    return jsonify(words)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port="8005")
