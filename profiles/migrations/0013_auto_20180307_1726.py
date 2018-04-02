# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-03-07 14:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0012_auto_20180307_1726'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='status',
            field=models.IntegerField(choices=[(0, 'Покупатель'), (1, 'Мастер')], default=0, help_text='Будучи мастером вы сможете получать персональные заказ', verbose_name='Тип профиля'),
        ),
    ]