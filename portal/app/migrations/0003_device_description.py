# Generated by Django 3.0.6 on 2020-05-06 02:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_home_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='description',
            field=models.CharField(max_length=1000, null=True),
        ),
    ]
