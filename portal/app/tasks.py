from __future__ import absolute_import, unicode_literals
import random
from celery import shared_task


@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    total = x * (y * random.randint(3, 100))
    return total


@shared_task
def xsum(numbers):
    return sum(numbers)
