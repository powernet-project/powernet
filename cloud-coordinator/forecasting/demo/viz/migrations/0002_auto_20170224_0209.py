# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-24 02:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viz', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='localweather',
            name='Clouds',
        ),
        migrations.RemoveField(
            model_name='localweather',
            name='SolarRadiation',
        ),
        migrations.AlterField(
            model_name='localweather',
            name='date',
            field=models.DateTimeField(),
        ),
    ]
