#!/usr/bin/env python
# encoding: utf-8


import json
import logging
from functools import partial
from collections import defaultdict

from tornado import gen

from .query import send_es_query
from .query import get_alert_items
from .query import get_alert_type_strategy_and_query_body

from gelyung.alert import Alert


@gen.coroutine
def judge_and_alert(instance):

    def _get_query_datas():
        # 构造出所有的告警项的ES请求参数
        alert_items = get_alert_items()
        _query_constructor = partial(
            get_alert_type_strategy_and_query_body, hostname=instance)
        return map(_query_constructor, alert_items)

    querys = _get_query_datas()
    strategys = {q['alertname']: q['strategy'] for q in querys}

    # alertname为key，发送es查询的协程为value
    workdic = {q['alertname']: send_es_query(q['query_body']) for q in querys}
    # 多个告警项并发查询ES聚合结果
    waiter = gen.WaitIterator(**workdic)
    while not waiter.done():
        try:
            es_ret = yield waiter.next()
        except Exception as e:
            logging.error(e, exc_info=True)
        else:
            alertname = waiter.current_index
            # 在这里处理es的返回值
            alert_content = yield judge_result_and_make_alert_msg(alertname,
                                                  strategys[alertname],
                                                  json.loads(es_ret))
            # 有告警内容时才需要告警
            if alert_content.get('body'):
                receive_group = strategys[alertname]['contact_group']
                alert_level = strategys[alertname]['level']
                alerting = Alert(receive_group, alert_level, alert_content)
                # 发送告警的协程
                yield alerting.send()


@gen.coroutine
def judge_result_and_make_alert_msg(alertname, strategy, es_ret):
    content = defaultdict(str)

    if 'error' in es_ret:
        content['subject'] = es_ret['error']['root_cause']['type']
        content['body'] = es_ret['error']['root_cause']['reason']
    else:
        aggs = es_ret['aggregations']
        # 该查询时段内若无匹配数据，数据需要更新
        # 发出一条数据过时的告警
        # TODO: 此处代码逻辑需要再优化
        for field, value in aggs.items():
            if value['count'] < 1:
                msg = "{0} is out-of-date.\n".format(field)
                content['body'] += msg
        if content.get('body'):
            content['subject'] = alertname + '/out-of-date'
            raise gen.Return(content)

        # 返回的ES聚合结果正常
        for field, func in strategy['fields'].items():
            # 以字段名作为变量名赋值
            locals()[field] = aggs[field][func]
        expression = strategy['expression']
        should_alert = eval(expression)
        if should_alert:
            lvalue, oper, rvalue = expression.split()
            lvalue = eval(lvalue)
            content['body'] = ("Computed value is: {0}\nCompare operator is: {1}\n"
                               "Threshold is: {2}").format(lvalue, oper, rvalue)
            content['subject'] = alertname
    raise gen.Return(content)
