# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-03-02 16:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0021_auto_20180302_1651'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='user_middle_name',
            field=models.CharField(default='', max_length=255, verbose_name='Отчество'),
            preserve_default=False,
        ),
    ]