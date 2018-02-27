#QUESTIONS models
from __future__ import unicode_literals

from django.db import models

""" Questions and Answers """


#A Model containing a question and optionally a more explicit description
class Question(models.Model):
    Question_Choices = [('B', 'boolean'), ('L', 'list'), ('D', 'date'), ('T', 'text'),('C', 'country')]
    title = models.CharField(max_length = 256)
    description = models.TextField()
    qtype = models.CharField(max_length=1, choices=Question_Choices) 

    def __unicode__(self):
        return self.title

#Answer possibilty for list type question
class AnswerPossibility(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.CharField(max_length=64)

    def __unicode__(self):
        return self.answer

#An answer for a question by a user
class Answer(models.Model):
    from django.contrib.auth.models import User
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.TextField()
    answered_on = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.answer




""" Questionsets """

#Group several questions in a set and set if they are required to be answered by the user
class QuestionSet(models.Model):
    name = models.CharField(max_length = 256)
    questions = models.ManyToManyField('Question', through='SetHasQuestion')

    def __unicode__(self):
        return self.name

#Connection model between Set and Questions
class SetHasQuestion(models.Model):
    question_set = models.ForeignKey(QuestionSet, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_required = models.BooleanField()