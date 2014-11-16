import autocomplete_light
autocomplete_light.autodiscover()

from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from extension_test import views

urlpatterns = patterns('extension_test.views',
    url(r'^question/(?P<iid>\d+)/?$', views.question, name='Question'),

#These are required for about pages to work. Include them, or custom items will die!
#    url(r'^about/(?P<template>.+)/?$', views.DynamicTemplateView.as_view(), name="about"),
#    url(r'^about/?$', TemplateView.as_view(template_name='aristotle_dse/static/about_aristotle_dse.html'), name="about"),
)