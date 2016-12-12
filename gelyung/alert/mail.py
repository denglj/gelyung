#!/usr/bin/env python
# encoding: utf-8

import logging
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from functools import partial

from tornado import gen

from settings import ALERT_EMAIL_SMTP_HOST
from settings import ALERT_EMAIL_SMTP_PORT
from settings import ALERT_EMAIL_SMTP_USER
from settings import ALERT_EMAIL_SMTP_PASSWD
from settings import ALERT_EMAIL_FROM

#  ALERT_EMAIL_SMTP_HOST = '10.205.91.22'
#  ALERT_EMAIL_SMTP_PORT = 587
#  ALERT_EMAIL_SMTP_USER = 'mcluster'
#  ALERT_EMAIL_SMTP_PASSWD = 'Mcl_20140903!'
#  ALERT_EMAIL_FROM = 'mcluster@letv.com'


class _SMTPSession(object):

    def __init__(self,
                 host=ALERT_EMAIL_SMTP_HOST,
                 port=ALERT_EMAIL_SMTP_PORT,
                 username=ALERT_EMAIL_SMTP_USER,
                 passwd=ALERT_EMAIL_SMTP_PASSWD):
        self.host = host
        self.port = port
        self.username = username
        self.passwd = passwd
        try:
            self.conn = smtplib.SMTP(self.host, self.port)
            self.conn.login(self.username, self.passwd)
        except Exception as e:
            self.conn = None
            logging.error(e, exc_info=True)

    @gen.coroutine
    def send(self, *args, **kwargs):
        try:
            yield self.conn.sendmail(*args, **kwargs)
        except Exception as e:
            logging.error(e, exc_info=True)

    def close(self):
        self.conn.quit()


SMTPSession = _SMTPSession()


@gen.coroutine
#  def sendmail(session, fromaddr, toaddr, subject, body):
def sendmail(toaddr, subject, body):
    """ 发送邮件的协程

    :param SMTPSession session: 连接到邮件服务器的会话
    :param str fromaddr: 发件人
    :param list toaddr: 收件人列表
    :param str subject: 邮件标题
    :param str body: 邮件正文

    :rtype: dict: 每个收件人接收邮件的状态
    """
    session = SMTPSession
    fromaddr = ALERT_EMAIL_FROM
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = ', '.join(toaddr)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    text = msg.as_string()
    yield session.send(fromaddr, toaddr, text)


# 默认绑定了邮件服务器会话和发件人
#  send_alert_mail = partial(sendmail, session=SMTPSession,
                          #  fromaddr=ALERT_EMAIL_FROM)
