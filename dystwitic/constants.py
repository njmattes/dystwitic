#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from scipy import misc


BASE_DIR = os.path.abspath(os.path.dirname(__file__))

OBSFUCATE_COLOR = False

COLOR_TERMS = {
    'blue':      [0, 136, 185],    # 5B 5/10
    'red':       [198, 86, 91],    # 5R 5/10
    'yellow':    [255, 223, 0],    # 9Y 9/18
    'orange':    [184, 100, 31],   # 5YR 5/10
    'violet':    [152, 102, 180],  # 5P 5/10
    'purple':    [188, 88, 37],    # 5RP 5/10
    'green':     [0, 142, 99],     # 5G 5/10
    'brown':     [153, 75, 0],     # 5YR 4/10
    'pink':      [255, 165, 167],  # 5R 8/10
    'black':     [0, 0, 0],
    'white':     [255, 255, 255],
    'gray':      [128, 128, 128],
}

# 9 Oranges
COLORS = {
    'OR_PU': [
        [179, 88, 6], [224, 130, 20], [253, 184, 99], [254, 224, 182],
        [247, 247, 247], [216, 218, 235], [178, 171, 210],
        [128, 115, 172], [84, 39, 136],
    ],
    'OR': [
        [255, 247, 236], [254, 232, 200], [253, 212, 158], [253, 187, 132],
        [252, 141, 89], [239, 101, 72], [215, 48, 31], [179, 0, 0],
        [179, 0, 0],
    ],
    'BR_BG': [
        [140, 81, 10], [191, 129, 45], [223, 194, 125], [246, 232, 195],
        [245, 245, 245], [199, 234, 229], [128, 205, 193],
        [53, 151, 143], [1, 102, 94],
    ],
}['OR_PU']

TAGS = [
    # 'art',
    # 'action',
    # 'trump',
    'realdonaldtrump'
]

PIXEL = 5

RASTER = misc.imread(os.path.join(
        BASE_DIR, 'static', 'masks', 'wcs_{}deg.tif'.format(PIXEL)))