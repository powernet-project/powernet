# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-07-16 19:44
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0019_auto_20190716_1942'),
    ]

    operations = [
        migrations.RenameField(
            model_name='farmdata',
            old_name='farmdevice',
            new_name='farm_device',
        ),
    ]