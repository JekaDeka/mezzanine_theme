# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-05-28 10:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theme', '0017_auto_20170528_1320'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='work_type',
            field=models.CharField(choices=[('Любой', 'Любой'), ('Аксессуары', 'Аксессуары'), ('Дизайн и реклама', 'Дизайн и реклама'), ('Для дома и интерьера', 'Для дома и интерьера'), ('Музыкальные инструменты', 'Музыкальные инструменты'), ('Обувь ручной работы', 'Обувь ручной работы'), ('Одежда', 'Одежда'), ('Открытки', 'Открытки'), ('Подарки к праздникам', 'Подарки к праздникам'), ('Посуда', 'Посуда'), ('Работы для детей', 'Работы для детей'), ('Русский стиль', 'Русский стиль'), ('Для домашних животных', 'Для домашних животных'), ('Канцелярские товары', 'Канцелярские товары'), ('Картины и панно', 'Картины и панно'), ('Косметика ручной работы', 'Косметика ручной работы'), ('Куклы и игрушки', 'Куклы и игрушки'), ('Материалы для творчества', 'Материалы для творчества'), ('Свадебный салон', 'Свадебный салон'), ('Субкультуры', 'Субкультуры'), ('Сувениры и подарки', 'Сувениры и подарки'), ('Сумки и аксессуары', 'Сумки и аксессуары'), ('Украшения', 'Украшения'), ('Фен-шуй и эзотерика', 'Фен-шуй и эзотерика'), ('Цветы и флористика', 'Цветы и флористика')], default='Любой', max_length=55, verbose_name='Вид работы'),
        ),
    ]
