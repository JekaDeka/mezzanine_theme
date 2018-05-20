# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-05-18 15:46
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0019_auto_20180518_1830'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shopproduct',
            options={'verbose_name': 'Товар', 'verbose_name_plural': 'Товары'},
        ),
        migrations.RemoveField(
            model_name='productreview',
            name='mastery',
        ),
        migrations.RemoveField(
            model_name='productreview',
            name='punctuality',
        ),
        migrations.RemoveField(
            model_name='productreview',
            name='responsibility',
        ),
        migrations.AddField(
            model_name='productreview',
            name='rating',
            field=models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], default=1, verbose_name='Рейтинг'),
        ),
        migrations.AlterField(
            model_name='productreview',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_reviews', to=settings.AUTH_USER_MODEL, verbose_name='Товар'),
        ),
    ]