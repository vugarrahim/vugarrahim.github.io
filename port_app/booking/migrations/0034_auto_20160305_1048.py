# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-05 10:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0033_auto_20160305_0827'),
    ]

    operations = [
        migrations.AddField(
            model_name='vesselsschedule',
            name='current_cargo_capacity',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='vesselsschedule',
            name='current_passenger_count',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
