#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from celery import Celery
from dystwitic.config import CeleryConfig
"""Launcher for `celery beat`. `celery beat` processes repetitive tasks on
specified inetervals (map creation using RBF, deletion of old records in
Mongo, etc.). These tasks are specified and configured in the `CeleryConfig`
object in the `dystwitic.config` module. The tasks are stored in the
`dystwitic.work.tasks` module.
"""

BEAT_APP_NAME = 'dystwitic_dev'
BEAT_APP_TASKS_MODULE = 'dystwitic.work.tasks'

app = Celery(
    BEAT_APP_NAME,
    include=[BEAT_APP_TASKS_MODULE, ])

app.config_from_object(CeleryConfig)


if __name__ == '__main__':
    app.start()
