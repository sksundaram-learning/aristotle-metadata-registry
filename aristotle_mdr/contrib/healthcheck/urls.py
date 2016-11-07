from django.conf.urls import patterns, url
from aristotle_mdr.contrib.healthcheck import views


urlpatterns = patterns(
    'aristotle_mdr.contrib.slots.views',
    url(r'^healthz/?$', views.heartbeat, name='health'),
)
