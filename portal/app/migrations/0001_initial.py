# Generated by Django 3.0.6 on 2020-05-06 02:48

import app.models
from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import enumfields.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('type', enumfields.fields.EnumField(enum=app.models.DeviceType, max_length=40)),
                ('status', enumfields.fields.EnumField(default='UNKNOWN', enum=app.models.DeviceStatus, max_length=40)),
                ('value', models.IntegerField(default=0)),
                ('cosphi', models.FloatField(default=1.0)),
            ],
            options={
                'db_table': 'device',
            },
        ),
        migrations.CreateModel(
            name='EcobeeDevice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_key', models.CharField(max_length=100)),
                ('access_token', models.CharField(max_length=100)),
                ('refresh_token', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'ecobee',
            },
        ),
        migrations.CreateModel(
            name='Home',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('location', models.CharField(max_length=1000)),
                ('type', enumfields.fields.EnumField(default='UNKNOWN', enum=app.models.HomeType, max_length=20)),
            ],
            options={
                'db_table': 'home',
            },
        ),
        migrations.CreateModel(
            name='HueStates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', enumfields.fields.EnumField(default='UNKNOWN', enum=app.models.HueStatesType, max_length=40)),
            ],
            options={
                'db_table': 'hue_states',
            },
        ),
        migrations.CreateModel(
            name='UtilityEnergyPrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('price', models.FloatField()),
                ('timestamp_in_utc_millis', models.CharField(max_length=30)),
            ],
            options={
                'db_table': 'energy_price',
            },
        ),
        migrations.CreateModel(
            name='PowernetUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', enumfields.fields.EnumField(default='HOME', enum=app.models.PowernetUserType, max_length=10)),
                ('first_name', models.CharField(max_length=50, null=True)),
                ('last_name', models.CharField(max_length=50, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_access_dt_stamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'powernet_user',
            },
        ),
        migrations.CreateModel(
            name='HomeData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reactive_power', models.FloatField(default=0)),
                ('real_power', models.FloatField(default=0)),
                ('state_of_charge', models.FloatField(default=0)),
                ('dt_stamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('home', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Home')),
            ],
            options={
                'db_table': 'home_data',
            },
        ),
        migrations.AddField(
            model_name='home',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.PowernetUser'),
        ),
        migrations.CreateModel(
            name='FarmMaxDemand',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('max_power', models.FloatField(default=0)),
                ('month_pst', models.IntegerField(default=0)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('home', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Home')),
            ],
            options={
                'db_table': 'farm_max_power_demand',
            },
        ),
        migrations.CreateModel(
            name='FarmDevice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_uid', models.CharField(max_length=100)),
                ('type', enumfields.fields.EnumField(enum=app.models.DeviceType, max_length=40)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('home', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Home')),
            ],
            options={
                'db_table': 'farm_device',
                'unique_together': {('home', 'device_uid')},
            },
        ),
        migrations.CreateModel(
            name='FarmData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=None, null=True)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('farm_device', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.FarmDevice')),
            ],
            options={
                'db_table': 'farm_device_data',
            },
        ),
        migrations.CreateModel(
            name='DeviceState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('watt_consumption', models.FloatField()),
                ('measurement_timestamp', models.DateTimeField()),
                ('additional_information', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Device')),
            ],
            options={
                'db_table': 'device_state',
            },
        ),
        migrations.AddField(
            model_name='device',
            name='home',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Home'),
        ),
        migrations.CreateModel(
            name='ApplianceJsonData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('devices_json', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('home', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Home')),
            ],
            options={
                'db_table': 'appliance_data',
            },
        ),
    ]
