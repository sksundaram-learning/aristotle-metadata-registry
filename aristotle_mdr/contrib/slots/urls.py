from django.conf.urls import patterns, url
from aristotle_mdr.contrib.slots import views


urlpatterns = patterns(
    'aristotle_mdr.contrib.slots.views',

    url(r'^slot/(?P<slot_type_id>\d+)/?$', views.SimilarSlotsView.as_view(), name='similar_slots'),
)
