# -*- coding: utf-8 -*-

import json
import logging
import os
from sockjs.tornado import SockJSRouter, SockJSConnection
from tornado.web import RequestHandler, StaticFileHandler
from tornado.web import Application
from tornado.ioloop import IOLoop

from sidecar.utils import log


class WebHandler(RequestHandler):
    def initialize(self, page, **kwargs):
        self.page = page
        self.kwargs = kwargs

    def get(self):
        self.render(self.page, **self.kwargs)


class TextHandler(RequestHandler):
    def initialize(self, content):
        self.content = content

    def get(self):
        self.finish(self.content)


class FileHandler(StaticFileHandler):
    def initialize(self, path):
        if path is None:
            self.absolute_path = None
        else:
            path = os.path.join(os.path.dirname(__file__), path)
            self.absolute_path = os.path.abspath(os.path.expanduser(path))
            self.root, self.filename = os.path.split(self.absolute_path)

    def get(self, path=None, include_body=True):
        if self.absolute_path is not None:
            return super(FileHandler, self).get(self.filename, include_body)
        self.finish('')


class Connection(SockJSConnection):
    def send_json(self, kind, data=None):
        log.debug()
        self.send(json.dumps({'kind': kind, 'data': data or {}}))

    def on_open(self, info):
        log.debug()
        self.send_json('ready')

    def on_message(self, msg):
        msg = json.loads(msg)
        log.debug(msg)

    def on_close(self):
        log.debug()

    @classmethod
    def tornado_app(cls, ui, title, debug=False):
        root = os.path.dirname(__file__)
        router = SockJSRouter(cls, '/api')

        settings = {
            'static_path': os.path.join(root, 'static'),
            'template_path': os.path.join(root, 'static'),
            'debug': debug
        }

        handlers = [
            ('/', WebHandler, {'page': 'index.html', 'title': title}),
            ('/ui.json', TextHandler, {'content': ui})
        ]
        handlers.extend(router.urls)

        return Application(handlers, **settings)

    @classmethod
    def start(cls, ui, title, debug=False, port=9999):
        if debug:
            logging.basicConfig(level=logging.DEBUG)
        log.debug()

        app = cls.tornado_app(ui, title, debug=debug)
        app.listen(port)

        IOLoop.instance().start()
