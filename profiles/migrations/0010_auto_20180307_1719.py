# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-03-07 14:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0009_auto_20180307_1719'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='condition',
            new_name='status',
        ),
    ]