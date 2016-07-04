from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings, modify_settings
from django.test.utils import setup_test_environment

from django.core.management import call_command
from aristotle_mdr.contrib.help import models

setup_test_environment()


class TestHelpPagesLoad(TestCase):
    def test_help_pages_load_into_db(self):
        count_hp_1 = models.HelpPage.objects.all().count()
        count_cp_1 = models.ConceptHelp.objects.all().count()

        call_command('load_aristotle_help')

        count_hp_2 = models.HelpPage.objects.all().count()
        count_cp_2 = models.ConceptHelp.objects.all().count()
        self.assertTrue(count_hp_2 > count_hp_1)
        self.assertTrue(count_cp_2 > count_cp_1)

    def test_help_pages_load(self):
        call_command('load_aristotle_help')
        regular_help = models.HelpPage.objects.all()
        concept_help = models.ConceptHelp.objects.all()

        response = self.client.get(reverse('aristotle_help:help_base'))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('aristotle_help:help_concepts'))
        self.assertEqual(response.status_code, 200)

        for app_label in getattr(settings, 'ARISTOTLE_SETTINGS')['CONTENT_EXTENSIONS']:
            response = self.client.get(reverse('aristotle_help:concept_app_help', args=[app_label]))
            self.assertEqual(response.status_code, 200)

        for obj in concept_help:
            response = self.client.get(reverse('aristotle_help:concept_help', args=[obj.app_label, obj.concept_type]))
            self.assertEqual(response.status_code, 200)

        for obj in concept_help:
            response = self.client.get(reverse('aristotle_help:concept_help', args=[obj.app_label, obj.concept_type]))
            self.assertEqual(response.status_code, 200)

        for obj in regular_help:
            response = self.client.get(reverse('aristotle_help:help_page', args=[obj.slug]))
            self.assertEqual(response.status_code, 200)

    def test_bad_help_template_tags(self):
        from aristotle_mdr.contrib.help.templatetags import aristotle_help as tags

        page = models.HelpPage()

        rendered = tags.relink(page, 'body')
        self.assertTrue(rendered == "")

        page = models.HelpPage(
            body="[[some_page]]"
        )

        rendered = tags.relink(page, 'body')
        self.assertTrue('unknown model' in rendered)

    def test_good_help_template_tags(self):
        from aristotle_mdr.contrib.help.templatetags import aristotle_help as tags

        page = models.HelpPage(
            body="[[aristotle_mdr.Property|s]]"
        )

        rendered = tags.relink(page, 'body')
        self.assertTrue('Properties' in rendered)
