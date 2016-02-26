# -*- coding: utf-8

import json
import random
import string
import tornado.gen
import tornado.testing
import tornado.web
import tornado.websocket

from sidecar.connection import Connection


class AsyncSockJSClient(object):
    def __init__(self, ws):
        self.ws = ws

    def send(self, data):
        self.ws.write_message(json.dumps(data))

    @tornado.gen.coroutine
    def read(self):
        response = yield self.ws.read_message()
        assert response[0] == 'a'  # SockJS message tag
        # payload is a JSON-encoded array of JSON-encoded objects
        messages = [json.loads(payload) for payload in json.loads(response[1:])]
        raise tornado.gen.Return(messages)


class TestConnection(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return Connection.tornado_app({}, 'foo')

    @tornado.gen.coroutine
    def connect(self):
        r1 = str(random.randint(0, 1000))
        conn_id = ''.join(random.choice(string.ascii_letters) for _ in range(8))
        port = self.get_http_port()
        url = 'ws://localhost:{}/api/{}/{}/websocket'.format(port, r1, conn_id)
        ws = yield tornado.websocket.websocket_connect(url)
        response = yield ws.read_message()
        assert response == 'o'  # SockJS opening tag
        raise tornado.gen.Return(AsyncSockJSClient(ws))

    @tornado.testing.gen_test
    def test_handshake(self):
        client = yield self.connect()
        response = yield client.read()
        assert response == [{'kind': 'ready', 'data': {}}]
