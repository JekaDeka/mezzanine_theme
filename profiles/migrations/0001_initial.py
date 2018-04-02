# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2018-02-20 16:17
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import mezzanine.core.fields
import smart_selects.db_fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Регион')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Страна')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Регион')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.Country')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255, verbose_name='Имя')),
                ('last_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Фамилия')),
                ('image', models.ImageField(default='', upload_to='tmp_images/', verbose_name='Ваше изображение')),
                ('phone', models.CharField(blank=True, max_length=255, verbose_name='Телефон')),
                ('allow_blogpost_count', models.PositiveIntegerField(default=10, verbose_name='Разрешенное количество записей в Блоге')),
                ('allow_product_count', models.PositiveIntegerField(default=10, verbose_name='Разрешенное количество товаров в магазине')),
                ('bio', mezzanine.core.fields.RichTextField(blank=True, default='', verbose_name='О себе')),
                ('city', smart_selects.db_fields.ChainedForeignKey(auto_choose=True, chained_field='region', chained_model_field='region', on_delete=django.db.models.deletion.CASCADE, to='profiles.City', verbose_name='Город')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.Country', verbose_name='Страна')),
                ('region', smart_selects.db_fields.ChainedForeignKey(auto_choose=True, chained_field='country', chained_model_field='country', on_delete=django.db.models.deletion.CASCADE, to='profiles.Region', verbose_name='Регион')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='city',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.Country'),
        ),
        migrations.AddField(
            model_name='city',
            name='region',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.Region'),
        ),
    ]
