from django.conf.urls import patterns, include, url
from aristotle_mdr.contrib.generic.views import GenericAlterManyToManyView
from aristotle_mdr.tests.apps.extension_test.models import Question, Questionnaire


urlpatterns = patterns(
    '',
    url(r'^', include('aristotle_mdr.urls')),
    url(r'^extension_test/', include('extension_test.extension_urls', app_name="extension_test", namespace="extension_test")),
    url(r'^questionnaire/(?P<iid>\d+)/add_question/?$',
        GenericAlterManyToManyView.as_view(
            model_base = Questionnaire,
            model_to_add = Question,
            model_base_field = 'questions'
        ), name='questionnaire_add_question'),
)
