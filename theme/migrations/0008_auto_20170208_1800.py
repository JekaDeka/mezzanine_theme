# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-02-08 15:00
from __future__ import unicode_literals

from django.db import migrations
import mezzanine.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('theme', '0007_myprofile_bio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myprofile',
            name='bio',
            field=mezzanine.core.fields.RichTextField(default='', verbose_name='Биография'),
        ),
    ]
