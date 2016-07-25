from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.recentExams, name='exams.recentExams'),
    url(r'^search/$', views.searchExams, name='exams.search'),
    url(r'^(?P<exam_id>[0-9]+)/$', views.viewExam, name='exams.viewExam'),         
    url(r'^delall/$', views.deleteAll, name='exams.deleteAll'),     
]