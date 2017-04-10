# -*- coding: utf-8 -*-
import simplejson as json
from flask import Blueprint, render_template, Response

from dystwitic.web.cache import cache
from dystwitic.constants import PIXEL
from dystwitic.work.tasks import cache_map

mod = Blueprint('dystwitic', __name__)


@mod.route('/')
def index():
    return render_template(
        'index.html',
        pixel=PIXEL,
        pixels=int(360*180/PIXEL**2)
    )


@mod.route('/about')
def about():
    return render_template(
        'about.html',
    )


@mod.route('/bio')
def bio():
    return render_template(
        'bio.html',
    )


@mod.route('/matteson')
def matteson():
    return render_template(
        'matteson.html',
    )


@mod.route('/snyder-quinn')
def snyder_quinn():
    return render_template(
        'snyder-quinn.html',
    )


@mod.route('/get_map')
def get_map():
    app_map = cache.get('map')
    if not app_map:
        app_map = cache_map()
    return Response(
        json.dumps({'map': json.loads(app_map)}),
        mimetype='application/json',
    )

