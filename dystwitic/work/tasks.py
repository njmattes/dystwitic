#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from six import iteritems
import re
import colorsys
import simplejson as json
import numpy as np
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from pymongo import MongoClient
from dystwitic.config import MongoConfig
from dystwitic.constants import TAGS, OBSFUCATE_COLOR, COLORS
from dystwitic.ingest.mongo import write_tag_row, write_color_row
from dystwitic.work.celery import app
from dystwitic.work.map import make_map
from dystwitic.web.cache import cache

"""`celery` tasks.

These functions are monitored by `celery`. Repetitive tasks are scheduled and
run by `celery`'s `beat` process. `celery beat` itself is launched and
monitored by `supervisord`. Other tasks are added to a queue as needed.

Options for these tasks can be set in the `CeleryConfig` object in the
`dystwitic.config` module.
"""


@app.task(bind=True, max_retries=2, soft_time_limit=2, name='cache_map')
def cache_map(task):
    """`celery beat` task for storing updated maps in a `redis` cache.

    :param task:
    :type task:
    :return:
    :rtype:
    """
    app_map = make_map()
    if app_map:
        cache.set('map', app_map)
        return app_map


@app.task(bind=True, max_retries=3, soft_time_limit=4, name='process_tweet')
def process_tweet(task, string):
    """Task for parsing and storing tweets as they're streamed. This task
    is added to a `celery` queue as the tweets are received so as not to
    block the stream (as doing so would cause it to crash).

    :param task:
    :type task:
    :param string:
    :type string:
    :return:
    :rtype:
    """
    data = json.loads(string)
    if 'text' in data:
        coords = None
        if data['place'] is not None:
            if 'bounding_box' in data['place']:
                coords = np.mean(np.array(
                    data['place']['bounding_box']['coordinates'][0]),
                    axis=0)
        elif data['coordinates'] is not None:
            if 'coordinates' in data['coordinates']:
                coords = data['coordinates']['coordinates']

        if coords is not None:

            sid = SentimentIntensityAnalyzer()
            ss = sid.polarity_scores(data['text'])

            if OBSFUCATE_COLOR:
                hsl = []
                rgb = []
                colors = [v
                          for k, v in iteritems(COLORS)
                          if len(re.findall(r'{color}'.format(color=k),
                                            data['text'], re.IGNORECASE)) > 0]
                if len(colors) > 0:
                    hsl = [colorsys.rgb_to_hsv(*(np.array(c) / 255.))
                           for c in colors]
                    rgb = [np.array(c) / 255. for c in colors]
                    write_color_row(coords, rgb, hsl, ss)

            tags = [t for t in TAGS
                    if len(re.findall(r'{tag}'.format(tag=t),
                                      data['text'], re.IGNORECASE)) > 0]
            if len(tags) > 0:
                write_tag_row(coords, ss)


@app.task(bind=True, max_retries=3, soft_time_limit=10,
          name='remove_old_tweets')
def remove_old_tweets(task):
    client = MongoClient(MongoConfig.HOST, MongoConfig.PORT)
    db = client[MongoConfig.DATABASE]
    color_collection = db[MongoConfig.COLOR_COLLECTION]
    tag_collection = db[MongoConfig.TAG_COLLECTION]
    for collection in [tag_collection, color_collection]:
        n = collection.count({})
        if n > 1000:
            n -= 1000
            dt = list(collection.find(projection={'_id': False}).sort(
                '_id', 1).limit(n))[-1]['date']
            collection.remove({'date': {'$lt': dt}})
