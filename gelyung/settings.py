#!/usr/bin/env python
# encoding: utf-8

import os
import sys
import logging
import logging.config

import tornado
from tornado.options import define, options

#  a util func use for connect path. eg:
#  >>> path('/a', 'b', 'c')
#  >>> '/a/b/c'
path = lambda root, *a: os.path.join(root, *a)

# some basic path settings
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
STATIC_PATH = path(PROJECT_ROOT, 'static')
TEMPLATE_PATH = path(PROJECT_ROOT, "templates")
LOG_DIR = "/var/log/gelyung"

# add project path to system that could importable. eg:
# >>> from gelyung.handlers import base
sys.path.insert(0, BASE_DIR)

# tornado varable define
define("port", default=8000, help="run on the given port", type=int)
define("config", default=None, help="tornado config file")
define("debug", default=False, help="debug mode")

# parse commadline
tornado.options.parse_command_line()
# parse config file
if options.config:
    tornado.options.parse_config_file(options.config)

# Development type setting


class DeploymentType:
    PRODUCTION = "PRODUCTION"
    STAGING = "STAGING"
    TEST = "TEST"
    DEV = "DEV"


if 'DEPLOYMENT_TYPE' in os.environ:
    DEPLOYMENT = os.environ['DEPLOYMENT_TYPE'].upper()
else:
    DEPLOYMENT = DeploymentType.DEV

# settings for tornado Web class `Application` init
settings = {
    "debug": DEPLOYMENT != DeploymentType.PRODUCTION or options.debug,
    "static_path": STATIC_PATH,
    "template_path": TEMPLATE_PATH,
    "cookie_secret": "!!CHANGEME!!",
    "xsrf_cookies": False
}

# ES searching config
ES_QUERY_API = 'http://10.140.67.170:9200/_search'

# Alert config
ALERT_CONF = path(PROJECT_ROOT, 'alertconf.yml')
ALERT_VOICE_API = 'YOUR API URL'
ALERT_VOICE_TOKEN = 'YOUR TOKEN'

ALERT_SMS_API = 'YOUR API URL'
ALERT_SMS_TOKEN = 'YOUR TOKEN'

ALERT_EMAIL_SMTP_HOST = 'HOST'
ALERT_EMAIL_SMTP_PORT = 587
ALERT_EMAIL_SMTP_USER = 'username'
ALERT_EMAIL_SMTP_PASSWD = 'password!'
ALERT_EMAIL_FROM = 'from@example.com'

# 同时检查几个实例
ALERT_CONCURRENCY_NUM = 50

# 每隔多少秒进行一轮告警检查
ALERT_CHECK_CYCLE = 60

# Matrix API
MATRIX_API_GET_INSTANCES = ''

# logging config
# the dict of below, `root` field is for root logger, `loggers` field are
# child logger. usually, child logger is for diffrence module or scenario.
DEV_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'basic': {
            'format': ('%(asctime)-6s: %(name)s - %(levelname)s - %(message)s;'
                       '%(thread)d - %(filename)s - %(funcName)s'),
            'datefmt': "%Y-%m-%d %H:%M:%S",
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'basic',
        },
        'main_file': {
            'level': 'INFO',
            'class': 'logging.handlers.WatchedFileHandler',
            'formatter': 'basic',
            'filename': path(LOG_DIR, 'main.log'),
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.WatchedFileHandler',
            'formatter': 'basic',
            'filename': path(LOG_DIR, 'error.log'),
        },
        'requests_main_file': {
            'level': 'INFO',
            'class': 'logging.handlers.WatchedFileHandler',
            'formatter': 'basic',
            'filename': path(LOG_DIR, 'requests_main.log'),
        },
        'requests_error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.WatchedFileHandler',
            'formatter': 'basic',
            'filename': path(LOG_DIR, 'requests_error.log'),
        }
    },
    'loggers': {
        'gelyung.foo': {
            'handlers': ['console', 'main_file', 'error_file'],
            'level': 'DEBUG',
            'propogate': False
        },
    },
    'root': {
        'handlers': ['console', 'main_file', 'error_file'],
        'level': 'DEBUG',
    }
}

PROD_LOGGING = DEV_LOGGING.copy()
PROD_LOGGING.update({
    'loggers': {
        'gelyung.foo': {
            'handlers': ['main_file', 'error_file'],
            'level': 'DEBUG',
            'propogate': False
        },
    },
    'root': {
        'handlers': ['main_file', 'error_file'],
        'level': 'DEBUG',
    }
})

LOGGING_CONF = DEV_LOGGING if settings["debug"] else PROD_LOGGING
logging.config.dictConfig(LOGGING_CONF)
