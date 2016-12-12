#!/usr/bin/env python
# encoding: utf-8

import tornado.ioloop
import tornado.web
import tornado.autoreload
from tornado.options import options
import logging

from settings import settings
from gelyung.urls import url_patterns
from gelyung.sched import MonitTask


class MainApplication(tornado.web.Application):

    def __init__(self):
        logging.info("init MainApplication with settings: %s" % str(settings))
        tornado.web.Application.__init__(self, url_patterns, **settings)


def main():
    app = MainApplication()
    app.listen(options.port)
    MonitTask()
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
