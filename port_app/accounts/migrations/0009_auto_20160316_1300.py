# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-16 13:00
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_auto_20160316_1258'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='myuser',
            options={'permissions': (('user_view', 'Can view User'), ('user_all_view', 'Can view ALL User'), ('user_super_create', 'Can view super create User'))},
        ),
    ]
