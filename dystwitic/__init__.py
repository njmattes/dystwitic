# -*- coding: utf-8 -*-
from flask import Flask
from flask_compress import Compress
from flask_assets import Bundle, Environment
from dystwitic.web.views import mod as dystwitic_mod


app = Flask(__name__)
app.config.from_object('dystwitic.config.FlaskConfig')
Compress(app)
assets = Environment(app)

app.register_blueprint(dystwitic_mod)

js = Bundle('js/vendors/d3/d3-selection.v1.min.js',
            'js/vendors/d3/d3-color.v1.min.js',
            'js/vendors/d3/d3-path.v1.min.js',
            'js/vendors/d3/d3-polygon.v1.min.js',
            'js/vendors/d3/d3-shape.v1.min.js',
            'js/vendors/d3/d3-collection.v1.min.js',
            'js/vendors/d3/d3-dispatch.v1.min.js',
            'js/vendors/d3/d3-dsv.v1.min.js',
            'js/vendors/d3/d3-request.v1.min.js',
            filters='jsmin', output='gen/dystwitic.d3.v0.js')
assets.register('js_d3', js)

js = Bundle('js/vendors/socket.io.1.3.6.min.js',
            'js/app/dystwitic_socket.v0.js',
            filters='jsmin', output='gen/dystwitic.v0.js')
assets.register('js_app', js)
