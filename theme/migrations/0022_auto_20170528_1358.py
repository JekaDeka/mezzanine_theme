# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-05-28 10:58
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theme', '0021_auto_20170528_1343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='created',
            field=models.DateField(default=datetime.date.today, editable=False, verbose_name='Дата добавления'),
        ),
    ]