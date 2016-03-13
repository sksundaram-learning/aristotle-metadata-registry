from django.conf.urls import patterns, include, url


urlpatterns = patterns(
    '',
    url(r'^browse/', include('aristotle_mdr.contrib.browse.urls')),
    url(r'^help/', include('aristotle_mdr.contrib.help.urls')),
    url(r'^', include('aristotle_mdr.urls')),
)
