# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-30 23:46
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0004_auto_20160523_2025'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='last_used',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name='date last used'),
        ),
        migrations.AddField(
            model_name='question',
            name='num_used',
            field=models.PositiveIntegerField(default=0),
        ),
    ]