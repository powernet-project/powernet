# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-06-15 14:21
from __future__ import unicode_literals

import app.models
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import enumfields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_powernetuser_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='FarmDevice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('type', enumfields.fields.EnumField(enum=app.models.DeviceType, max_length=40)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('home', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Home')),
            ],
            options={
                'db_table': 'farm_device_data',
            },
        ),
    ]
