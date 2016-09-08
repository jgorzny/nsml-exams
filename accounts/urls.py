from django.conf.urls import patterns, url
from django.contrib.auth import views

urlpatterns = [
    url(
        r'^login/$',
        views.login,
        name='login',
        kwargs={'template_name': 'accounts/login.html'}
    ),
    url(
        r'^logout/$',
        views.logout,
        name='logout',
        kwargs={'next_page': '/'}
    ),
    url(
        r'^password_change/$',
        views.password_change,
        name='password_change',
        kwargs={
               'template_name': 'accounts/password_change_form.html',
               'post_change_redirect':'accounts:password_change_done',
               }
    ),
    url(
        r'^password_change_done/$',
        views.password_change_done,
        name='password_change_done',
        kwargs={'template_name': 'accounts/password_change_done.html'}
    ),	
    
]