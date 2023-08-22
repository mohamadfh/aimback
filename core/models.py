from django.db import models
from authentication.models import CustomUser
from .choices import ANSWER_CHOICES


class Organization(models.Model):
    name = models.CharField(max_length=256)


class Employee(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.fullname


class Manager(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.fullname


class Question(models.Model):
    text = models.CharField(max_length=255)
    block = models.IntegerField(default=1)

    def __str__(self):
        return self.text


class UserAnswer(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.IntegerField(default=0, choices=ANSWER_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
