from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse
import aristotle_mdr.models as models
import aristotle_mdr.tests.utils as utils
from django.core.management import call_command

from django.test.utils import setup_test_environment
setup_test_environment()

class ConceptWizardPage(utils.LoggedInViewPages):
    wizard_url_name="Harry Potter" # This will break if called without overriding the wizard_url_name. Plus its funny.
    def tearDown(self):
        call_command('clear_index', interactive=False, verbosity=0)

    def setUp(self):
        super(ConceptWizardPage, self).setUp()
        import haystack
        haystack.connections.reload('default')

    @property
    def wizard_url(self):
        return reverse('aristotle:%s'%self.wizard_url_name)

    def test_anonymous_cannot_view_create_page(self):
        self.logout()
        response = self.client.get(self.wizard_url)
        self.assertEqual(response.status_code,302)

    def test_viewer_cannot_view_create_page(self):
        self.login_viewer()
        response = self.client.get(self.wizard_url)
        self.assertEqual(response.status_code,302)

    def test_registrar_cannot_view_create_page(self):
        self.login_registrar()
        response = self.client.get(self.wizard_url)
        self.assertEqual(response.status_code,302)

    def test_editor_can_view_create_page(self):
        self.login_editor()
        response = self.client.get(self.wizard_url)
        self.assertEqual(response.status_code,200)

    def test_editor_can_make_object(self):
        self.login_editor()
        step_1_data = {
            self.wizard_form_name+'-current_step': 'initial',
        }

        response = self.client.post(self.wizard_url, step_1_data)
        wizard = response.context['wizard']
        self.assertEqual(wizard['steps'].current, 'initial')
        self.assertTrue('name' in response.context['wizard']['form'].errors.keys())

        # must submit a name
        step_1_data.update({'initial-name':"Test Item"})
        # success!

        response = self.client.post(self.wizard_url, step_1_data)
        wizard = response.context['wizard']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(wizard['steps'].current, 'results')

        step_2_data = {
            self.wizard_form_name+'-current_step': 'results',
            'results-name':"Test Item",
        }

        response = self.client.post(self.wizard_url, step_2_data)
        wizard = response.context['wizard']
        self.assertTrue('description' in response.context['wizard']['form'].errors.keys())
        self.assertTrue('workgroup' in response.context['wizard']['form'].errors.keys())

        # no "test item" yet.
        self.assertFalse(models._concept.objects.filter(name="Test Item").exists())

        # must submit a description at this step. But we are using a non-permitted workgroup.
        step_2_data.update({
            'results-description':"Test Description",
            'results-workgroup':self.wg2.pk
            })
        response = self.client.post(self.wizard_url, step_2_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('workgroup' in response.context['wizard']['form'].errors.keys())

        # must submit a description at this step. With the right workgroup
        step_2_data.update({
            'results-description':"Test Description",
            'results-workgroup':self.wg1.pk
            })
        response = self.client.post(self.wizard_url, step_2_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(models._concept.objects.filter(name="Test Item").exists())
        self.assertEqual(models._concept.objects.filter(name="Test Item").count(),1)
        item = models._concept.objects.filter(name="Test Item").first()
        self.assertRedirects(response,reverse("aristotle:item", args=[item.id]))

class ObjectClassWizardPage(ConceptWizardPage,TestCase):
    wizard_url_name="createObjectClass"
    wizard_form_name="object_class_wizard"
class PropertyWizardPage(ConceptWizardPage,TestCase):
    wizard_url_name="createProperty"
    wizard_form_name="property_wizard"
class ValueDomainWizardPage(ConceptWizardPage,TestCase):
    wizard_url_name="createValueDomain"
    wizard_form_name="value_domain_wizard"

class DataElementWizardPage(ConceptWizardPage,TestCase):
    wizard_url_name="createDataElement"
    wizard_form_name="data_element_wizard"

class DataElementConceptWizardPage(ConceptWizardPage,TestCase):
    wizard_url_name="createDataElementConcept"
    wizard_form_name="data_element_concept_wizard"
    def test_editor_can_make_object(self):
        pass
    def test_editor_can_make_object__has_prior_components(self):
        self.login_editor()
        ani = models.ObjectClass.objects.create(name="Animagus",description="",workgroup=self.wg1)
        at  = models.Property.objects.create(name="Animal type",description="",workgroup=self.wg1)

        step_1_data = {
            self.wizard_form_name+'-current_step': 'oc_p_search',
            'oc_p_search-oc_name':"Animagus",
            'oc_p_search-pr_name':"Animal type"
        }
        # success!

        response = self.client.post(self.wizard_url, step_1_data)
        wizard = response.context['wizard']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(wizard['steps'].current, 'oc_p_results')


    def test_editor_can_make_object__no_prior_components(self):
        self.login_editor()
        step_1_data = {
            self.wizard_form_name+'-current_step': 'oc_p_search',
        }

        response = self.client.post(self.wizard_url, step_1_data)
        wizard = response.context['wizard']
        self.assertEqual(wizard['steps'].current, 'oc_p_search')
        self.assertTrue('oc_name' in response.context['wizard']['form'].errors.keys())
        self.assertTrue('pr_name' in response.context['wizard']['form'].errors.keys())

        # must submit a name
        step_1_data.update({'oc_p_search-oc_name':"Animagus"})
        step_1_data.update({'oc_p_search-pr_name':"Animal type"})
        # success!

        response = self.client.post(self.wizard_url, step_1_data)
        wizard = response.context['wizard']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(wizard['steps'].current, 'oc_p_results')
        self.assertContains(response,"No matching object classes were found")
        self.assertContains(response,"No matching properties were found")

        step_2_data = {
            self.wizard_form_name+'-current_step': 'oc_p_results',
        } # nothing else needed, as we aren't picking a component.

        response = self.client.post(self.wizard_url, step_2_data)
        wizard = response.context['wizard']
        self.assertEqual(wizard['steps'].current, 'make_oc')

        # Now we make the object class
        step_3_data = {
            self.wizard_form_name+'-current_step': 'make_oc',
            'make_oc-name':"Animagus",
        }

        response = self.client.post(self.wizard_url, step_3_data)
        wizard = response.context['wizard']
        self.assertTrue('description' in response.context['wizard']['form'].errors.keys())
        self.assertTrue('workgroup' in response.context['wizard']['form'].errors.keys())

        # no "test item" yet.
        self.assertFalse(models._concept.objects.filter(name="Test Item").exists())

        # must submit a description at this step. But we are using a non-permitted workgroup.
        step_3_data.update({
            'make_oc-description':"A wizard who can change shape.",
            'make_oc-workgroup':self.wg2.pk
            })
        response = self.client.post(self.wizard_url, step_3_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('workgroup' in response.context['wizard']['form'].errors.keys())

        # must submit a description at this step. With the right workgroup
        step_3_data.update({
            'make_oc-workgroup':self.wg1.pk
            })
        response = self.client.post(self.wizard_url, step_3_data)
        self.assertEqual(response.status_code, 200)
        wizard = response.context['wizard']
        self.assertEqual(wizard['steps'].current, 'make_p')

        # Now we make the property
        step_4_data = {
            self.wizard_form_name+'-current_step': 'make_p',
            'make_p-name':"Animal type",
        }

        response = self.client.post(self.wizard_url, step_4_data)
        wizard = response.context['wizard']
        self.assertTrue('description' in response.context['wizard']['form'].errors.keys())
        self.assertTrue('workgroup' in response.context['wizard']['form'].errors.keys())

        # no "test item" yet.
        self.assertFalse(models._concept.objects.filter(name="Test Item").exists())

        # must submit a description at this step. But we are using a non-permitted workgroup.
        step_4_data.update({
            'make_p-description':"A wizard who can change shape.",
            'make_p-workgroup':self.wg2.pk
            })
        response = self.client.post(self.wizard_url, step_4_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('workgroup' in response.context['wizard']['form'].errors.keys())

        # must submit a description at this step. With the right workgroup
        step_4_data.update({
            'make_p-workgroup':self.wg1.pk
            })
        response = self.client.post(self.wizard_url, step_4_data)
        self.assertEqual(response.status_code, 200)
        wizard = response.context['wizard']
        self.assertEqual(wizard['steps'].current, 'find_dec_results')

        step_4_data.update(step_1_data)
        step_4_data.update(step_2_data)
        step_4_data.update(step_3_data)
        self.assertEqual(response.status_code, 200)
        wizard = response.context['wizard']
        self.assertEqual(response.context['form'].initial['name'], 'Animagus--Animal type')


        step_5_data = {}
        step_5_data.update(step_1_data)
        step_5_data.update(step_2_data)
        step_5_data.update(step_3_data)
        step_5_data.update(step_4_data)
        step_5_data.update({self.wizard_form_name+'-current_step': 'find_dec_results',})

        response = self.client.post(self.wizard_url, step_5_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('name' in response.context['wizard']['form'].errors.keys())


"""Ordinary. Wizarding. Level. Examinations. O.W.L.s. More commonly known as 'Owls'.
Study hard and you will be rewarded.
Fail to do so and the consequences may be... severe"""