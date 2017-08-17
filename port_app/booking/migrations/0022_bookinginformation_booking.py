# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-02 14:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0021_remove_bookinginformation_booking_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookinginformation',
            name='booking',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='booking.Booking'),
            preserve_default=False,
        ),
    ]