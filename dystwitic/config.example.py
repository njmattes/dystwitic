#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from datetime import timedelta


class TwitterConfig(object):
    CONSUMER_KEY = '<YOUR_CONSUMER_KEY>'
    CONSUMER_SECRET = '<YOUR_CONSUMER__SECRET>'
    OAUTH_TOKEN = '<YOUR_OAUTH_KEY>'
    OAUTH_SECRET = '<YOUR_OAUTH_SECRET>'


class MongoConfig(object):
    HOST = 'localhost'
    PORT = 27017
    DATABASE = 'dystwitic'
    COLOR_COLLECTION = 'stream_colors'
    TAG_COLLECTION = 'stream_tags'


class FlaskConfig(object):
    DEBUG = True
    ASSETS_DEBUG = True
    ADMINS = frozenset(['<REPLACE_ME>'])
    SECRET_KEY = '<REPLACE_ME>'
    THREADS_PER_PAGE = 8
    CSRF_ENABLED = True
    CSRF_SESSION_KEY = '<REPLACE_ME>'
    CACHE_TYPE = 'redis'
    CACHE_REDIS_DB = 1


class FlaskProductionConfig(FlaskConfig):
    DEBUG = False
    ASSETS_DEBUG = False


class CeleryConfig(object):
    BROKER_URL = 'amqp://localhost:5672/'
    CELERYBEAT_SCHEDULE = {
        'make_map-every-1-second': {
            'task': 'cache_map',
            'schedule': timedelta(seconds=1),
            'args': (), },
        'remove-old-tweets-every-1-day': {
            'task': 'remove_old_tweets',
            'schedule': timedelta(days=1),
            'args': (), }, }
    CELERY_TIMEZONE = 'UTC'
    CELERY_TASK_RESULT_EXPIRES = 3600
    CELERY_IGNORE_RESULT = True
