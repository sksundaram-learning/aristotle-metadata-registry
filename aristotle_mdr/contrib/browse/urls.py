from django.conf.urls import patterns, url

from aristotle_mdr.contrib.browse import views

urlpatterns = patterns(
    'aristotle_mdr.contrib.browse.views',

    url(r'^(?P<app>[a-zA-Z_]+)/(?P<model>[a-zA-Z_]+)/?', views.BrowseConcepts.as_view(), name='browse_concepts'),
    url(r'^(?P<app>[a-zA-Z_]+)/?', views.BrowseModels.as_view(), name='browse_models'),
    url(r'^/?$', views.BrowseApps.as_view(), name='browse_apps'),
)
