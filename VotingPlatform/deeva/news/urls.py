from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.allNews, name='allNews'),
    url(r'^(?P<news_id>[0-9]+)$', views.oneNews, name='oneNews'),
]
