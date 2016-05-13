from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings, modify_settings
from django.test.utils import setup_test_environment

from django.core.management import call_command
from aristotle_mdr.contrib.help import models
from aristotle_mdr.tests.apps.extension_test.models import Question, Questionnaire
from aristotle_mdr.tests import utils
from aristotle_mdr.models import Workgroup

setup_test_environment()


class TestGenericPagesLoad(utils.LoggedInViewPages, TestCase):

    def test_anon_cant_use_generic(self):
        wg = Workgroup.objects.create(name="Setup WG")
        q = Questionnaire.objects.create(name='test questionnaire', workgroup=wg)
        url = reverse('questionnaire_add_question', kwargs={'iid': q.id})
        response = self.client.get(url)
        self.assertRedirects(response, reverse('friendly_login') + "?next=" + url)
