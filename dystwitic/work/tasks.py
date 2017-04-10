#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from six import iteritems
import os
import re
import colorsys
from collections import namedtuple, Counter
from datetime import datetime
import simplejson as json
import numpy as np
from scipy import misc
from scipy.interpolate import interp1d, Rbf
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from dystwitic.constants import BASE_DIR, PIXEL, TAGS, OBSFUCATE_COLOR, \
    COLOR_TERMS, COLORS
from dystwitic.ingest.mongo import color_collection, tag_collection, \
    write_tag_row, write_color_row
from dystwitic.work.celery import app
from dystwitic.web.cache import cache
"""`celery` tasks.

These functions are monitored by `celery`. Repetitive tasks are scheduled and
run by `celerey`'s `beat` process. `celery beat` itself is launched and
monitored by `supervisord`. Other tasks are added to a queue as needed.

Options for these tasks can be set in the `CeleryConfig` object in the
`dystwitic.config` module.
"""


def make_map():
    """`celery beat` task for updating map information.

    Every interval, `celery beat` runs this function to update the
    JSON used for drawing the map in the client. This JSON is cached
    in `redis` using the `cache_map` function below.
    """
    raster = misc.imread(os.path.join(
        BASE_DIR, 'static', 'masks', 'wcs_{}deg.tif'.format(PIXEL)))
    raster_x = raster.shape[1]
    raster_y = raster.shape[0]

    data_display_idxs = 50

    def coordinates(lons, lats):
        phi = lats * np.pi / 180.
        theta = lons * np.pi / 180.
        coords = namedtuple('Coords', 'phi theta x y z')
        x = np.cos(phi) * np.cos(theta) * -1
        y = np.cos(phi) * np.sin(theta)
        z = np.sin(phi)
        return coords(phi, theta, x, y, z)

    def move_dupes():
        r = .001
        for dupe_lon in [item for item, counter in iteritems(Counter(lons))
                         if counter > 1]:
            idx = np.where(lons == dupe_lon)[0]
            for i, lon_idx in enumerate(idx):
                lons[lon_idx] += r * np.cos(2 * np.pi * i / len(idx))
                lats[lon_idx] += r * np.sin(2 * np.pi * i / len(idx))

    if OBSFUCATE_COLOR:
        data_interp_idxs = 500
        data = list(color_collection.find(
            projection={'_id': False}
        ).sort('_id', -1).limit(data_interp_idxs))

        xs, y1s, y2s, y3s = np.array(
            [[d['compound'], d['r'][i], d['g'][i], d['b'][i]]
             for d in data for i in range(len(d['r']))]).T
    else:
        xs = np.array([1, .75, .5, .25, 0, -.25, -.5, -.75, -1., ])
        y1s, y2s, y3s = np.array(COLORS).T / 255.

    args_idx = np.argsort(xs)

    f1 = interp1d(xs[args_idx], y1s[args_idx], kind='linear',
                  fill_value='extrapolate')
    f2 = interp1d(xs[args_idx], y2s[args_idx], kind='linear',
                  fill_value='extrapolate')
    f3 = interp1d(xs[args_idx], y3s[args_idx], kind='linear',
                  fill_value='extrapolate')

    data = list(tag_collection.find(
        projection={'_id': False}
    ).sort('_id', -1).limit(data_display_idxs))

    compound = np.array([x['compound'] for x in data])
    args_idx = np.argsort(compound)

    lons = np.array([x['lon'] for x in data])[args_idx]
    lats = np.array([x['lat'] for x in data])[args_idx]
    time_wt = np.array([abs((x['date'] - datetime.now()).total_seconds())
                        for x in data])[args_idx]

    rs = f1(compound[args_idx] * np.exp(time_wt/-31536000.))
    gs = f2(compound[args_idx] * np.exp(time_wt/-31536000.))
    bs = f3(compound[args_idx] * np.exp(time_wt/-31536000.))

    move_dupes()

    xg = np.linspace(-180, 180, raster_x)
    yg = np.linspace(90, -90, raster_y)
    X, Y = np.meshgrid(xg, yg)
    X = np.ma.masked_array(X, np.logical_not(raster))
    Y = np.ma.masked_array(Y, np.logical_not(raster))

    fine = coordinates(X, Y)
    interp = coordinates(lons, lats)

    try:
        method = 'linear'
        rbf = Rbf(interp.x, interp.y, interp.z, rs, function=method)
        huesg = rbf(fine.x, fine.y, fine.z)
        rbf = Rbf(interp.x, interp.y, interp.z, gs, function=method)
        satsg = rbf(fine.x, fine.y, fine.z)
        rbf = Rbf(interp.x, interp.y, interp.z, bs, function=method)
        valsg = rbf(fine.x, fine.y, fine.z)

        arr = np.stack((huesg, satsg, valsg), axis=2) * raster.reshape(
            (raster_y, raster_x, 1))

        return [[None if np.isnan(p) else round(p, 2) for p in t]
                for r in arr for t in r]

    except:

        return False


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
    for collection in [tag_collection, color_collection]:
        n = collection.count({})
        if n > 1000:
            n -= 1000
            dt = list(collection.find(projection={'_id': False}).sort(
                '_id', 1).limit(n))[-1]['date']
            collection.remove({'date': {'$lt': dt}})
