from django.test import TestCase

import aristotle_mdr.models as models
import aristotle_mdr.perms as perms
import aristotle_mdr.tests.utils as utils
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.template import TemplateDoesNotExist
from aristotle_mdr.tests.utils import ManagedObjectVisibility
from aristotle_mdr.tests.test_html_pages import LoggedInViewConceptPages
from aristotle_mdr.tests.test_admin_pages import AdminPageForConcept

from django.test.utils import setup_test_environment
setup_test_environment()

from extension_test.models import Question, Questionnaire

class TestExtensionListVisibility(TestCase):
    def test_extension_list_page(self):
        from django.test import Client
        from django.apps import apps
        client = Client()
        response = client.get(reverse('aristotle_mdr:extensions'))
        self.assertEqual(response.status_code,200)
        ext = apps.get_app_config('extension_test')
        download = apps.get_app_config('text_download_test')
        self.assertTrue(download.verbose_name in response.content)
        self.assertTrue('text_download_test' in response.context['download_extensions'].keys())
        self.assertTrue(ext.verbose_name in response.content)
        self.assertTrue(ext in response.context['content_extensions'])

class QuestionVisibility(TestCase,ManagedObjectVisibility):
    def setUp(self):
        self.wg = models.Workgroup.objects.create(name="Setup WG")
        self.item = Question.objects.create(name="Test Question",
            workgroup=self.wg,
            )

class QuestionAdmin(AdminPageForConcept,TestCase):
    itemType=Question

class LoggedInViewExtensionConceptPages(LoggedInViewConceptPages):
    def get_help_page(self):
        return reverse('extension_test:about',args=[self.item1._meta.model_name])

class QuestionViewPage(LoggedInViewExtensionConceptPages,TestCase):
    url_name='question'
    itemType=Question
    def test_help_page_exists(self):
        self.logout()
        response = self.client.get(self.get_help_page())
        self.assertEqual(response.status_code,200)

class QuestionnaireVisibility(TestCase,ManagedObjectVisibility):
    def setUp(self):
        self.wg = models.Workgroup.objects.create(name="Setup WG")
        self.item = Questionnaire.objects.create(name="Test Question",
            workgroup=self.wg,
            )

class QuestionnaireAdmin(AdminPageForConcept,TestCase):
    itemType=Questionnaire

class QuestionnaireViewPage(LoggedInViewExtensionConceptPages,TestCase):
    url_name='item' #'questionnaire' # the lazy way
    itemType=Questionnaire
    def test_help_page_exists(self):
        self.logout()

        with self.assertRaises(TemplateDoesNotExist):
            response = self.client.get(self.get_help_page())# They never made this help page, this will error

