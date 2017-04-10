#!/usr/bin/env python
# -*- coding: utf-8 -*-
import redis


cache = redis.Redis(host='localhost', port=6379, db=1)
