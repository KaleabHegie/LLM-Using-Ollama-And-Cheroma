from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Document(models.Model):
    file = models.FileField()

class LoadedFile(models.Model):
    number = models.IntegerField(default=0)


class ChatInstance(models.Model):
    user = models.ForeignKey(User, null=True, blank=True ,on_delete=models.SET_NULL)
    title = models.CharField(null=True, blank=True, max_length=100)
    created_at = models.DateTimeField(auto_now=True, auto_now_add=False)

class QuestionHistory(models.Model):
    question = models.CharField(max_length=500)
    response = models.TextField(null=True , blank=True)
    instance = models.ForeignKey(ChatInstance, null=True, blank=True, on_delete=models.SET_NULL)