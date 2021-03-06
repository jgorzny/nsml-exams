# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-26 01:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0015_exam'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='figuresInAppendix',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='exam',
            name='imagesInFolder',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='exam',
            name='inputFiles',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='exam',
            name='layout',
            field=models.CharField(choices=[('0', 'Sections'), ('1', 'Together')], default='0', max_length=1),
        ),
        migrations.AddField(
            model_name='exam',
            name='omitAnswers',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='exam',
            name='omitFigures',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='exam',
            name='omitInstructions',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='exam',
            name='omitMeta',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='exam',
            name='omitPackages',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='exam',
            name='omitQuestionSource',
            field=models.BooleanField(default=False),
        ),
    ]
