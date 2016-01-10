from django.conf.urls import patterns, include, url


urlpatterns = patterns(
    '',
    url(r'^', include('aristotle_mdr.urls')),
    url(r'^extension_test/', include('extension_test.extension_urls', app_name="extension_test", namespace="extension_test")),
)
