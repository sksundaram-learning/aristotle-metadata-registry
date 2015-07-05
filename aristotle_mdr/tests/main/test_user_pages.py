from django.test import TestCase
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.urlresolvers import reverse

import aristotle_mdr.tests.utils as utils
from aristotle_mdr import models

from django.test.utils import setup_test_environment
setup_test_environment()

class UserHomePages(utils.LoggedInViewPages,TestCase):
    def setUp(self):
        super(UserHomePages, self).setUp()

    def check_generic_pages(self):
        response = self.client.get(reverse('aristotle:userHome',))
        self.assertEqual(response.status_code,200)
        response = self.client.get(reverse('aristotle:userEdit',))
        self.assertEqual(response.status_code,200)
        response = self.client.get(reverse('aristotle:userInbox',))
        self.assertEqual(response.status_code,200)
        response = self.client.get(reverse('aristotle:userInbox',args=['all']))
        self.assertEqual(response.status_code,200)
        response = self.client.get(reverse('aristotle:userFavourites',))
        self.assertEqual(response.status_code,200)
        response = self.client.get(reverse('aristotle:userWorkgroups',))
        self.assertEqual(response.status_code,200)
        response = self.client.get(reverse('aristotle:user_workgroups_archives',))
        self.assertEqual(response.status_code,200)
        response = self.client.get(reverse('aristotle:userRecentItems',))
        self.assertEqual(response.status_code,200)

    def test_user_can_edit_own_details(self):
        self.login_viewer()
        new_email = 'my_new@email.com'
        response = self.client.post(reverse('aristotle:userEdit'),
            {
                'first_name':self.viewer.first_name,
                'last_name':self.viewer.last_name,
                'email': new_email,
            })
        self.assertEqual(response.status_code,302)
        self.viewer = User.objects.get(pk=self.viewer.pk)
        self.assertEqual(self.viewer.email,new_email)

    def test_viewer_can_access_homepages(self):
        self.login_viewer()
        self.check_generic_pages()

        # A viewer, has no registrar permissions:
        response = self.client.get(reverse('aristotle:userRegistrarTools',))
        self.assertEqual(response.status_code,403)
        response = self.client.get(reverse('aristotle:userReadyForReview',))
        self.assertEqual(response.status_code,403)

        # A view is not a superuser
        response = self.client.get(reverse('aristotle:userAdminTools',))
        self.assertEqual(response.status_code,403)
        response = self.client.get(reverse('aristotle:userAdminStats',))
        self.assertEqual(response.status_code,403)
        self.logout()

    def test_registrar_can_access_tools(self):
        self.login_registrar()
        self.check_generic_pages()

        self.assertTrue(self.registrar.profile.is_registrar)
        response = self.client.get(reverse('aristotle:userRegistrarTools',))
        self.assertEqual(response.status_code,200)
        response = self.client.get(reverse('aristotle:userReadyForReview',))
        self.assertEqual(response.status_code,200)

    def test_registrar_has_valid_items_in_ready_to_review(self):

        item1 = models.ObjectClass.objects.create(name="Test Item 1",description=" ",workgroup=self.wg1)
        item2 = models.ObjectClass.objects.create(name="Test Item 2",description=" ",workgroup=self.wg2)
        item3 = models.ObjectClass.objects.create(name="Test Item 3",description=" ",workgroup=self.wg1,readyToReview=True)
        item4 = models.ObjectClass.objects.create(name="Test Item 4",description=" ",workgroup=self.wg2,readyToReview=True)

        self.login_registrar()

        response = self.client.get(reverse('aristotle:userReadyForReview',))
        self.assertEqual(response.status_code,200)

        self.assertTrue(len(response.context['items']),1)
        self.assertTrue(item3 in response.context['items'])
        self.assertTrue(item1 not in response.context['items'])
        self.assertTrue(item2 not in response.context['items'])
        self.assertTrue(item4 not in response.context['items'])

    def test_superuser_can_access_tools(self):
        self.login_superuser()
        self.check_generic_pages()

        self.assertTrue(self.su.profile.is_registrar)
        response = self.client.get(reverse('aristotle:userRegistrarTools',))
        self.assertEqual(response.status_code,200)
        response = self.client.get(reverse('aristotle:userReadyForReview',))
        self.assertEqual(response.status_code,200)

        self.assertTrue(self.su.is_superuser)
        response = self.client.get(reverse('aristotle:userAdminTools',))
        self.assertEqual(response.status_code,200)
        response = self.client.get(reverse('aristotle:userAdminStats',))
        self.assertEqual(response.status_code,200)
        self.logout()

    def test_login_redirects(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code,200)

        self.login_superuser()
        response = self.client.get("/login")
        self.assertRedirects(response,reverse('aristotle:userHome'))

        response = self.client.get("/login?next="+reverse('aristotle:userFavourites'))
        self.assertRedirects(response,reverse('aristotle:userFavourites'))

class UserDashRecentItems(utils.LoggedInViewPages,TestCase):
    def setUp(self):
        super(UserDashRecentItems, self).setUp()
        import haystack
        haystack.connections.reload('default')

    def tearDown(self):
        call_command('clear_index', interactive=False, verbosity=0)

    def test_user_recent_dashboard_panel(self):

        self.login_editor()

        response = self.client.get(reverse('aristotle:userHome',))
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.context['recent']),0)

        wizard_url = reverse('aristotle:createItem',args=['aristotle_mdr','objectclass'])
        wizard_form_name="dynamic_aristotle_wizard"

        step_1_data = {
            wizard_form_name+'-current_step': 'initial',
            'initial-name':"Test Item"
        }

        response = self.client.post(wizard_url, step_1_data)

        step_2_data = {
            wizard_form_name+'-current_step': 'results',
            'results-name':"Test Item",
            'results-description':"Test Description",
            'results-workgroup':self.wg1.pk
            }
        response = self.client.post(wizard_url, step_2_data)
        self.assertTrue(models._concept.objects.filter(name="Test Item").exists())
        self.assertEqual(models._concept.objects.filter(name="Test Item").count(),1)
        item = models._concept.objects.filter(name="Test Item").first()

        response = self.client.get(reverse('aristotle:userHome',))
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.context['recent']),1)

        # Lets update an item so there is some recent history
        from django.forms import model_to_dict
        updated_item = dict((k,v) for (k,v) in model_to_dict(item).items() if v is not None)
        updated_name = updated_item['name'] + " updated!"
        updated_item['name'] = updated_name
        response = self.client.post(reverse('aristotle:edit_item',args=[item.id]), updated_item)

        response = self.client.get(reverse('aristotle:userHome',))
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.context['recent']),2)

        self.assertContains(response,"Changed name")
