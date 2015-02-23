import aristotle_mdr.api as api
from tastypie.api import Api

import notifications
import autocomplete_light
# import every app/autocomplete_light_registry.py
autocomplete_light.autodiscover()

from django.conf.urls import patterns, include, url
from django.contrib.auth.views import password_reset
from django.contrib import admin
admin.autodiscover()

v1_api = Api(api_name='v1')
v1_api.register(api.GlossaryListResource())


urlpatterns = patterns('',
    # Examples:
    url(r'^login/?$', 'django.contrib.auth.views.login'),
    url(r'^logout/?$', 'django.contrib.auth.views.logout',
        {'next_page': '/'}),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^autocomplete/', include('autocomplete_light.urls')),
    url(r'^grappelli/', include('grappelli.urls')), # grappelli URLS
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^ckeditor/', include('ckeditor.urls')),
    url(r'^inplaceeditform/', include('inplaceeditform.urls')),
    url(r'^account/notifications/', include(notifications.urls)),
    url(r'^api/', include(v1_api.urls)),
    url(r'^account/password/reset/$', password_reset), #, {'template_name': 'my_templates/password_reset.html'}
    url(r'^account/password/reset_done/$', password_reset), #, {'template_name': 'my_templates/password_reset.html'}
    url(r'^', include('aristotle_mdr.urls_aristotle',app_name="aristotle_mdr",namespace="aristotle")),

    url(r'^user/password/reset/$',
        'django.contrib.auth.views.password_reset',
        {'post_reset_redirect' : '/user/password/reset/done/'},
        name="password_reset"),
    url(r'^user/password/reset/done/$',
        'django.contrib.auth.views.password_reset_done',
        name="password_reset_done"
        ),
    (r'^user/password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        'django.contrib.auth.views.password_reset_confirm',
        {'post_reset_redirect' : '/user/password/done/'}),
    (r'^user/password/done/$',
        'django.contrib.auth.views.password_reset_complete'),

    )

handler403 = 'aristotle_mdr.views.unauthorised'