from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Document(models.Model):
    file = models.FileField()

class LoadedFile(models.Model):
    number = models.IntegerField(default=0)


class QuestionHistory(models.Model):
    question = models.CharField(max_length=500)
    response = models.TextField(null=True , blank=True)
    user = models.ForeignKey(User , on_delete=models.CASCADE)