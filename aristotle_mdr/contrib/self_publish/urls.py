from django.conf.urls import patterns, url
from aristotle_mdr.contrib.self_publish import views


urlpatterns = patterns(
    'aristotle_mdr.contrib.self_publish.views',

    url(r'^item/(?P<iid>\d+)/?$', views.PublishMetadataFormView.as_view(), name='publish_metadata'),
)
