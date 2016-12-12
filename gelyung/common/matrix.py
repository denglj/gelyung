#!/usr/bin/env python
# encoding: utf-8

"""

This module used for interacting with the matrix.
"""

import yaml
import logging
from tornado import gen
#  from tornado import httpclient

from settings import ALERT_CONF
#  from settings import MATRIX_API_GET_INSTANCES


@gen.coroutine
def get_instances(matrix_api=None):
    """
    此处应该从matrix的API获取被监控的实例，
    现在定义的是一个主机名就代表一个实例
    """
    try:
        #  response = yield httpclient.AsyncHTTPClient().fetch(MATRIX_API_GET_INSTANCES)
        # handle matrix response here

        # 暂时从配置文件获取代替从matrix获取
        conf = yaml.safe_load(open(ALERT_CONF))
        instances = conf['instances']
    except Exception as e:
        logging.error(e, exc_info=True)
        raise gen.Return([])
    raise gen.Return(instances)
