from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<question_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^add/$', views.add, name='add'),
    url(r'^delall/$', views.deleteAllQuestions, name='questions.deleteAll'),    
    url(r'^search/$', views.search, name='questions.search'),
    url(r'^search_results/$', views.searchresults, name='questions.searchresults'),
    url(r'^cart/$', views.cart, name='questions.cart'),	
    url(r'^(?P<question_id>[0-9]+)/edit/$', views.edit, name='edit'),
    url(r'^(?P<question_id>[0-9]+)/render/$', views.renderQuestion, name='questions.render'),
    url(r'^(?P<question_id>[0-9]+)/copy/$', views.copyQuestion, name='questions.copy'),	
    url(r'^(?P<question_id>[0-9]+)/delete/$', views.deleteQuestion, name='questions.deleteQuestion'), 
    url(r'^(?P<question_id>[0-9]+)/removeFromExams/$', views.removeQuestionFromExams, name='questions.exams.removeAll'),
    url(r'^(?P<question_id>[0-9]+)/removeFromExam/(?P<exam_id>[0-9]+)/$', views.removeQuestionFromOneExam, name='questions.exams.removeOne'),    
    url(r'^(?P<question_id>[0-9]+)/exams/$', views.viewExamsContainingQuestion, name='questions.exams.show'),        
    url(r'^cart/add/(?P<question_id>[0-9]+)/$', views.store, name='questions.cart.add'),
    url(r'^cart/remove/(?P<question_id>[0-9]+)/$', views.removeFromCart, name='questions.cart.remove'),    
    url(r'^cart/empty/$', views.emptyCart, name='questions.cart.empty'),        
    url(r'^accounts/login/$', auth_views.login, {'template_name': 'admin/login.html'}),
    url(r'^cart/generate/options/$', views.generateCartOptions, name='questions.cart.options'), 
    url(r'^cart/generate/$', views.generateOptions, name='questions.cart.generate'),
    url(r'^(?P<question_id>[0-9]+)/edit/fig/(?P<figure_num>[0-9]+)/$', views.downloadFigure, name='questions.edit.downloadFigure'),
    url(r'^cart/generate/make/$', views.makeExam, name='questions.cart.make'),
    url(r'^searchresults_json/$', views.ajax, name='questions.search.json'), 
    url(r'^tags/(?P<tag_id>[0-9]+)/$', views.tagDetail, name='tag.detail'),    
    url(r'^tags/$', views.tagList, name='tag.list'),  
    url(r'^tags/(?P<tag_id>[0-9]+)/edit/$', views.tagRename, name='tag.rename'),    
    url(r'^tags/(?P<tag_id>[0-9]+)/del/$', views.tagDelete, name='tag.del'),       

]