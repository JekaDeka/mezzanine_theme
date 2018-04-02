# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2018-02-22 05:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0006_remove_userprofile_comments_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='rating_average',
            field=models.FloatField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='rating_count',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='rating_sum',
            field=models.IntegerField(default=0, editable=False),
        ),
    ]