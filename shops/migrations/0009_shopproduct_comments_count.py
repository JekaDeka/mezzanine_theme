# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-05-17 22:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0008_shopproduct_size'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopproduct',
            name='comments_count',
            field=models.IntegerField(default=0, editable=False),
        ),
    ]
