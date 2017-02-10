# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-02-09 09:14
from __future__ import unicode_literals

from django.db import migrations, models
import mezzanine.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('theme', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Slider',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('featured_image', mezzanine.core.fields.FileField(blank=True, max_length=255, null=True, verbose_name='Featured Image')),
                ('short_description', mezzanine.core.fields.RichTextField(blank=True)),
                ('href', models.CharField(blank=True, help_text='A link to the blog (optional)', max_length=2000)),
            ],
            options={
                'verbose_name': 'Slider item',
                'verbose_name_plural': 'Slider items',
            },
        ),
    ]
