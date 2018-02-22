from django.shortcuts import render
from .models import News

# Create your views here.

def allNews(request):
    """all news view"""
    from .functions import getNews
    newss = getNews()
    return render(request, 'news/allnews.html', {'newss':newss})

def oneNews(request, news_id):
    """one specific news view"""
    from .functions import getOneNews
    try:
        news = getOneNews(news_id)
    except News.DoesNotExist as e:
        from django.contrib import messages
        messages.error(request, "Sorry. The requested news was not found.")
        return allNews(request)
    
    return render(request, 'news/onenews.html', {'news':news})

