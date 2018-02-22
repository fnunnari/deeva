from django.contrib import admin
from .models import News

# Register your models here.

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    fieldsets = ((None, { 'fields': ('title', 'text', 'date', 'keep_on_homepage', 'hide', 'share_news')}),) 

    readonly_fields = ('share_news',) 

    list_display = ('title', 'text_short', 'date', 'keep_on_homepage', 'hide')
    list_filter = ('date', 'keep_on_homepage')




