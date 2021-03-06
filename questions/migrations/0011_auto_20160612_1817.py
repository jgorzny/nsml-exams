# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-12 22:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0010_images_short_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='images',
            name='figure_source',
            field=models.TextField(default='Figure source', max_length=2000),
        ),
        migrations.AlterField(
            model_name='question',
            name='answer_text',
            field=models.TextField(default='Answer source', max_length=2000),
        ),
        migrations.AlterField(
            model_name='question',
            name='question_instructions',
            field=models.TextField(default='Instructions source', max_length=2000),
        ),
        migrations.AlterField(
            model_name='question',
            name='question_text',
            field=models.TextField(default='Question source', max_length=2000),
        ),
        migrations.AlterField(
            model_name='tables',
            name='table',
            field=models.TextField(default='Table source', max_length=2000),
        ),
    ]
