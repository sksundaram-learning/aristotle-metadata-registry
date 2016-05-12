from django.test import TestCase
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.urlresolvers import reverse

import aristotle_mdr.tests.utils as utils
from aristotle_mdr import models

from django.test.utils import setup_test_environment
setup_test_environment()


class UserHomePages(utils.LoggedInViewPages, TestCase):
    def setUp(self):
        super(UserHomePages, self).setUp()

    def check_generic_pages(self):
        response = self.client.get(reverse('aristotle:userHome',))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('aristotle:userEdit',))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('aristotle:userInbox',))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('aristotle:userInbox', args=['all']))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('aristotle:userFavourites',))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('aristotle:userWorkgroups',))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('aristotle:user_workgroups_archives',))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('aristotle:userRecentItems',))
        self.assertEqual(response.status_code, 200)

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


    def test_user_can_see_how_to_publish_content_in_workgroups(self):
        self.login_viewer()

        from aristotle_mdr.models import WORKGROUP_OWNERSHIP
        wg1 = models.Workgroup.objects.create(
            name="Test WG",
            ownership=WORKGROUP_OWNERSHIP.registry
        )
        wg1.giveRoleToUser('viewer',self.viewer)
        
        response = self.client.get(wg1.get_absolute_url())
        self.assertEqual(response.status_code,200)

        self.assertTrue(
            "Content in this registry can be made visible by <em>any</em> "
            "Registration Authority." in response.content
        )
        self.assertTrue(
            "<em>locked</em> if its status is locked in" in response.content
            and "<em>any</em> registration authority"  in response.content
        )        
        ra = models.RegistrationAuthority.objects.create(name="RA1")
        wg2 = models.Workgroup.objects.create(
            name="Test WG",
            ownership=WORKGROUP_OWNERSHIP.authority
        )
        wg2.registrationAuthorities.add(ra)
        wg2.save()

        wg2.giveRoleToUser('viewer',self.viewer)
        response = self.client.get(wg2.get_absolute_url())
        self.assertEqual(response.status_code,200)
        
        self.assertTrue(
            "<em>locked</em> if its status is:" in response.content
        )
        self.assertTrue(
            "<li>%s or above in" % ra.get_locked_state_display() in response.content
        )
        self.assertTrue(
            "<em>publically visible</em> if its status is:" in response.content
        )
        self.assertTrue(
            "<li>%s or above in" % ra.get_public_state_display() in response.content
        )


    def test_user_can_filter_and_sort_workgroups(self):
        self.login_viewer()

        # make some workgroups
        for i in range(1,4):
            wg1 = models.Workgroup.objects.create(name="Test WG match_this_name %s"%i)
            wg1.giveRoleToUser('viewer',self.viewer)
            for j in range(i):
                models.ObjectClass.objects.create(name="Test item",workgroup=wg1)
        for i in range(4,7):
            wg1 = models.Workgroup.objects.create(name="Test WG %s"%i,definition="match_this_definition")
            wg1.giveRoleToUser('viewer',self.viewer)
            for j in range(i):
                models.ObjectClass.objects.create(name="Test item",workgroup=wg1)

        #should have 7 workgroups now.

        response = self.client.get(reverse('aristotle:userWorkgroups'))
        self.assertEqual(response.status_code,200)

        self.assertTrue(self.viewer.profile.myWorkgroups,7)

        wg1.archived=True

        self.assertTrue(self.viewer.profile.myWorkgroups,6)

        response = self.client.get(reverse('aristotle:userWorkgroups'))

        self.assertTrue(len(response.context['page']),self.viewer.profile.myWorkgroups.count())

        response = self.client.get(reverse('aristotle:userWorkgroups')+"?filter=match_this_name")
        self.assertEqual(len(response.context['page']),3)
        for wg in response.context['page']:
            self.assertTrue('match_this_name' in wg.name)

        response = self.client.get(reverse('aristotle:userWorkgroups')+"?sort=items_desc")
        wgs = list(response.context['page'])
        # When sorting by number off items assert that each workgroup has more items than the next.
        for a,b in zip(wgs[:-1],wgs[1:]):
            self.assertTrue(a.items.count() >= b.items.count())


    def test_user_can_filter_and_sort_archived_workgroups(self):
        self.login_viewer()

        # make some workgroups
        for i in range(1,4):
            wg1 = models.Workgroup.objects.create(name="Test WG match_this_name %s"%i)
            wg1.giveRoleToUser('viewer',self.viewer)
            for j in range(i):
                models.ObjectClass.objects.create(name="Test item",workgroup=wg1)
        for i in range(4,7):
            wg1 = models.Workgroup.objects.create(name="Test WG %s"%i,definition="match_this_definition")
            wg1.giveRoleToUser('viewer',self.viewer)
            for j in range(i):
                models.ObjectClass.objects.create(name="Test item",workgroup=wg1)
            wg1.archived=True
            wg1.save()

        #should have 7 workgroups now with 3 archived

        response = self.client.get(reverse('aristotle:user_workgroups_archives'))
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.context['page']),3)
        for wg in response.context['page']:
            self.assertTrue(wg.archived)

    def test_registrar_can_access_tools(self):
        self.login_registrar()
        self.check_generic_pages()

        self.assertTrue(self.registrar.profile.is_registrar)
        response = self.client.get(reverse('aristotle:userRegistrarTools',))
        self.assertEqual(response.status_code,200)
        response = self.client.get(reverse('aristotle:userReadyForReview',))
        self.assertEqual(response.status_code,200)

    def test_registrar_has_valid_items_in_ready_to_review(self):

        item1 = models.ObjectClass.objects.create(name="Test Item 1",definition=" ",workgroup=self.wg1)
        item2 = models.ObjectClass.objects.create(name="Test Item 2",definition=" ",workgroup=self.wg2)
        item3 = models.ObjectClass.objects.create(name="Test Item 3",definition=" ",workgroup=self.wg1,readyToReview=True)
        item4 = models.ObjectClass.objects.create(name="Test Item 4",definition=" ",workgroup=self.wg2,readyToReview=True)

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
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('aristotle:userAdminStats',))
        self.assertEqual(response.status_code, 200)
        self.logout()

    def test_login_redirects(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)

        self.login_superuser()
        response = self.client.get("/login")
        self.assertRedirects(response, reverse('aristotle:userHome'))

        response = self.client.get("/login?next=" + reverse('aristotle:userFavourites'))
        self.assertRedirects(response, reverse('aristotle:userFavourites'))


class UserDashRecentItems(utils.LoggedInViewPages, TestCase):
    def setUp(self):
        super(UserDashRecentItems, self).setUp()
        import haystack
        haystack.connections.reload('default')

    def tearDown(self):
        call_command('clear_index', interactive=False, verbosity=0)

    def test_user_recent_dashboard_panel(self):

        self.login_editor()

        response = self.client.get(reverse('aristotle:userHome',))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['recent']), 0)

        wizard_url = reverse('aristotle:createItem', args=['aristotle_mdr', 'objectclass'])
        wizard_form_name = "dynamic_aristotle_wizard"

        step_1_data = {
            wizard_form_name + '-current_step': 'initial',
            'initial-name': "Test Item"
        }

        response = self.client.post(wizard_url, step_1_data)
        self.assertFalse(models._concept.objects.filter(name="Test Item").exists())
        step_2_data = {
            wizard_form_name + '-current_step': 'results',
            'results-name': "Test Item",
            'results-definition': "Test Definition",
            'results-workgroup': self.wg1.pk
        }
        response = self.client.post(wizard_url, step_2_data)
        self.assertTrue(models._concept.objects.filter(name="Test Item").exists())
        self.assertEqual(models._concept.objects.filter(name="Test Item").count(), 1)
        item = models._concept.objects.filter(name="Test Item").first()

        from reversion.models import Revision

        response = self.client.get(reverse('aristotle:userHome'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.context['recent']),
            Revision.objects.filter(user=self.editor).count()
        )

        # Lets update an item so there is some recent history
        updated_item = utils.model_to_dict_with_change_time(item)
        updated_name = updated_item['name'] + " updated!"
        updated_item['name'] = updated_name
        response = self.client.post(reverse('aristotle:edit_item', args=[item.id]), updated_item)
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('aristotle:userHome',))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['recent']), Revision.objects.filter(user=self.editor).count())

        self.assertContains(response, "Changed name")
