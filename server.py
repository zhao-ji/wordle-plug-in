#!/usr/bin/env python
# coding: utf-8

from flask import Flask, request, jsonify
from flask_api import status
import logbook

from utils import apply_logging
from utils import find_words_by_history, find_words_by_chars, apply_query

# import sentry_sdk
# from sentry_sdk.integrations.flask import FlaskIntegration
# sentry_sdk.init(
#     dsn="https://185976c83698461c95db2c658d7f1fca@o374324.ingest.sentry.io/5197511",
#     integrations=[FlaskIntegration()]
# )


apply_logging()
app = Flask(__name__)


@app.route("/", methods=['POST'])
def search():
    content = request.get_json()
    ip = request.headers.get("X-Real-IP", "")
    logbook.info(" {} {}".format(ip, "content"))
    if not all(["length" in content, "history" in content]):
        return "Request error!", status.HTTP_400_BAD_REQUEST
    return jsonify(apply_query(find_words_by_history(
        content["length"], content["history"]), {}))


@app.route("/", methods=['GET'])
def easy_search():
    query = request.args.get("q", "")
    length = int(request.args.get("l", 0))
    ip = request.headers.get("X-Real-IP", "")
    logbook.info(" {}, length: {}, query: {} ".format(ip, length, query))
    if not query or not length:
        return jsonify(['their', 'could', 'among'])
    return jsonify(apply_query(find_words_by_chars(length, query), {}))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port="8005")
