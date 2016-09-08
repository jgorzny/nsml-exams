from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.recentExams, name='exams.recentExams'),
    url(r'^search/$', views.searchExams, name='exams.search'),
    url(r'^templates/$', views.examTemplates, name='exams.templates'),  
    url(r'^templates/add/$', views.examAddTemplate, name='exams.addTemplate'),        
    url(r'^templates/(?P<templateid>[0-9]+)/edit/$', views.examEditTemplate, name='exams.editTemplate'),  
    url(r'^templates/(?P<templateid>[0-9]+)/view/$', views.examViewTemplate, name='exams.ViewTemplate'),        
    url(r'^templates/(?P<templateid>[0-9]+)/delete/$', views.examDelTemplate, name='exams.delTemplate'),        
    url(r'^search_results/$', views.examSearchResults, name='exams.searchResults'),    
    url(r'^(?P<exam_id>[0-9]+)/$', views.viewExam, name='exams.viewExam'),         
    url(r'^delall/$', views.deleteAll, name='exams.deleteAll'), 
    url(r'^delempty/$', views.deleteEmpty, name='exams.deleteEmpty'), 
    url(r'^delallempty/$', views.deleteAllEmpty, name='exams.deleteAllEmpty'),         
    url(r'^(?P<exam_id>[0-9]+)/delete/$', views.deleteExam, name='exams.deleteExam'),
    url(r'^(?P<exam_id>[0-9]+)/edit/$', views.editExam, name='exams.editExam'),
    url(r'^(?P<exam_id>[0-9]+)/update/$', views.updateExam, name='exams.update'),        
    url(r'^(?P<exam_id>[0-9]+)/download/$', views.downloadExam, name='exams.downloadExam'),        
    

]