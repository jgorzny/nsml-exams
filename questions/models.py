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
from NSMLEB.fulltext import SearchManager


import os


class Question(models.Model):
    objects    = SearchManager(['question_description'])

    question_text = models.TextField(max_length=2000,default='Question source')
    pub_date = models.DateTimeField('date published')
    question_description = models.TextField(max_length=200,default='Description - web/comments only')
    question_instructions = models.TextField(max_length=2000,default='Instructions source')
    answer_text = models.TextField(max_length=2000,default='Answer source')
    last_edited = models.DateTimeField('date last edited',default=datetime.now)
    num_edits = models.PositiveIntegerField(default=0)
    initial_author = models.CharField(max_length=200,default='None yet')
    contributing_authors = models.CharField(max_length=200,default='None yet')
    question_notes = models.TextField(max_length=200,default='Question notes')
    tags = TagAutocompleteField()
    last_used = models.DateTimeField('date last used',default=datetime.now)
    num_used = models.PositiveIntegerField(default=0)
    is_public = models.BooleanField(default=False)
    
    VEASY = '0'
    EASY = '1'
    MEDIUM = '2'
    HARD = '3'
    VHARD = '4'
    QUESTION_DIFFICULTIES = (
        (VEASY, 'Very Easy'),
        (EASY, 'Easy'),
        (MEDIUM, 'Medium'),
        (HARD, 'Hard'),
        (VHARD, 'Very Hard'),
    )
    difficulty = models.CharField(max_length=1,
                                      choices=QUESTION_DIFFICULTIES ,
                                      default=VEASY)    

    def get_pk(self):
        print ("getting",self.id)
        return u'%s' % (self.pk)
                                      
    def __unicode__(self):
        return u'%s %s' % ("Question",self.pk)
    
    def get_tags(self):
        return Tag.objects.get_for_object(self) 
        
    def get_tags_clean(self):
        tags = Tag.objects.get_for_object(self)
        out = ""
        for t in tags:
            out = out + str(t) + ", "
        return out[:-2]
        
    def get_figures(self):
        return Images.objects.filter(question=self.pk)
        
    def get_figure_names_short(self):
        figures = self.get_figures()
        out = []
        for f in figures:
            out.append(f.get_fig_name_short())
        return out
        
    def get_figure_names(self):
        figures = self.get_figures()
        out = []
        for f in figures:
            out.append(f.get_fig_name())
        return out        

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
        
    def get_difficulty_name(self):
        if self.difficulty == '0':
            return "Very Easy"
        elif self.difficulty == '1':
            return "Easy"
        elif self.difficulty == '2':
            return "Medium"
        elif self.difficulty == '3':
            return "Hard"
        else:
            return "Very Hard"
        
    #TODO: generates broken HTML (first \item generates a </li> that closes nothing)
    def getHTMLQuestionSource(self):
        print "getting HTML source..."
        out = self.question_text.replace("\\begin{itemize}", "<ul>")
        out = out.replace("\\end{itemize}", "</li></ul>")
        out = out.replace("\\item", "</li><li>")
        out = out.replace("<li></li>","")
        out = out.replace("<li></li>","")
        out = out.replace("<li>\n</li>","")        
        print out
        return out
        
    #TODO: generates broken HTML (first \item generates a </li> that closes nothing)        
    def getHTMLAnswerSource(self):
        print "getting HTML source..."
        out = self.answer_text.replace("\\begin{itemize}", "<ul>")
        out = out.replace("\\end{itemize}", "</li></ul>")
        out = out.replace("\\item", "</li><li>")
        out = out.replace("<li> </li>","")
        out = out.replace("<li></li>","")
        out = out.replace("<li>\n</li>","")
        print out
        return out        
        
class Images(models.Model):
    question = models.ForeignKey(Question, default=None)
    image =  models.FileField(default='',blank=True, null=True) 
    num = models.PositiveIntegerField(default=0)
    figure_source = models.TextField(max_length=2000,default='Figure source')
    short_name = models.TextField(max_length=200,default='filename')

    def __unicode__(self):
        return u'%s %s' % ("Image",self.pk)    
    
    def get_fig_name(self):
        print "figure name is:", self.image.name
        return self.image.name

    def get_fig_name_short(self):
        return self.short_name
        
        
class Tables(models.Model):
    question = models.ForeignKey(Question, default=None)
    table = models.TextField(max_length=2000,default='Table source') 
    num = models.PositiveIntegerField(default=0)
    
    def __unicode__(self):
        return u'%s %s' % ("Table",self.pk)     

class Exam(models.Model):
    exam_name = models.TextField(max_length=200,default='Exam name')
    pub_date = models.DateTimeField('date published')
    exam_description = models.TextField(max_length=200,default='Description - web/comments only')
    last_edited = models.DateTimeField('date last edited',default=datetime.now)
    num_edits = models.PositiveIntegerField(default=0)
    exam_author = models.CharField(max_length=200,default='None yet')
    contributing_authors = models.CharField(max_length=200,default='None yet')
    tags = TagAutocompleteField()
    is_public = models.BooleanField(default=False)
    questions = models.CommaSeparatedIntegerField(max_length=200)
    
    omitQuestionSource = models.BooleanField(default=False)
    omitInstructions = models.BooleanField(default=False)
    omitAnswers = models.BooleanField(default=False)
    omitFigures = models.BooleanField(default=False)
    omitMeta = models.BooleanField(default=False)
     
    imagesInFolder = models.BooleanField(default=False)
    figuresInAppendix = models.BooleanField(default=False)
    omitPackages = models.BooleanField(default=False)
    inputFiles = models.BooleanField(default=False)

    SECTIONS = '0'
    TOGETHER = '1'
    EXAM_LAYOUTS = (
        (SECTIONS, 'Sections'),
        (TOGETHER, 'Together'),
    )
    layout = models.CharField(max_length=1,
                                      choices=EXAM_LAYOUTS ,
                                      default=SECTIONS)    
   
class QuestionForm(ModelForm):
    class Meta:
        model = Question
        fields = ['question_text','question_description','question_instructions','question_notes','answer_text', 'tags', 'difficulty', 'is_public']

class QuestionSearch(ModelForm):
    filterResults = forms.BooleanField(required=False, label="Include questions already in your exam", initial=False)
    
    searchVEasyQuestions = forms.BooleanField(required=False, label="Search Very Easy Questions", initial=False)    
    searchEasyQuestions = forms.BooleanField(required=False, label="Search Easy Questions", initial=False)
    searchMedQuestions = forms.BooleanField(required=False, label="Search Medium Questions", initial=False)
    searchHardQuestions = forms.BooleanField(required=False, label="Search Hard Questions", initial=False)
    searchVHardQuestions = forms.BooleanField(required=False, label="Search Very Hard Questions", initial=False)
    
    maxUses = forms.IntegerField(required=False, label="Questions used at most _ times", min_value=0)

    searchText = forms.CharField(widget=forms.Textarea, label="Description search text:")
    class Meta:
        model = Question
        fields=['tags']
        
