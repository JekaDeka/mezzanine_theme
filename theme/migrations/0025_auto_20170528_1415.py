# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-05-28 11:15
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('theme', '0024_auto_20170528_1414'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='author',
            field=models.ForeignKey(default=None, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
