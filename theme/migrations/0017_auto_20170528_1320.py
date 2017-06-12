# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-05-28 10:20
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import mezzanine.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('theme', '0016_auto_20170528_1301'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='work_type',
            field=models.CharField(choices=[('Любой', 'Любой'), ('Аксессуары', 'Аксессуары'), ('Дизайн и реклама', 'Дизайн и реклама'), ('Для дома и интерьера', 'Для дома и интерьера'), ('Музыкальные инструменты', 'Музыкальные инструменты'), ('Обувь ручной работы', 'Обувь ручной работы'), ('Одежда', 'Одежда'), ('Открытки', 'Открытки'), ('Подарки к праздникам', 'Подарки к праздникам'), ('Посуда', 'Посуда'), ('Работы для детей', 'Работы для детей'), ('Русский стиль', 'Русский стиль'), ('Для домашних животных', 'Для домашних животных'), ('Канцелярские товары', 'Канцелярские товары'), ('Картины и панно', 'Картины и панно'), ('Косметика ручной работы', 'Косметика ручной работы'), ('Куклы и игрушки', 'Куклы и игрушки'), ('Материалы для творчества', 'Материалы для творчества'), ('Свадебный салон', 'Свадебный салон'), ('Субкультуры', 'Субкультуры'), ('Сувениры и подарки', 'Сувениры и подарки'), ('Сумки и аксессуары', 'Сумки и аксессуары'), ('Украшения', 'Украшения'), ('Фен-шуй и эзотерика', 'Фен-шуй и эзотерика'), ('Цветы и флористика', 'Цветы и флористика')], default='Любой', max_length=55),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='author',
            field=models.ForeignKey(default=1, editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='color_suggest',
            field=models.CharField(default='', help_text='Пример: «небесно-голубой» или «любой».', max_length=500, null=True, verbose_name='Пожелания к цвету'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='description',
            field=mezzanine.core.fields.RichTextField(default='', help_text='Как можно более подробно опишите желаемое изделие.', verbose_name='Подробное описание'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='featured_image',
            field=mezzanine.core.fields.FileField(blank=True, help_text='Загрузите фотографии эскизов или примеров, которые помогут мастерам точнее понять Ваш заказ.', max_length=255, null=True, verbose_name='Изображение'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='material_suggest',
            field=models.CharField(default='', help_text='Пример: шерсть', max_length=500, verbose_name='Пожелания к материалам'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Если Вы не представляете, сколько подобная работа могла бы стоить, оставьте поле незаполненным.', max_digits=8, null=True, verbose_name='Бюджет'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='size_suggest',
            field=models.CharField(default='', help_text='Пример: «с футбольный мяч» или «длина - 30 см».', max_length=500, verbose_name='Пожелания к размерам'),
        ),
    ]
