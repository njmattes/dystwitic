#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dystwitic import app
from dystwitic.web.socket import sio


if __name__ == '__main__':
    sio.run(app)