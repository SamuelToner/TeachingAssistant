from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title


class QuestionAnswer(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField()


class Result(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.TextField()
    student_answer = models.TextField()
    result = models.CharField(max_length=10)
