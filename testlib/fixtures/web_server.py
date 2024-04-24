__all__ = ["webhook_server"]

from dataclasses import dataclass
from threading import Thread

import pytest
from flask import Flask, make_response, request
from werkzeug import serving


@dataclass
class ReceivedData:
    payload: dict
    args: dict


class Server:
    thread: Thread
    werkzeug: serving.BaseWSGIServer

    def __init__(self):
        self.received_data = []

    @property
    def listening_port(self):
        return self.werkzeug.socket.getsockname()[1]

    def start(self):
        self.thread.start()

    def shutdown(self):
        self.werkzeug.shutdown()
        self.thread.join()

    @staticmethod
    def create_flask_server():
        server = Server()
        app = Flask(__name__)

        @app.route("/testhook", methods=["POST"])
        def webhook():
            server.received_data.append(ReceivedData(payload=request.json, args=request.args))
            return make_response()

        server.werkzeug = serving.make_server(host="0.0.0.0", port=0, app=app)
        server.thread = Thread(target=server.werkzeug.serve_forever)
        return server


@pytest.fixture
def webhook_server():
    server = Server.create_flask_server()
    try:
        server.start()
        yield server
    finally:
        server.shutdown()
