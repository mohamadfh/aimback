from django.db import models
from authentication.models import CustomUser
from .choices import ANSWER_CHOICES


class Organization(models.Model):
    name = models.CharField(max_length=256 , unique=True)

    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='employee')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    has_submitted = models.BooleanField(default=False)
    def __str__(self):
        return self.user.fullname


class Manager(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='manager')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.fullname


class Block(models.Model):
    title = models.CharField(default="" , max_length=256)
    description = models.CharField(max_length=2048)
    number = models.IntegerField()

    def __str__(self):
        return str(self.number) + " " + self.title

    def save(self, *args, **kwargs):
        # Set the id of the Block object to be equal to its number
        self.id = self.number
        super(Block, self).save(*args, **kwargs)


class Question(models.Model):
    text = models.CharField(max_length=1024)
    block = models.ForeignKey(Block, on_delete=models.CASCADE)

    def __str__(self):
        return self.text


class UserAnswer(models.Model):
    user = models.ForeignKey(Employee, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.IntegerField(default=0, choices=ANSWER_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.answer + " " + self.user.username + " " + self.question.id
