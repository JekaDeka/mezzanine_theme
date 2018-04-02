# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-02-28 21:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0015_auto_20180301_0015'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='shop_name',
            field=models.CharField(default='Тестовый магазин', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orderitem',
            name='shop_name',
            field=models.CharField(default='Тестовый', max_length=255),
            preserve_default=False,
        ),
    ]