# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-31 16:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0008_auto_20160531_1223'),
    ]

    operations = [
        migrations.AddField(
            model_name='images',
            name='figure_source',
            field=models.TextField(default='Figure source', max_length=200),
        ),
    ]
