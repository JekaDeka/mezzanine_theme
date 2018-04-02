# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-03-07 14:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0010_auto_20180307_1719'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='status',
            field=models.CharField(choices=[(0, 'Покупатель'), (1, 'Мастер')], default=0, help_text='Будучи мастером вы сможете получать персональные заказ', max_length=255, verbose_name='Тип профиля'),
        ),
    ]