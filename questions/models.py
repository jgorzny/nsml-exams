from __future__ import unicode_literals

from django.db import models
from django.forms import ModelForm

# Create your models here.
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
	
class QuestionForm(ModelForm):
    class Meta:
        model = Question
        fields = ['question_text']