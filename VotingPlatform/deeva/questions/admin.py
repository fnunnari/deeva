from django.contrib import admin

from .models import Question, Answer, QuestionSet, SetHasQuestion

# Register your models here.

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    #list
    list_display = ('internal_name', 'title', 'qtype',)
    list_display_links = ('internal_name',)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    #list
    list_display = ('user', 'question', 'answer', 'answered_on')
    list_display_links = ('user', 'question', 'answer',)


class SetHasQuestionInline(admin.TabularInline):
    model = SetHasQuestion
    extra = 0

@admin.register(QuestionSet)
class QuestionSetAdmin(admin.ModelAdmin):
    #list
    list_display = ('name', 'questions_list',)
    list_display_links = ('name',)

    #page
    inlines = (SetHasQuestionInline,)
