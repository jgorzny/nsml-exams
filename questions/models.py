from __future__ import unicode_literals
from datetime import datetime    

from django.db import models
from django.forms import ModelForm
from tagging.forms import TagField

from tagging_autocomplete.models import TagAutocompleteField
from tagging_autocomplete.widgets import TagAutocomplete

# Create your models here.
class Question(models.Model):
    question_text = models.TextField(max_length=200,default='Question source')
    pub_date = models.DateTimeField('date published')
    question_description = models.TextField(max_length=200,default='Description - web/comments only')
    question_instructions = models.TextField(max_length=200,default='Instructions source')
    answer_text = models.TextField(max_length=200,default='Answer source')
    last_edited = models.DateTimeField('date last edited',default=datetime.now)
    num_edits = models.PositiveIntegerField(default=0)
    figure_one = models.FileField(default='',blank=True, null=True)
    figure_two = models.FileField(default='',blank=True, null=True)
    figure_three = models.FileField(default='',blank=True, null=True)
    initial_author = models.CharField(max_length=200,default='None yet')
    contributing_authors = models.CharField(max_length=200,default='None yet')
    question_notes = models.TextField(max_length=200,default='Question notes')
    latex_figure_one = models.TextField(max_length=200,default='e.g. a table')
    latex_figure_two = models.TextField(max_length=200,default='e.g. a table')
    latex_figure_three = models.TextField(max_length=200,default='e.g. a table')
    tags = TagAutocompleteField()
    
class QuestionForm(ModelForm):
    class Meta:
        model = Question
        fields = ['question_text','question_description','question_instructions','question_notes','answer_text',
        'figure_one','figure_two','figure_three','latex_figure_one','latex_figure_two', 'latex_figure_three', 'tags']
        #tags = TagField(widget=TagAutocomplete())