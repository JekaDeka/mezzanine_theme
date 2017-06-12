# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-06-09 16:24
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.CITIES_COUNTRY_MODEL),
        migrations.swappable_dependency(settings.CITIES_CITY_MODEL),
        ('theme', '0046_auto_20170609_1906'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usershop',
            name='city',
        ),
        migrations.AddField(
            model_name='usershop',
            name='city',
            field=models.ManyToManyField(to=settings.CITIES_CITY_MODEL, verbose_name='Город'),
        ),
        migrations.RemoveField(
            model_name='usershop',
            name='country',
        ),
        migrations.AddField(
            model_name='usershop',
            name='country',
            field=models.ManyToManyField(to=settings.CITIES_COUNTRY_MODEL, verbose_name='Страна'),
        ),
    ]
