# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-09 08:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking_payment', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentinfo',
            name='hash_code',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
