# Generated by Django 3.1.4 on 2020-12-03 22:28

import app.models
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import enumfields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_device_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='HomeDevice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_uid', models.CharField(max_length=100)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('type', enumfields.fields.EnumField(enum=app.models.DeviceType, max_length=40)),
                ('home', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.home')),
            ],
            options={
                'db_table': 'home_device',
                'unique_together': {('home', 'device_uid')},
            },
        ),
        migrations.AlterField(
            model_name='farmdata',
            name='timestamp',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now),
        ),
        migrations.CreateModel(
            name='HomeDeviceData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=None, null=True)),
                ('timestamp', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('home_device', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.homedevice')),
            ],
            options={
                'db_table': 'home_device_data',
            },
        ),
    ]
