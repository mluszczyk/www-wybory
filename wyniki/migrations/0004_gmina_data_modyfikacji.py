# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-12 21:43
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('wyniki', '0003_auto_20160410_1935'),
    ]

    operations = [
        migrations.AddField(
            model_name='gmina',
            name='data_modyfikacji',
            field=models.DateTimeField(default=datetime.datetime(2016, 5, 12, 21, 43, 37, 5797, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
