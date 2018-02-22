from django.conf.urls import url

from . import views, views_admin

urlpatterns = [
    url(r'^experiments/experiment/(?P<variable_set_id>[0-9]+)/variables_header_download$',
        views_admin.download_variables_header, name='variables_header'),

    url(r'^experiments/generation/(?P<generation_id>[0-9]+)/import_individuals$',
        views_admin.upload_individuals, name='upload_individuals'),   
    url(r'^experiments/generation/(?P<generation_id>[0-9]+)/import_individuals/status/(?P<task_id>\w+)/progress$',
        views_admin.upload_individuals_status_progress, name='upload_individuals_status_progress'), 
    url(r'^experiments/generation/(?P<generation_id>[0-9]+)/import_individuals/status/(?P<task_id>\w+)$',
        views_admin.upload_individuals_status, name='upload_individuals_status'),   

    url(r'^experiments/variable/import_variables$',
        views_admin.import_variables, name='import_variables'),   
]
    