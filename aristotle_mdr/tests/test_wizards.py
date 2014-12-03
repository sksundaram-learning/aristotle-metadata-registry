from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse
import aristotle_mdr.models as models
import aristotle_mdr.tests.utils as utils

from django.test.utils import setup_test_environment
setup_test_environment()

class ConceptWizardPage(utils.LoggedInViewPages):
    wizard_name="Harry Potter" # This will break if called without overriding the wizard_name. Plus its funny.
    def setUp(self):
        super(SupersedePage, self).setUp()

    def test_anonymous_cannot_view_create_page(self):
        self.logout()
        response = self.client.get(reverse('aristotle:%s'%self.wizard_name,args=[self.item1.id]))
        self.assertEqual(response.status_code,302)

    def test_viewer_cannot_view_create_page(self):
        self.login_viewer()
        response = self.client.get(reverse('aristotle:%s'%self.wizard_name,args=[self.item1.id]))
        self.assertEqual(response.status_code,302)

    def test_registrar_cannot_view_create_page(self):
        self.login_registrar()
        response = self.client.get(reverse('aristotle:%s'%self.wizard_name,args=[self.item1.id]))
        self.assertEqual(response.status_code,302)

    def test_editor_can_view_create_page(self):
        self.login_editor()
        response = self.client.get(reverse('aristotle:%s'%self.wizard_name,args=[self.item1.id]))
        self.assertEqual(response.status_code,302)

class ObjectClassWizardPage(ConceptWizardPage,TestCase):
    wizard_name="createObjectClass"
class PropertyWizardPage(ConceptWizardPage,TestCase):
    wizard_name="createProperty"
class ValueDomainWizardPage(ConceptWizardPage,TestCase):
    wizard_name="createValueDomain"
class DataElementConceptWizardPage(ConceptWizardPage,TestCase):
    wizard_name="createDataElementConcept"
class DataElementWizardPage(ConceptWizardPage,TestCase):
    wizard_name="createDataElement"
