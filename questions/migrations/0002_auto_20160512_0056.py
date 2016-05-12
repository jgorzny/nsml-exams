# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-12 04:56
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='answer_text',
            field=models.TextField(default='Answer source', max_length=200),
        ),
        migrations.AddField(
            model_name='question',
            name='contributing_authors',
            field=models.CharField(default='None yet', max_length=200),
        ),
        migrations.AddField(
            model_name='question',
            name='figure_one',
            field=models.FileField(default='', upload_to=b''),
        ),
        migrations.AddField(
            model_name='question',
            name='figure_three',
            field=models.FileField(default='', upload_to=b''),
        ),
        migrations.AddField(
            model_name='question',
            name='figure_two',
            field=models.FileField(default='', upload_to=b''),
        ),
        migrations.AddField(
            model_name='question',
            name='initial_author',
            field=models.CharField(default='None yet', max_length=200),
        ),
        migrations.AddField(
            model_name='question',
            name='last_edited',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name='date last edited'),
        ),
        migrations.AddField(
            model_name='question',
            name='latex_figure_one',
            field=models.TextField(default='e.g. a table', max_length=200),
        ),
        migrations.AddField(
            model_name='question',
            name='latex_figure_three',
            field=models.TextField(default='e.g. a table', max_length=200),
        ),
        migrations.AddField(
            model_name='question',
            name='latex_figure_two',
            field=models.TextField(default='e.g. a table', max_length=200),
        ),
        migrations.AddField(
            model_name='question',
            name='num_edits',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='question',
            name='question_description',
            field=models.TextField(default='Description - web/comments only', max_length=200),
        ),
        migrations.AddField(
            model_name='question',
            name='question_instructions',
            field=models.TextField(default='Instructions source', max_length=200),
        ),
        migrations.AddField(
            model_name='question',
            name='question_notes',
            field=models.TextField(default='Question notes', max_length=200),
        ),
        migrations.AlterField(
            model_name='question',
            name='question_text',
            field=models.TextField(default='Question source', max_length=200),
        ),
    ]
