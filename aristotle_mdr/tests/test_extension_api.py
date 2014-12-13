from django.test import TestCase

import aristotle_mdr.models as models
import aristotle_mdr.perms as perms
import aristotle_mdr.tests.utils as utils
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from aristotle_mdr.tests.utils import ManagedObjectVisibility
from aristotle_mdr.tests.test_everything import LoggedInViewConceptPages

from django.test.utils import setup_test_environment
setup_test_environment()

from extension_test.models import Question

class QuestionVisibility(TestCase,ManagedObjectVisibility):
    def setUp(self):
        self.wg = models.Workgroup.objects.create(name="Setup WG")
        self.item = Question.objects.create(name="Test Question",
            workgroup=self.wg,
            )

class QuestionViewPage(LoggedInViewConceptPages,TestCase):
    url_name='question'
    itemType=Question
    def get_page(self,item):
        return reverse('extension_test:%s'%self.item1.url_name,args=[item.id])
    def get_help_page(self):
        return reverse('extension_test:%s'%self.item1.url_name)
    def test_help_page_exists(self):
        self.logout()
        response = self.client.get(self.get_help_page())
        self.assertRedirects(response,reverse("extension_test:about",args=[self.item1.help_name])) # This should redirect
