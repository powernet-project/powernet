from __future__ import absolute_import, unicode_literals
from celery import shared_task
from app.core.views.global_controller.gc_main import *


@shared_task
def run_global_controller(p_forecast, r_forecast, q_zero):
    arb = run_gc(p_forecast, r_forecast, q_zero)
    return arb
