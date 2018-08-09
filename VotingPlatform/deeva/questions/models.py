#QUESTIONS models
from __future__ import unicode_literals

from django.db import models

""" Questions and Answers """


#A Model containing a question and optionally a more explicit description
class Question(models.Model):
    Question_Choices = [('B', 'boolean'), ('L', 'list'), ('D', 'date'), ('T', 'text'), ('C', 'country')]
    
    internal_name = models.CharField(unique=True, max_length=64, help_text="A short internal name to easily select questions.") 
    title = models.TextField(help_text="The question to be asked.")
    help_text = models.TextField(null=True, blank=True, help_text="An optional help text, to clear up what is expected from the user.")
    qtype = models.CharField(max_length=1, choices=Question_Choices, help_text="Boolean: will be rendered as 'Yes/No'. List displays a drop-down menu. Text is a free-text answer.") 
    answer_possibilities = models.TextField(null=True, blank=True, help_text="If this is a list question, write down the answer possibilities to be displayed in that list seperated by a semicolon (;).")

    #answer_possibilities as a python list
    def answer_possibilities_list(self):
        return [x.strip() for x in self.answer_possibilities.split(';')]

    #get rid of whitespace for consistent look
    def save(self, *args, **kwargs):
        self.answer_possibilities = "; ".join(self.answer_possibilities_list()) 
        super().save(*args, **kwargs) 

    def clean(self):
        from django.core.exceptions import ValidationError
        print('len', len(self.answer_possibilities_list()))
        print('content', self.answer_possibilities_list())
        if (self.qtype == 'L') and ('' in self.answer_possibilities_list()):
            raise ValidationError("If the question type is list, the answer possibilties cannot contain an empty string.")
        if len(self.answer_possibilities_list()) > 0:
            if not len(self.answer_possibilities_list()) == len(set(self.answer_possibilities_list())):
                raise ValidationError("Having duplicates in answer possibilities is not allowed.")

    def __str__(self):
        return self.internal_name


#An answer for a question by a user
class Answer(models.Model):
    from django.contrib.auth.models import User
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.TextField()
    answered_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} + {} = {}".format(self.user, self.question, self.answer)




""" Questionsets """

#Group several questions in a set and set if they are required to be answered by the user
class QuestionSet(models.Model):
    name = models.CharField(unique=True, max_length = 255)
    questions = models.ManyToManyField('Question', through='SetHasQuestion')

    def questions_list(self):
        return list(self.questions.all().values_list('internal_name', flat=True))

    def __str__(self):
        return self.name

#Connection model between Set and Questions
class SetHasQuestion(models.Model):
    question_set = models.ForeignKey(QuestionSet, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_required = models.BooleanField()