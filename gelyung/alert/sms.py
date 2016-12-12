#!/usr/bin/env python
# encoding: utf-8

import urllib
import logging

from tornado.gen import coroutine
from tornado.httpclient import AsyncHTTPClient

from settings import ALERT_SMS_API, ALERT_SMS_TOKEN


@coroutine
def sender(mobiles, content):
    """
    TODO: 这里使用的sms接口，是根据voice猜出来的，所以实现方式
    与voice一模一样也能发送，只是接口中的某个参数不同。
    需与监控团队确认此接口能用做生产环境后，可以统一这两个接口
    的使用实现。
    """
    mobile = ','.join(map(str, mobiles))
    logging.info("sms will be send to: {0}".format(mobile))
    paras = dict(token=ALERT_SMS_TOKEN, mobile=mobile,
                 msg=content)
    phone_url = '%s?%s' % (ALERT_SMS_API, urllib.urlencode(paras))
    yield AsyncHTTPClient().fetch(phone_url, raise_error=False)


if __name__ == '__main__':
    from tornado.ioloop import IOLoop
    ALERT_SMS_API = 'http://ump.letv.cn:8080/alarm/sms'
    ALERT_SMS_TOKEN = '0115e72e386b969613560ce15124d75a'
    ioloop = IOLoop.current()
    ioloop.run_sync(lambda: sender(["18349178100"], "短信测试"))
