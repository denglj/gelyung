#!/usr/bin/env python
# encoding: utf-8


from datetime import timedelta
import logging

from tornado import gen, queues
from tornado.ioloop import PeriodicCallback

from settings import ALERT_CONCURRENCY_NUM, ALERT_CHECK_CYCLE
from gelyung.common.matrix import get_instances
from gelyung.judge import judge_and_alert


class MonitTask(object):

    def __init__(self):
        check_instances = PeriodicCallback(self.check_instances,
                                           ALERT_CHECK_CYCLE * 1000)
        check_instances.start()

    @gen.coroutine
    def check_instances(self):
        """
        把待监控的instance取出来放入队列，
        然后消费队列里的instance，即对每个instance进行告警检查
        """
        q = queues.Queue()
        monitoring, monitored = set(), set()
        instances = yield get_instances()
        map(q.put, instances)

        @gen.coroutine
        def _judge_and_alert():
            current_instance = yield q.get()
            try:
                if current_instance in monitoring:
                    return
                monitoring.add(current_instance)
                yield judge_and_alert(current_instance)
                monitored.add(current_instance)
                logging.info("{0} was checked!".format(current_instance))
            finally:
                q.task_done()

        @gen.coroutine
        def _worker():
            while True:
                yield _judge_and_alert()

        for _ in range(ALERT_CONCURRENCY_NUM):
            _worker()
        # 对所有实例的检查必须在一轮检查周期内完成
        yield q.join(timeout=timedelta(seconds=ALERT_CHECK_CYCLE))
        assert monitoring == monitored
        logging.info("Current monitoring cycle is done!")
