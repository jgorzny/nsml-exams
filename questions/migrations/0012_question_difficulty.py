# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-16 01:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0011_auto_20160612_1817'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='difficulty',
            field=models.CharField(choices=[('0', 'Very Easy'), ('1', 'Easy'), ('2', 'Medium'), ('3', 'Hard'), ('4', 'Very Hard')], default='0', max_length=1),
        ),
    ]
