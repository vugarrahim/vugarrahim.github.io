# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-02 14:18
from __future__ import unicode_literals

import booking.utils.tools
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0019_remove_bookinginformation_booking_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booking_id', models.CharField(default=booking.utils.tools.rand_key, max_length=15, unique=True)),
                ('booking_type', models.CharField(choices=[('1', 'One way'), ('2', 'Return')], max_length=25)),
                ('transit_type', models.CharField(choices=[('transit', 'Transit'), ('non transit', 'Non Transit')], max_length=25)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
