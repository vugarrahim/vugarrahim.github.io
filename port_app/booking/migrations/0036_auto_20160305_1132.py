# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-05 11:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0035_auto_20160305_1106'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vesselsschedule',
            name='current_cargo_capacity',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='vesselsschedule',
            name='current_passenger_count',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
