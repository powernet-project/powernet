from __future__ import absolute_import, unicode_literals
from celery import shared_task
from app.core.views.global_controller.gc_main import *


@shared_task
def run_global_controller():
    arb = run_gc()
    return arb


@shared_task
def wtf():
    return 100 * 6546 + 8
