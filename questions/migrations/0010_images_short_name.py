# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-06 23:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0009_images_figure_source'),
    ]

    operations = [
        migrations.AddField(
            model_name='images',
            name='short_name',
            field=models.TextField(default='filename', max_length=200),
        ),
    ]