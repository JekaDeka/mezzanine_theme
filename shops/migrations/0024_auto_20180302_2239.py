# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-03-02 19:39
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0023_auto_20180302_2238'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='user_adress',
            new_name='user_address',
        ),
    ]