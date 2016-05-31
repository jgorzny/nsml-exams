from __future__ import unicode_literals
from datetime import datetime    

from django.db import models
from django.forms import ModelForm
from tagging.forms import TagField

from tagging_autocomplete.models import TagAutocompleteField
from tagging_autocomplete.widgets import TagAutocomplete
from tagging.models import Tag
from tagging.registry import register
from django import forms

import os



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
    last_used = models.DateTimeField('date last used',default=datetime.now)
    num_used = models.PositiveIntegerField(default=0)


    
    def get_tags(self):
        return Tag.objects.get_for_object(self) 
        
    def get_figures(self):
        return Images.objects.filter(question=self.pk)

    def get_tables(self):
        return Tables.objects.filter(question=self.pk)        
    
    def get_num_tables(self):
        tableSet = Tables.objects.filter(question=self.pk)
        return tableSet.count()
        
    def get_new_table_num(self):
        tableSet = Tables.objects.filter(question=self.pk)
        return tableSet.count() + 1
    
    def get_new_figure_num(self):
        figureSet = Images.objects.filter(question=self.pk)
        return figureSet.count() + 1
        
class Images(models.Model):
    question = models.ForeignKey(Question, default=None)
    image =  models.FileField(default='',blank=True, null=True) 
    num = models.PositiveIntegerField(default=0)
    
    def get_fig_name(self):
        print "figure name is:", self.image.name
        return os.path.basename(self.image.name)

class Tables(models.Model):
    question = models.ForeignKey(Question, default=None)
    table = models.TextField(max_length=200,default='Table source') 
    num = models.PositiveIntegerField(default=0)
    
class QuestionForm(ModelForm):
    class Meta:
        model = Question
        fields = ['question_text','question_description','question_instructions','question_notes','answer_text',
        'figure_one','figure_two','figure_three','latex_figure_one','latex_figure_two', 'latex_figure_three', 'tags']

class QuestionSearch(ModelForm):
    filterResults = forms.BooleanField(required=False, label="Include questions already in your exam", initial=False)

    class Meta:
        model = Question
        fields=['tags']
        
