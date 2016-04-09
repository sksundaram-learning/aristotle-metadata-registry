from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings, modify_settings
from django.test.utils import setup_test_environment

from django.core.management import call_command
from aristotle_mdr.contrib.help import models

setup_test_environment()


class TestHelpPagesLoad(TestCase):
    def test_help_pages_load(self):
        count_1 = models.HelpPage.objects.all().count()
        call_command('loadhelp', 'aristotle_help/*')
        count_2 = models.HelpPage.objects.all().count()
        self.assertTrue(count_2 > count_1)

    def test_concept_help_pages_load(self):
        count_1 = models.ConceptHelp.objects.all().count()
        call_command('loadhelp', 'aristotle_help/concept_help/*')
        count_2 = models.ConceptHelp.objects.all().count()
        self.assertTrue(count_2 > count_1)
