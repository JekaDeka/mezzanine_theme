# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-02-28 21:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0014_auto_20180228_2343'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='shop_slug',
            field=models.CharField(default='a', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orderitem',
            name='shop_slug',
            field=models.CharField(default='a', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='shop_image',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='shop_image',
            field=models.CharField(max_length=200, null=True),
        ),
    ]