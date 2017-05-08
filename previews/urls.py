from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^previewcode$', views.previewCodeView, name='previews.previewView'),
    url(r'^previewcode/clear$', views.previewCodeClear, name='previews.delpreview'),
    url(r'^previewcode/edit$', views.previewCodeEdit, name='previews.editpreview'),
    url(r'^previewcode/update', views.previewUpdate, name='previews.update'),
    
]