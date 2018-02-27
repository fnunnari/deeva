from django.conf.urls import url

from . import views, views_admin

app_name = 'experiments'

urlpatterns = [
    url(r'^experiments/all', views.allExperiments, name='allExperiments'),
    url(r'^experiments/(?P<wizard_id>[0-9]+)$', views.oneExperiment, name='oneExperiment'),
    url(r'^vote/(?P<wizard_id>[0-9]+)$', views.vote, name='vote'),

    url(r'^$', views.index, name='index'),
]