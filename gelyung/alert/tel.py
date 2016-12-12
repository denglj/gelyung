#!/usr/bin/env python
# encoding: utf-8

import urllib
import logging

from tornado.gen import coroutine
from tornado.httpclient import AsyncHTTPClient

from settings import ALERT_VOICE_API, ALERT_VOICE_TOKEN


@coroutine
def sender(mobiles, content):
    mobile = ','.join(map(str, mobiles))
    logging.info("tel will be call: {0}".format(mobile))
    paras = dict(token=ALERT_VOICE_TOKEN, mobile=mobile,
                 msg=content)
    phone_url = '%s?%s' % (ALERT_VOICE_API, urllib.urlencode(paras))
    yield AsyncHTTPClient().fetch(phone_url, raise_error=False)


if __name__ == '__main__':
    from tornado.ioloop import IOLoop
    ALERT_VOICE_API = 'http://ump.letv.cn:8080/alarm/voice'
    ALERT_VOICE_TOKEN = 'ad21fd9b78c48d7ff367090eaad3e264'
    IOLoop.current().run_sync(lambda: sender(['18349178100'], "电话测试呀!"))
