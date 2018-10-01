from django.conf.urls import url

from . import views, views_admin

app_name = 'experiments'

urlpatterns = [
    url(r'^experiments/all', views.allExperiments, name='allExperiments'),
    url(r'^experiments/(?P<wizard_id>[0-9]+)$', views.oneExperiment, name='oneExperiment'),

    url(r'^wiz/(?P<wizard_id>[0-9]+)/vote$', views.vote, name='vote'),
    url(r'^wiz/(?P<wizard_id>[0-9]+)/vote_after_break_$', views.vote, {'had_break': True}, name='vote_after_break'),

    
    url(r'^wiz/(?P<wizard_id>[0-9]+)/break$', views.wizard_break, name='wizard_break'),
    
    url(r'^wiz/(?P<wizard_id>[0-9]+)/comp_vote$', views.comp_vote, name='comp_vote'),
    url(r'^wiz/(?P<wizard_id>[0-9]+)/rate_vote$', views.rate_vote, name='rate_vote'),


    url(r'wiz/(?P<wizard_id>\w+)/end', views.wizard_exit, name='wizard_exit'),
    url(r'wiz/(?P<wizard_id>\w+)/infos', views.wizard_personalinfos, name='wizard_personalinfos'),
    # url(r'wiz/(?P<wizard_id>\w+)/vote', views.wizard_vote, name='wizard_vote'),
    url(r'wiz/(?P<wizard_id>\w+)/example', views.wizard_example, name='wizard_example'),
    url(r'wiz/(?P<wizard_id>\w+)/disclaimer', views.wizard_disclaimer,
        name='wizard_disclaimer'),
    url(r'wiz/(?P<wizard_id>\w+)/welcome', views.wizard_welcome, name='wizard_welcome'),
    url(r'wiz/(?P<wizard_id>\w+)/checkuser', views.wizard_checkuser, name='wizard_checkuser'),
    url(r'wiz/(?P<wizard_id>\w+)', views.wizard_start, name='wizard_start'),

    url(r'^individuals/content/(?P<individual_id>[0-9]+)/(?P<content_name>[\w.]+)$', views.send_individual_content, name='send_individual_content'),

    url(r'^$', views.index, name='index'),
]
