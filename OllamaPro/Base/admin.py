from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Document)
admin.site.register(LoadedFile)
admin.site.register(QuestionHistory)
admin.site.register(ChatInstance)