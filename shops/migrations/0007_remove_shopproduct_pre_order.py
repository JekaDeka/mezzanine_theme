# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-05-17 22:01
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0006_auto_20180517_1956'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shopproduct',
            name='pre_order',
        ),
    ]