# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-16 12:58
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_auto_20160305_1235'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='myuser',
            options={'permissions': (('user_view', 'Can view User'), ('user_all_view', 'Can view ALL User'), ('user_super_create', 'Can view ALL User'))},
        ),
    ]
