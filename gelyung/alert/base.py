#!/usr/bin/env python
# encoding: utf-8

import hashlib
import time

import yaml
from tornado import gen

from settings import ALERT_CONF
from .mail import sendmail as email_sender
from .sms import sender as sms_sender
from .tel import sender as tel_sender

alertconf = yaml.safe_load(open(ALERT_CONF, 'r'))


class Alert(object):
    """
    告警基础类，定义了一次告警必须的基本信息,
    每一个Alert对象都代表着一次告警。
    """
    time_record = {}

    def __init__(self, receive_group, alert_level, content, when=None):
        '''
        一次告警的基本组成。

        :param str receive_group: 给谁发
            用户分组名称
        :param str alert_level: 告警等级，决定通过什么方式发送告警
            不同的等级对应的告警方式在配置中自定义
        :param dict content: 传达什么内容
            {'subject': 'title', 'body': 'detail'}
        :param datetime when: 什么时候发
            默认为None是即时发送，若是时间对象则按时发送。
            第一期不实现定时发送。
        '''
        self.receive_group = receive_group
        self.alert_level = alert_level
        self.content = content
        self.when = when
        self.alertid = hashlib.md5(content.get('subject')).hexdigest()[:16]
        self.timestamp = int(time.time())

    @property
    def sendway(self):
        """
        根据告警等级获取该告警应有的发送方式
        """
        return alertconf['levels'][self.alert_level]

    def _is_should_record_timestamp(self):
        """判断该条告警是否需要记录时间戳, 如果需要则记录。便于做告警间隔限制。

        如果当前告警不在记录中，则记录；若不在记录中， 则计算新旧两条消息的间隔
        时间，当间隔时间小于配置中写的时间间隔，则不记录，否则需要记录。

        如果判断出需要做记录，意味着这条告警消息也需要发出去。
        """
        INTERVAL = alertconf['INTERVAL']
        if self.alertid in Alert.time_record:
            cur_interval = self.timestamp - Alert.time_record[self.alertid]
            if cur_interval <= INTERVAL:
                return False
        Alert.time_record[self.alertid] = self.timestamp
        return True

    def _parsed_content(self):
        subject, body = self.content
        return {'subject': subject,
                'body': body}

    def _get_receivers(self):
        '''
        get receivers contacts from group name
        '''
        members = alertconf['contact_groups'][self.receive_group]
        contacts = alertconf['contact_members']
        result = {}
        for way in self.sendway:
            result[way] = [contacts[name][way]
                           for name in contacts if name in members]
        return result

    @gen.coroutine
    def send(self):
        '''
        发送告警
        '''
        # 不需要记录时间戳意味着不需要发送告警
        if not self._is_should_record_timestamp():
            return

        members = alertconf['contact_groups'][self.receive_group]
        receivers = self._get_receivers()
        content = self.content
        print("===========SEND INTERFACE START================")
        print("Execute here means the alert will be send!")
        print("Receivers are: {0}".format(members))
        print("Alert content is: {0}".format(content))
        print("Will send through: {0}".format(self.sendway))
        print("===========SEND INTERFACE END================")

        # TODO:并发yield list
        for way in self.sendway:
            if way == 'tel':
                yield tel_sender(receivers['tel'], content['subject'])
            elif way == 'sms':
                yield sms_sender(receivers['sms'],
                                     content['subject']+'\n'+content['body'])
            else:
                yield email_sender(receivers['email'],
                                       content['subject'], content['body'])
