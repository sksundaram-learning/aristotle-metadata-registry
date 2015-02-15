import autocomplete_light
autocomplete_light.autodiscover()

from django.conf.urls import patterns, url

from extension_test import views

urlpatterns = patterns('',
    url(r'^about/(?P<template>.+)/?$', views.DynamicTemplateView.as_view(), name="about"),
)