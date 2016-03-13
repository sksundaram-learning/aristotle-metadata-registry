from django.conf.urls import patterns, url
from aristotle_mdr.contrib.help import views


urlpatterns = patterns(
    'aristotle_mdr.contrib.help.views',

    url(r'^concepts/(?P<app>[a-zA-Z_]+)/(?P<model>[a-zA-Z_]+)/?', views.ConceptHelpView.as_view(), name='concept_help'),
    # url(r'^concepts/(?P<app>[a-zA-Z_]+)/?', views.AppHelpView.as_view(), name='app_help'),
)
