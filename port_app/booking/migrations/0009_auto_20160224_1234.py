# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-24 12:34
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0008_auto_20160224_1221'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='booking',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='owner',
        ),
        migrations.DeleteModel(
            name='Invoice',
        ),
    ]
