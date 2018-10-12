#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import namedtuple, Counter
from datetime import datetime
from six import iteritems
import numpy as np
from scipy.interpolate import interp1d, Rbf
from pymongo import MongoClient
from dystwitic.constants import OBSFUCATE_COLOR, COLORS, RASTER
from dystwitic.config import MongoConfig


def make_map():
    """Generate the JSON used for drawing the map in the client.
    This JSON is cached in `redis` with a task monitored by the `celery beat`
    scheduler.
    """
    client = MongoClient(MongoConfig.HOST, MongoConfig.PORT)
    db = client[MongoConfig.DATABASE]
    color_collection = db[MongoConfig.COLOR_COLLECTION]
    tag_collection = db[MongoConfig.TAG_COLLECTION]

    raster_x = RASTER.shape[1]
    raster_y = RASTER.shape[0]

    # How many tweets will we be basing the map on
    data_display_idxs = 50

    if OBSFUCATE_COLOR:
        """Get colors from tweets to create a ridiculous color scale.
        This is essentially mapping colors to sentiment values, based
        on the calculated sentiments of tweets that contain color
        terms. 
        """
        data_interp_idxs = 500
        data = list(color_collection.find(
            projection={'_id': False}
        ).sort('_id', -1).limit(data_interp_idxs))
        # FIXME: This is garnage. Do it all in one line bozo.
        xs, y1s, y2s, y3s = np.array(
            [[d['compound'], d['r'][i], d['g'][i], d['b'][i]]
             for d in data for i in range(len(d['r']))]).T
        ys = np.vstack((y1s, y2s, y3s))
    else:
        xs = np.array([1, .75, .5, .25, 0, -.25, -.5, -.75, -1., ])
        ys = np.array(COLORS).T / 255.

    args_idx = np.argsort(xs)

    # These callables map in input (a sentiment) to an output
    # (a red, green, or blue value)
    frgb = interp1d(xs[args_idx], ys[:, args_idx], kind='linear',
                  fill_value='extrapolate')

    # Get tweets from mongo
    data = list(tag_collection.find(
        projection={'_id': False}
    ).sort('_id', -1).limit(data_display_idxs))

    # Get compound sentiment from tweets and get a sorted index
    sentiments = np.array([x['compound'] for x in data])
    args_idx = np.argsort(sentiments)

    # Get lons and lates from tweets and order by sentiment
    lons = np.array([x['lon'] for x in data])[args_idx]
    lats = np.array([x['lat'] for x in data])[args_idx]
    # Create a weighting vector based on how recent the tweets are
    time_wts = np.array([abs((x['date'] - datetime.now()).total_seconds())
                         for x in data])[args_idx]
    time_wts = np.exp(time_wts/-31536000.)
    # Generate RGB values for each tweet
    rgbs = frgb(sentiments[args_idx] * time_wts)
    # Shift points when they overlap
    lons, lats = move_dupes(lons, lats)

    xg = np.linspace(-180, 180, raster_x)
    yg = np.linspace(90, -90, raster_y)
    X, Y = np.meshgrid(xg, yg)
    X = np.ma.masked_array(X, np.logical_not(RASTER))
    Y = np.ma.masked_array(Y, np.logical_not(RASTER))

    fine = coordinates(X, Y)
    interp = coordinates(lons, lats)

    try:
        arr = vrbf(np.tile(interp.x, (3, 1)),
                   np.tile(interp.y, (3, 1)),
                   np.tile(interp.z, (3, 1)),
                   rgbs,
                   np.tile(fine.x, (3, 1, 1)),
                   np.tile(fine.y, (3, 1, 1)),
                   np.tile(fine.z, (3, 1, 1)), )
        arr = np.rollaxis(arr, 0, 3)
        arr = arr * RASTER.reshape((raster_y, raster_x, 1))
        return [[None if np.isnan(p) else round(p, 2) for p in t]
                for r in arr for t in r]

    except:
        return False


def coordinates(lons, lats):
    """Generate polar and xyz coordinates for each lonlat pair"""
    phi = lats * np.pi / 180.
    theta = lons * np.pi / 180.
    coords = namedtuple('Coords', 'phi theta x y z')
    x = np.cos(phi) * np.cos(theta) * -1
    y = np.cos(phi) * np.sin(theta)
    z = np.sin(phi)
    return coords(phi, theta, x, y, z)


def move_dupes(lons, lats):
    """Shift overlapping points"""
    r = .001
    for dupe_lon in [item for item, counter in iteritems(Counter(lons))
                     if counter > 1]:
        idx = np.where(lons == dupe_lon)[0]
        for i, lon_idx in enumerate(idx):
            lons[lon_idx] += r * np.cos(2 * np.pi * i / len(idx))
            lats[lon_idx] += r * np.sin(2 * np.pi * i / len(idx))

    return lons, lats


def get_rbf(x, y, z, d, x1, y1, z1):
    rbf = Rbf(x, y, z, d, function='linear')
    return rbf(x1, y1, z1)


vrbf = np.vectorize(
    get_rbf,
    signature='(m),(m),(m),(m),(p,r),(p,r),(p,r)->(p,r)')



if __name__ == '__main__':
    import time
    start_time = time.time()
    make_map()
    print('make_map(): {}s'.format(time.time()-start_time, ))
    start_time = time.time()
    make_map_original()
    print('make_map_original(): {}s'.format(time.time()-start_time, ))


