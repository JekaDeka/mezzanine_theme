# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-05-18 11:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0009_shopproduct_comments_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopproduct',
            name='slug',
            field=models.URLField(default='', editable=False, unique=True),
        ),
    ]
