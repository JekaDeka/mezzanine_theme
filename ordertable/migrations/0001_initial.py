# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-02-26 13:30
from __future__ import unicode_literals

import datetime
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import mezzanine.core.fields
import ordertable.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderTableItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500, verbose_name='Название')),
                ('active', models.BooleanField(default=True, editable=False, verbose_name='Открыт')),
                ('created', models.DateField(default=datetime.date.today, editable=False, verbose_name='Дата добавления')),
                ('ended', models.DateField(blank=True, help_text='Оставьте пустым, если срок неограничен.', null=True, validators=[ordertable.models.validate_today], verbose_name='Крайний срок')),
                ('price', models.DecimalField(blank=True, decimal_places=0, default=0, help_text='Если Вы не представляете, сколько подобная работа могла бы стоить, оставьте поле незаполненным.', max_digits=8, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Бюджет')),
                ('count', models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Количество')),
                ('color_suggest', models.CharField(blank=True, default='', help_text='Пример: «небесно-голубой» или «любой».', max_length=500, verbose_name='Пожелания к цвету')),
                ('size_suggest', models.CharField(blank=True, default='', help_text='Пример: «с футбольный мяч» или «длина - 30 см».', max_length=500, verbose_name='Пожелания к размерам')),
                ('material_suggest', models.CharField(blank=True, default='', help_text='Пример: шерсть', max_length=500, verbose_name='Пожелания к материалам')),
                ('lock_in_region', models.BooleanField(default=False, help_text='Мастера из других регионов не получат уведомление о Вашем заказе', verbose_name='Только мой регион')),
                ('description', mezzanine.core.fields.RichTextField(default='', help_text='Как можно более подробно опишите желаемое изделие.', verbose_name='Подробное описание')),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders_author', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Заказы',
                'verbose_name_plural': 'Мои заявки',
                'ordering': ('-created',),
                'permissions': (('view_ordertableitem', 'View order item'),),
            },
        ),
        migrations.CreateModel(
            name='OrderTableItemCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500, verbose_name='Title')),
                ('slug', models.CharField(blank=True, help_text='Leave blank to have the URL auto-generated from the title.', max_length=2000, null=True, verbose_name='URL')),
                ('site', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='sites.Site')),
            ],
            options={
                'verbose_name': 'Вид работы',
                'verbose_name_plural': 'Виды работ',
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='OrderTableItemImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', mezzanine.core.fields.FileField(blank=True, help_text='Загрузите фотографии эскизов или примеров, которые помогут мастерам точнее понять Ваш заказ.', max_length=255, null=True, verbose_name='Изображение')),
                ('description', models.CharField(blank=True, max_length=100, verbose_name='Описание')),
                ('ordertableitem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='ordertable.OrderTableItem')),
            ],
            options={
                'verbose_name': 'Изображение',
                'verbose_name_plural': 'Изображения',
            },
        ),
        migrations.CreateModel(
            name='OrderTableItemRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_requests', to='ordertable.OrderTableItem', verbose_name='Заказы')),
                ('performer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_performers', to=settings.AUTH_USER_MODEL, verbose_name='Исполнители')),
            ],
            options={
                'verbose_name': 'Отклики',
                'verbose_name_plural': 'Отклики на заявки',
                'ordering': ('order',),
            },
        ),
        migrations.AddField(
            model_name='ordertableitem',
            name='categories',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ordertableitems', to='ordertable.OrderTableItemCategory', verbose_name='Виды работ'),
        ),
        migrations.AddField(
            model_name='ordertableitem',
            name='performer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders_perfmoer', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='OrderTableItemRequest',
            unique_together=set([('order', 'performer')]),
        ),
    ]