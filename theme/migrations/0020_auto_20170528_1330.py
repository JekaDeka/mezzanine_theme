# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-05-28 10:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theme', '0019_auto_20170528_1330'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='ended',
            field=models.DateTimeField(blank=True, help_text='оставьте пустым, если срок неограничен.', null=True, verbose_name='Крайний срок'),
        ),
    ]