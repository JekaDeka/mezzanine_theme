# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-03-11 23:19
from __future__ import unicode_literals

from django.db import migrations
import mezzanine.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('theme', '0009_auto_20170301_2144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myprofile',
            name='image',
            field=mezzanine.core.fields.FileField(blank=True, max_length=255, null=True, verbose_name='Изображение'),
        ),
    ]