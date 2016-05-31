from django.contrib import admin

from .models import Question, Images, Tables

admin.site.register(Question)
admin.site.register(Images)
admin.site.register(Tables)