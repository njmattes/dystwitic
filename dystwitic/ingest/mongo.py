# -*- coding: utf-8 -*-
from __future__ import division
from datetime import datetime
from pymongo import MongoClient
from dystwitic.config import MongoConfig
"""Functions for ingesting data from twitter streams into a Mongo as
JSON records of color and sentiment.
"""


client = MongoClient(MongoConfig.HOST, MongoConfig.PORT)
db = client[MongoConfig.DATABASE]
color_collection = db[MongoConfig.COLOR_COLLECTION]
tag_collection = db[MongoConfig.TAG_COLLECTION]


def write_color_row(coords, rgb, hsl, ss):
    color_collection.insert_one({
        'lon': coords[0],
        'lat': coords[1],
        'r': [r[0] for r in rgb],
        'g': [r[1] for r in rgb],
        'b': [r[2] for r in rgb],
        'h': [h[0] for h in hsl],
        's': [h[1] for h in hsl],
        'l': [h[2] for h in hsl],
        'pos': ss['pos'],
        'neu': ss['neu'],
        'neg': ss['neg'],
        'compound': ss['compound'],
        'date': datetime.utcnow(),
    })


def write_tag_row(coords, ss):
    tag_collection.insert_one({
        'lon': coords[0],
        'lat': coords[1],
        'pos': ss['pos'],
        'neu': ss['neu'],
        'neg': ss['neg'],
        'compound': ss['compound'],
        'date': datetime.utcnow(),
    })
