from django.core.urlresolvers import reverse
from django.test import TestCase

#import aristotle_mdr.models as models
#import aristotle_mdr.perms as perms
import aristotle_mdr.tests.utils as utils

from django.test.utils import setup_test_environment
setup_test_environment()

class GlossaryPage(utils.LoggedInViewPages,TestCase):
    def test_logged_out_glossary_page(self):
        self.logout()
        response = self.client.get(reverse('aristotle:glossary',))
        self.assertEqual(response.status_code,200)
        for term in response.context['terms']:
            self.assertTrue(term.is_public)
