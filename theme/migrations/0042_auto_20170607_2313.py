# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-06-07 20:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theme', '0041_auto_20170607_2302'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usershop',
            name='image',
            field=models.ImageField(blank=True, default='', upload_to='U:\\WORK\\Tanya\\handmade\\HelloDjango\\static\\media', verbose_name='Логотип магазина'),
        ),
    ]