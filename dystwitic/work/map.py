#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from collections import namedtuple, Counter
from datetime import datetime
from scipy import misc
from scipy.interpolate import interp1d, Rbf
from dystwitic.constants import BASE_DIR, PIXEL, OBSFUCATE_COLOR, COLORS


def make_map():
    """Generate the JSON used for drawing the map in the client.
    This JSON is cached in `redis` with a task monitored by the `celery beat`
    scheduler.
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


