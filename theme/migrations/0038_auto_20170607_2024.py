# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-06-07 17:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theme', '0037_auto_20170607_2006'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usershop',
            name='image',
            field=models.ImageField(blank=True, default='', upload_to='myprofile', verbose_name='Логотип магазина'),
        ),
    ]
