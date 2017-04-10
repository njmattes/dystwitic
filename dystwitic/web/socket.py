#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from math import fabs

from flask_socketio import SocketIO, emit

from dystwitic import app
from dystwitic.web.cache import cache
from dystwitic.work.tasks import cache_map

sio = SocketIO(app)


@sio.on('connect')
def connect():
    print('connected')


@sio.on('my request')
def my_map(data):
    t = datetime.now().second + 60
    if fabs(t - int(data['t'])) > 1 or data['f'] > 0:
        app_map = cache.get('map')
        if not app_map:
            app_map = cache_map()
    else:
        app_map = []
    emit('my response', {'map': app_map, 't': t, })


@sio.on('disconnect')
def disconnect():
    print('disconnect')


