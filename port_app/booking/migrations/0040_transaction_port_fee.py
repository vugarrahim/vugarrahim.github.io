# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-09 09:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0039_auto_20160308_1358'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='port_fee',
            field=models.FloatField(default=0, verbose_name='Cargo fee'),
        ),
    ]
