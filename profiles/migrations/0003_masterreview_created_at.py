# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-04-24 11:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_remove_masterreview_added_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='masterreview',
            name='created_at',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]