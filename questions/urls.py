from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<question_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^add/$', views.add, name='add'),
    url(r'^search/$', views.search, name='questions.search'),
    url(r'^search_results/$', views.searchresults, name='questions.searchresults'),
    url(r'^cart/$', views.cart, name='questions.cart'),	
    url(r'^(?P<question_id>[0-9]+)/edit/$', views.edit, name='edit'),	
    url(r'^cart/add/(?P<question_id>[0-9]+)/$', views.store, name='questions.cart.add'),
    url(r'^cart/remove/(?P<question_id>[0-9]+)/$', views.removeFromCart, name='questions.cart.remove'),    
    url(r'^cart/empty/$', views.emptyCart, name='questions.cart.empty'),        
    url(r'^accounts/login/$', auth_views.login, {'template_name': 'admin/login.html'}),
    url(r'^cart/generate/$', views.generateOptions, name='questions.cart.generate'),
    url(r'^cart/generate/make/$', views.makeExam, name='questions.cart.make'),
    url(r'^searchresults_json/$', views.ajax, name='questions.search.json'),
]