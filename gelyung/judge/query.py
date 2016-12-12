#!/usr/bin/env python
# encoding: utf-8

import json
import urllib

import yaml
from tornado import gen, httpclient

from settings import ALERT_CONF
from settings import ES_QUERY_API


@gen.coroutine
def send_es_query(query_data, query_type='count'):
    """
    异步发送ES查询请求
    """
    try:
        urlargs = urllib.urlencode({'search_type': query_type})
        query_url = '?'.join([ES_QUERY_API, urlargs])
        request = httpclient.HTTPRequest(query_url, 'POST', body=json.dumps(query_data))
        response = yield httpclient.AsyncHTTPClient().fetch(request)
    except Exception as e:
        print(e)
        raise gen.Return('')
    raise gen.Return(response.body)


def get_alert_items():
    conf = yaml.safe_load(open(ALERT_CONF, 'r'))
    return conf['alert_items']


def get_alert_type_strategy_and_query_body(alert, hostname):
    """
    根据alert配置和hostname构造完整的ES查询请求数据

    :param dict alert: 某一项告警配置
        e.g. {
                 'host/cpu/utilization':
                 {
                     'fields': {'idle': 'avg'},
                     'expression': '(1-idle) >= 0.8',
                     'metrictype': 'host/cpu',
                     'cycle': '5m'
                 }
             }
    :param str hostname: 主机名，也是监控系统模型中所称的实例
    """

    # 监控项的类型与对应的监控策略
    alerttype, strategy = alert.items()[0]
    # 告警消息的名称，`监控项/实例` ，简短而清晰地表明哪个实例
    # 的哪个告警项产生了告警
    alertname = '{0}/{1}'.format(alerttype, hostname)
    aggs = {}
    for field in strategy['fields']:
        aggs[field] = {
            "stats": {
                "field": "metrics.{0}".format(field)
            }
        }
    query_body = {
        "query": {
            "filtered": {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "range": {
                                    "timestamp": {
                                        "gte": "now-{0}".format(strategy['cycle']),
                                        "lte": "now"
                                    }
                                }
                            },
                            {
                                "match_phrase": {
                                    "metrictype": strategy['metrictype']
                                }
                            },
                            {
                                "match_phrase": {
                                    "lables.hostname": hostname
                                }
                            }
                        ]
                    }
                }
            }
        },
        "aggs": aggs
    }
    ret = {'alerttype': alerttype, 'alertname': alertname,
           'strategy': strategy, 'query_body': query_body}
    return ret
