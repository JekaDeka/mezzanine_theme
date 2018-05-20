# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-05-15 22:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0002_auto_20180513_1646'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.IntegerField(choices=[(1, 'Новый'), (2, 'В обработке'), (3, 'Завершенный'), (4, 'Отмененный')], default=1, verbose_name='Status'),
        ),
    ]