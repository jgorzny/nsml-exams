# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-05-08 02:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0020_previewcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='previewcode',
            name='preview_author',
            field=models.CharField(default='None yet', max_length=200),
        ),
    ]
