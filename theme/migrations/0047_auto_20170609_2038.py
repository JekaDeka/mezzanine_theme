# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-06-09 17:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theme', '0046_auto_20170609_2028'),
    ]

    operations = [
        migrations.AddField(
            model_name='usershop',
            name='payment_other',
            field=models.CharField(blank=True, help_text='Опишите любые другие условия и важные моменты по оплате — покупателю будет проще принять решение о покупке в вашем магазине.', max_length=255, verbose_name='Дополнительная информация об оплате'),
        ),
        migrations.AlterField(
            model_name='usershop',
            name='express_other',
            field=models.CharField(blank=True, help_text='Адреса, по которым покупатель сможет забрать товар самостоятельно. Любые другие нюансы и условия по доставке.', max_length=255, verbose_name='Дополнительная информация о доставке'),
        ),
    ]
