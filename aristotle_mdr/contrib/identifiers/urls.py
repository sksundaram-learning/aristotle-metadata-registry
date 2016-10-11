from django.conf.urls import patterns, url
from aristotle_mdr.contrib.identifiers.views import scoped_identifier_redirect


urlpatterns = patterns(
    'aristotle_mdr.contrib.identifier.views',

    url(r'^identifier/(?P<ns_prefix>.+)/(?P<iid>.+)/?$', scoped_identifier_redirect, name='scoped_identifier_redirect'),
)
