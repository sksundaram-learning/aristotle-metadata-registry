from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings
from django.test.utils import setup_test_environment
from django.utils import timezone

import aristotle_mdr.models as models
import aristotle_mdr.perms as perms
from aristotle_mdr.utils import url_slugify_concept
from aristotle_mdr.forms.creation_wizards import WorkgroupVerificationMixin,CheckIfModifiedMixin

setup_test_environment()
from aristotle_mdr.tests import utils
import datetime

class AnonymousUserViewingThePages(TestCase):
    def test_homepage(self):
        home = self.client.get("/")
        self.assertEqual(home.status_code,200)

    def test_notifications_for_anon_users(self):
        home = self.client.get("/")
        self.assertEqual(home.status_code,200)
        # Make sure notifications library isn't loaded for anon users as they'll never have notifications.
        self.assertTrue("notifications/notify.js" not in home.content)
        # At some stage this might need a better test to check the 500 page doesn't show... after notifications is fixed.
        
    def test_visible_item(self):
        wg = models.Workgroup.objects.create(name="Setup WG")
        ra = models.RegistrationAuthority.objects.create(name="Test RA")
        wg.registrationAuthorities.add(ra)
        item = models.ObjectClass.objects.create(name="Test OC",workgroup=wg)
        s = models.Status.objects.create(
                concept=item,
                registrationAuthority=ra,
                registrationDate=timezone.now(),
                state=ra.locked_state
                )
        home = self.client.get(url_slugify_concept(item))
        # Anonymous users requesting a hidden page will be redirected to login
        self.assertEqual(home.status_code,302)
        s.state = ra.public_state
        s.save()
        home = self.client.get(url_slugify_concept(item))
        self.assertEqual(home.status_code,200)

def setUpModule():
    from django.core.management import call_command
    call_command('loadhelp', 'aristotle_help/concept_help/*', verbosity=0, interactive=False)

class LoggedInViewConceptPages(utils.LoggedInViewPages):
    defaults = {}
    def setUp(self):
        super(LoggedInViewConceptPages, self).setUp()

        self.item1 = self.itemType.objects.create(name="Test Item 1 (visible to tested viewers)",definition=" ",workgroup=self.wg1,**self.defaults)
        self.item2 = self.itemType.objects.create(name="Test Item 2 (NOT visible to tested viewers)",definition=" ",workgroup=self.wg2,**self.defaults)
        self.item3 = self.itemType.objects.create(name="Test Item 3 (visible to tested viewers)",definition=" ",workgroup=self.wg1,**self.defaults)

    def test_su_can_view(self):
        self.login_superuser()
        response = self.client.get(self.get_page(self.item1))
        self.assertEqual(response.status_code,200)
        response = self.client.get(self.get_page(self.item2))
        self.assertEqual(response.status_code,200)

    def test_editor_can_view(self):
        self.login_editor()
        response = self.client.get(self.get_page(self.item1))
        self.assertEqual(response.status_code,200)
        response = self.client.get(self.get_page(self.item2))
        self.assertEqual(response.status_code,403)

    def test_viewer_can_view(self):
        self.login_viewer()
        response = self.client.get(self.get_page(self.item1))
        self.assertEqual(response.status_code,200)
        response = self.client.get(self.get_page(self.item2))
        self.assertEqual(response.status_code,403)

    def test_stubs_redirect_correctly(self):
        self.login_viewer()
        response = self.client.get(reverse('aristotle:item',args=[self.item1.id]))
        self.assertRedirects(response,url_slugify_concept(self.item1))
        response = self.client.get(reverse('aristotle:item',args=[self.item1.id])+"/not-a-model/fake-name")
        self.assertRedirects(response,url_slugify_concept(self.item1))
        response = self.client.get(reverse('aristotle:item',args=[self.item1.id])+"/this-isnt-even-a-proper-stub")
        self.assertRedirects(response,url_slugify_concept(self.item1))

    def test_anon_cannot_view_edit_page(self):
        self.logout()
        response = self.client.get(reverse('aristotle:edit_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,302)
        response = self.client.get(reverse('aristotle:edit_item',args=[self.item2.id]))
        self.assertEqual(response.status_code,302)
    def test_viewer_cannot_view_edit_page(self):
        self.login_viewer()
        response = self.client.get(reverse('aristotle:edit_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,403)
        response = self.client.get(reverse('aristotle:edit_item',args=[self.item2.id]))
        self.assertEqual(response.status_code,403)
    def test_submitter_can_view_edit_page(self):
        self.login_editor()
        response = self.client.get(reverse('aristotle:edit_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)
        form = response.context['form']
        self.assertTrue('change_comments' in form.fields)

        response = self.client.get(reverse('aristotle:edit_item',args=[self.item2.id]))
        self.assertEqual(response.status_code,403)

    def test_submitter_can_save_via_edit_page(self):
        self.login_editor()
        response = self.client.get(reverse('aristotle:edit_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)

        updated_item = utils.model_to_dict_with_change_time(response.context['item'])
        updated_name = updated_item['name'] + " updated!"
        updated_item['name'] = updated_name
        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.item1 = self.itemType.objects.get(pk=self.item1.pk)
        self.assertRedirects(response,url_slugify_concept(self.item1))
        self.assertEqual(self.item1.name,updated_name)

    def test_submitter_can_save_via_edit_page_with_change_comment(self):
        self.login_editor()
        response = self.client.get(reverse('aristotle:edit_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)

        updated_item = utils.model_to_dict_with_change_time(response.context['item'])
        updated_name = updated_item['name'] + " updated!"
        updated_item['name'] = updated_name
        change_comment = "I changed this because I can"
        updated_item['change_comments'] = change_comment
        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.item1 = self.itemType.objects.get(pk=self.item1.pk)

        self.assertRedirects(response,url_slugify_concept(self.item1))
        self.assertEqual(self.item1.name,updated_name)

        response = self.client.get(reverse('aristotle:item_history',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)
        self.assertTrue(change_comment in response.content)

    def test_submitter_can_save_via_edit_page_with_slots(self):
        self.login_editor()
        response = self.client.get(reverse('aristotle:edit_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)

        self.assertEqual(self.item1.slots.count(),0)

        from aristotle_mdr.contrib.slots.models import SlotDefinition, Slot
        slot_def = SlotDefinition.objects.create(
            app_label=self.itemType._meta.app_label,
            concept_type=self.itemType._meta.model_name,
            slot_name="extra",
            cardinality=SlotDefinition.CARDINALITY.singleton
        )

        updated_item = utils.model_to_dict_with_change_time(response.context['item'])
        updated_name = updated_item['name'] + " updated!"
        updated_item['name'] = updated_name

        # Add slots management form
        updated_item['slots-TOTAL_FORMS'] = 1
        updated_item['slots-INITIAL_FORMS'] = 0
        updated_item['slots-MIN_NUM_FORMS'] = 0
        updated_item['slots-MAX_NUM_FORMS'] = 1

        updated_item['slots-0-concept'] = self.item1.pk
        updated_item['slots-0-type'] = slot_def.pk
        updated_item['slots-0-value'] = 'test slot value'

        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.item1 = self.itemType.objects.get(pk=self.item1.pk)

        self.assertRedirects(response,url_slugify_concept(self.item1))
        self.assertEqual(self.item1.slots.count(),1)

        response = self.client.get(reverse('aristotle:edit_item',args=[self.item1.id]))
        self.assertTrue('test slot value' in response.content)


    def test_submitter_cannot_save_via_edit_page_with_slots_that_are_duplicates(self):
        self.login_editor()
        response = self.client.get(reverse('aristotle:edit_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)

        self.assertEqual(self.item1.slots.count(),0)

        from aristotle_mdr.contrib.slots.models import SlotDefinition, Slot
        slot_def = SlotDefinition.objects.create(
            app_label=self.itemType._meta.app_label,
            concept_type=self.itemType._meta.model_name,
            slot_name="extra",
            cardinality=SlotDefinition.CARDINALITY.singleton
        )

        updated_item = utils.model_to_dict_with_change_time(response.context['item'])
        updated_name = updated_item['name'] + " updated!"
        updated_item['name'] = updated_name

        # Add slots management form
        updated_item['slots-TOTAL_FORMS'] = 2
        updated_item['slots-INITIAL_FORMS'] = 0
        updated_item['slots-MIN_NUM_FORMS'] = 0
        updated_item['slots-MAX_NUM_FORMS'] = 2

        updated_item['slots-0-concept'] = self.item1.pk
        updated_item['slots-0-type'] = slot_def.pk
        updated_item['slots-0-value'] = 'test slot value'
        updated_item['slots-1-concept'] = self.item1.pk
        updated_item['slots-1-type'] = slot_def.pk
        updated_item['slots-1-value'] = 'test slot value2'

        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.item1 = self.itemType.objects.get(pk=self.item1.pk)

        self.assertEqual(response.status_code,200)
        self.assertEqual(self.item1.slots.count(),0)
        
        self.assertTrue("The selected slot type &#39;%(slot_name)s&#39; is only allowed to be included once" % {'slot_name': slot_def.slot_name} in response.content)

    def test_submitter_cannot_save_via_edit_page_with_slots_that_are_for_a_different_metadata_type(self):
        self.login_editor()

        from aristotle_mdr.contrib.slots.models import SlotDefinition, Slot
        if self.itemType._meta.model_name == "property":
            other_type = "objectclass"
        else:
            other_type = "property"
        slot_def = SlotDefinition.objects.create(
            app_label=self.itemType._meta.app_label,
            concept_type=other_type,
            slot_name="extra slot not available",
            cardinality=SlotDefinition.CARDINALITY.singleton
        )

        response = self.client.get(reverse('aristotle:edit_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)

        self.assertEqual(self.item1.slots.count(),0)
        self.assertTrue(slot_def.slot_name not in response.content)
        
        updated_item = utils.model_to_dict_with_change_time(response.context['item'])
        updated_name = updated_item['name'] + " updated!"
        updated_item['name'] = updated_name

        # Add slots management form
        updated_item['slots-TOTAL_FORMS'] = 1
        updated_item['slots-INITIAL_FORMS'] = 0
        updated_item['slots-MIN_NUM_FORMS'] = 0
        updated_item['slots-MAX_NUM_FORMS'] = 1

        updated_item['slots-0-concept'] = self.item1.pk
        updated_item['slots-0-type'] = slot_def.pk
        updated_item['slots-0-value'] = 'test slot value'

        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.item1 = self.itemType.objects.get(pk=self.item1.pk)

        self.assertEqual(response.status_code,200)
        self.assertEqual(self.item1.slots.count(),0)
        
        self.assertTrue("Select a valid choice. That choice is not one of the available choices" in response.content)

    def test_submitter_cannot_save_via_edit_page_if_other_saves_made(self):
        from datetime import timedelta
        self.login_editor()
        modified = self.item1.modified
        response = self.client.get(reverse('aristotle:edit_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)

        # fake that we fetched the page seconds before modification
        updated_item = utils.model_to_dict_with_change_time(response.context['item'],fetch_time=modified-timedelta(seconds=5))
        updated_name = updated_item['name'] + " updated!"
        updated_item['name'] = updated_name
        change_comment = "I changed this because I can"
        updated_item['change_comments'] = change_comment
        time_before_response = timezone.now()
        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)

        self.assertEqual(response.status_code,200)
        form = response.context['form']
        self.assertTrue(form.errors['last_fetched'][0] == CheckIfModifiedMixin.modified_since_form_fetched_error)

        # When sending a response with a bad last_fetch, the new one should come back right
        self.assertTrue(time_before_response < form.fields['last_fetched'].initial)

        # With the new last_fetched we can submit ok!
        updated_item['last_fetched'] = form.fields['last_fetched'].initial
        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.assertEqual(response.status_code,302)


        updated_item.pop('last_fetched')
        time_before_response = timezone.now()
        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)

        self.assertEqual(response.status_code,200)
        form = response.context['form']
        self.assertTrue(form.errors['last_fetched'][0] == CheckIfModifiedMixin.modified_since_field_missing)
        # When sending a response with no last_fetch, the new one should come back right
        self.assertTrue(time_before_response < form.fields['last_fetched'].initial)

        # With the new last_fetched we can submit ok!
        updated_item['last_fetched'] = form.fields['last_fetched'].initial
        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.assertEqual(response.status_code,302)

    # Test if workgroup-moving settings work

    @override_settings(ARISTOTLE_SETTINGS=dict(settings.ARISTOTLE_SETTINGS, WORKGROUP_CHANGES=[]))
    def test_submitter_cannot_change_workgroup_via_edit_page(self):
        # based on the idea that 'submitter' is not set in ARISTOTLE_SETTINGS.WORKGROUP
        self.wg_other = models.Workgroup.objects.create(name="Test WG to move to")
        self.wg_other.submitters.add(self.editor)

        self.login_editor()
        response = self.client.get(reverse('aristotle:edit_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)

        updated_item = utils.model_to_dict_with_change_time(response.context['item'])

        updated_item['workgroup'] = str(self.wg_other.pk)

        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.assertEqual(response.status_code,200)

        form = response.context['form']

        self.assertTrue('workgroup' in form.errors.keys())
        self.assertTrue(len(form.errors['workgroup'])==1)

        # Submitter is logged in, tries to move item - fails because
        self.assertFalse(perms.user_can_remove_from_workgroup(self.editor,self.item1.workgroup))
        self.assertTrue(form.errors['workgroup'][0] == WorkgroupVerificationMixin.cant_move_any_permission_error)

        updated_item['workgroup'] = str(self.wg2.pk)
        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.assertEqual(response.status_code,200)

        form = response.context['form']

        self.assertTrue('workgroup' in form.errors.keys())
        self.assertTrue(len(form.errors['workgroup'])==1)

        self.assertTrue('Select a valid choice.' in form.errors['workgroup'][0])

    @override_settings(ARISTOTLE_SETTINGS=dict(settings.ARISTOTLE_SETTINGS, WORKGROUP_CHANGES=['submitter']))
    def test_submitter_can_change_workgroup_via_edit_page(self):
        # based on the idea that 'submitter' is set in ARISTOTLE_SETTINGS.WORKGROUP
        self.wg_other = models.Workgroup.objects.create(name="Test WG to move to")

        self.login_editor()
        response = self.client.get(reverse('aristotle:edit_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)
        updated_item = utils.model_to_dict_with_change_time(response.context['item'])
        updated_item['workgroup'] = str(self.wg_other.pk)

        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.assertEqual(response.status_code,200)

        form = response.context['form']

        self.assertTrue('Select a valid choice.' in form.errors['workgroup'][0])

        self.wg_other.submitters.add(self.editor)

        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.assertEqual(response.status_code,302)

        updated_item['workgroup'] = str(self.wg2.pk)
        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.assertEqual(response.status_code,200)

        self.assertTrue('Select a valid choice.' in form.errors['workgroup'][0])


    @override_settings(ARISTOTLE_SETTINGS=dict(settings.ARISTOTLE_SETTINGS, WORKGROUP_CHANGES=['admin']))
    def test_admin_can_change_workgroup_via_edit_page(self):
        # based on the idea that 'admin' is set in ARISTOTLE_SETTINGS.WORKGROUP
        self.wg_other = models.Workgroup.objects.create(name="Test WG to move to")

        self.login_superuser()
        response = self.client.get(reverse('aristotle:edit_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)
        updated_item = utils.model_to_dict_with_change_time(self.item1)
        updated_item['workgroup'] = str(self.wg_other.pk)

        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.assertEqual(response.status_code,302)

        updated_item = utils.model_to_dict_with_change_time(self.item1)
        updated_item['workgroup'] = str(self.wg2.pk)
        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.assertEqual(response.status_code,302)


    @override_settings(ARISTOTLE_SETTINGS=dict(settings.ARISTOTLE_SETTINGS, WORKGROUP_CHANGES=['manager']))
    def test_manager_of_two_workgroups_can_change_workgroup_via_edit_page(self):
        # based on the idea that 'manager' is set in ARISTOTLE_SETTINGS.WORKGROUP
        self.wg_other = models.Workgroup.objects.create(name="Test WG to move to")
        self.wg_other.submitters.add(self.editor)

        self.login_editor()
        response = self.client.get(reverse('aristotle:edit_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)
        updated_item = utils.model_to_dict_with_change_time(response.context['item'])
        updated_item['workgroup'] = str(self.wg_other.pk)
        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.assertEqual(response.status_code,200)

        form = response.context['form']
        # Submitter can't move because they aren't a manager of any workgroups.
        self.assertTrue(form.errors['workgroup'][0] == WorkgroupVerificationMixin.cant_move_any_permission_error)

        self.wg_other.managers.add(self.editor)

        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.assertEqual(response.status_code,200)

        form = response.context['form']
        # Submitter can't move because they aren't a manager of the workgroup the item is in.
        self.assertTrue(form.errors['workgroup'][0] == WorkgroupVerificationMixin.cant_move_from_permission_error)


        self.login_manager()

        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.assertEqual(response.status_code,403)

        self.wg1.submitters.add(self.manager) # Need to give manager edit permission to allow them to actually edit things
        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.assertEqual(response.status_code,200)
        form = response.context['form']

        self.assertTrue('Select a valid choice.' in form.errors['workgroup'][0])

        self.wg_other.managers.add(self.manager)

        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.assertEqual(response.status_code,200)
        self.assertTrue('Select a valid choice.' in form.errors['workgroup'][0])

        self.wg_other.submitters.add(self.manager) # Need to give manager edit permission to allow them to actually edit things
        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.assertEqual(response.status_code,302)

        updated_item['workgroup'] = str(self.wg2.pk)
        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.assertEqual(response.status_code,200)

        self.assertTrue('Select a valid choice.' in form.errors['workgroup'][0])

    def test_anon_cannot_view_clone_page(self):
        self.logout()
        response = self.client.get(reverse('aristotle:clone_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,302)
        response = self.client.get(reverse('aristotle:clone_item',args=[self.item2.id]))
        self.assertEqual(response.status_code,302)

    def test_viewer_cannot_view_clone_page(self):
        self.login_viewer()
        response = self.client.get(reverse('aristotle:clone_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,403)
        response = self.client.get(reverse('aristotle:clone_item',args=[self.item2.id]))
        self.assertEqual(response.status_code,403)

    def test_submitter_can_view_clone_page(self):
        self.login_editor()
        response = self.client.get(reverse('aristotle:clone_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)
        response = self.client.get(reverse('aristotle:clone_item',args=[self.item2.id]))
        self.assertEqual(response.status_code,403)

    def test_submitter_can_save_via_clone_page(self):
        self.login_editor()
        response = self.client.get(reverse('aristotle:clone_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)
        updated_item = utils.model_to_dict(response.context['item'])
        updated_name = updated_item['name'] + " cloned!"
        updated_item['name'] = updated_name
        response = self.client.post(reverse('aristotle:clone_item',args=[self.item1.id]), updated_item)
        most_recent = self.itemType.objects.order_by('-created').first()
        self.assertRedirects(response,url_slugify_concept(most_recent))
        self.assertEqual(most_recent.name,updated_name)
        
        # Make sure the right item was save and our original hasn't been altered.
        self.item1 = self.itemType.objects.get(id=self.item1.id) # Stupid cache
        self.assertTrue('cloned' not in self.item1.name)

    def test_su_can_download_pdf(self):
        self.login_superuser()
        response = self.client.get(reverse('aristotle:download',args=['pdf',self.item1.id]))
        self.assertEqual(response.status_code,200)
        response = self.client.get(reverse('aristotle:download',args=['pdf',self.item2.id]))
        self.assertEqual(response.status_code,200)

    def test_editor_can_download_pdf(self):
        self.login_editor()
        response = self.client.get(reverse('aristotle:download',args=['pdf',self.item1.id]))
        self.assertEqual(response.status_code,200)
        response = self.client.get(reverse('aristotle:download',args=['pdf',self.item2.id]))
        self.assertEqual(response.status_code,403)

    def test_viewer_can_download_pdf(self):
        self.login_viewer()
        response = self.client.get(reverse('aristotle:download',args=['pdf',self.item1.id]))
        self.assertEqual(response.status_code,200)
        response = self.client.get(reverse('aristotle:download',args=['pdf',self.item2.id]))
        self.assertEqual(response.status_code,403)

    def test_viewer_cannot_view_supersede_page(self):
        self.login_viewer()
        response = self.client.get(reverse('aristotle:supersede',args=[self.item1.id]))
        self.assertEqual(response.status_code,403)
        response = self.client.get(reverse('aristotle:supersede',args=[self.item2.id]))
        self.assertEqual(response.status_code,403)

    def test_editor_can_view_supersede_page(self):
        self.login_editor()
        response = self.client.get(reverse('aristotle:supersede',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)
        response = self.client.get(reverse('aristotle:supersede',args=[self.item2.id]))
        self.assertEqual(response.status_code,403)
        response = self.client.get(reverse('aristotle:supersede',args=[self.item3.id]))
        self.assertEqual(response.status_code,200)

    def test_editor_can_remove_supersede_relation(self):
        self.login_editor()
        self.item2 = self.itemType.objects.create(name="supersede this",workgroup=self.wg1)
        self.item1.superseded_by = self.item2
        self.item1.save()
        
        self.assertTrue(self.item1 in self.item2.supersedes.all())
        response = self.client.post(
            reverse('aristotle:supersede',args=[self.item1.id]),{'newerItem':""})
        self.assertEqual(response.status_code,302)
        self.item1 = self.itemType.objects.get(id=self.item1.id) # Stupid cache
        print self.item1.superseded_by, response
        self.assertTrue(self.item1.superseded_by == None)
        self.assertTrue(self.item2.supersedes.count() == 0)

    def test_editor_can_use_ready_to_review(self):
        self.login_editor()
        response = self.client.get(reverse('aristotle:mark_ready_to_review',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)
        response = self.client.get(reverse('aristotle:mark_ready_to_review',args=[self.item2.id]))
        self.assertEqual(response.status_code,403)
        response = self.client.get(reverse('aristotle:mark_ready_to_review',args=[self.item3.id]))
        self.assertEqual(response.status_code,200)

        self.assertFalse(self.item1.readyToReview)
        response = self.client.post(reverse('aristotle:mark_ready_to_review',args=[self.item1.id]))
        self.assertRedirects(response,url_slugify_concept(self.item1))
        self.item1 = self.itemType.objects.get(id=self.item1.id) # Stupid cache
        self.assertTrue(self.item1.readyToReview)

    def test_viewer_cannot_view_deprecate_page(self):
        self.login_viewer()
        response = self.client.get(reverse('aristotle:deprecate',args=[self.item1.id]))
        self.assertEqual(response.status_code,403)
        response = self.client.get(reverse('aristotle:deprecate',args=[self.item2.id]))
        self.assertEqual(response.status_code,403)

    def test_editor_can_view_deprecate_page(self):
        self.login_editor()
        response = self.client.get(reverse('aristotle:deprecate',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)
        response = self.client.get(reverse('aristotle:deprecate',args=[self.item2.id]))
        self.assertEqual(response.status_code,403)
        response = self.client.get(reverse('aristotle:deprecate',args=[self.item3.id]))
        self.assertEqual(response.status_code,200)

    def test_help_page_exists(self):
        self.logout()
        response = self.client.get(
            reverse('concept_help',args=[self.itemType._meta.app_label,self.itemType._meta.model_name])
        )
        self.assertEqual(response.status_code,200)

    def test_viewer_can_view_registration_history(self):
        self.login_viewer()
        response = self.client.get(reverse('aristotle:registrationHistory',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)
        response = self.client.get(reverse('aristotle:registrationHistory',args=[self.item2.id]))
        self.assertEqual(response.status_code,403)

    def test_anon_cannot_view_registration_history(self):
        self.logout()
        response = self.client.get(reverse('aristotle:registrationHistory',args=[self.item1.id]))
        self.assertEqual(response.status_code,302)
        response = self.client.get(reverse('aristotle:registrationHistory',args=[self.item2.id]))
        self.assertEqual(response.status_code,302)

    def test_viewer_can_view_item_history(self):
        # Workgroup members can see the edit history of items
        self.login_viewer()
        response = self.client.get(reverse('aristotle:item_history',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)
        response = self.client.get(reverse('aristotle:item_history',args=[self.item2.id]))
        self.assertEqual(response.status_code,403)

        # Viewers shouldn't even have the link to history on items they arent in the workgroup for
        response = self.client.get(self.item2.get_absolute_url())
        self.assertFalse(reverse('aristotle:item_history',args=[self.item2.id]) in response.content)

        # Viewers will even have the link to history on items they are in the workgroup for
        response = self.client.get(self.item1.get_absolute_url())
        self.assertTrue(reverse('aristotle:item_history',args=[self.item1.id]) in response.content)

    def test_editor_can_view_item_history__and__compare(self):
        self.login_editor()

        from reversion import revisions as reversion
        
        with reversion.create_revision():
            self.item1.name = "change 1"
            reversion.set_comment("change 1")
            self.item1.readyToReview = True
            self.item1.save()

        with reversion.create_revision():
            self.item1.name = "change 2"
            reversion.set_comment("change 2")
            r = self.ra.register(
                item=self.item1,
                state=models.STATES.incomplete,
                user=self.registrar
            )
            self.item1.save()

        revisions = reversion.default_revision_manager.get_for_object(self.item1)

        response = self.client.get(reverse('aristotle:item_history',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)

        response = self.client.get(
            reverse('aristotle:item_history',args=[self.item1.id]),
            {'version_id1' : revisions.first().pk,
            'version_id2' : revisions.last().pk
            }
        )
        
        self.assertEqual(response.status_code,200)
        self.assertTrue("change 2" in response.content)
        self.assertTrue('statuses' in response.content)
        
        self.item1 = self.itemType.objects.get(pk=self.item1.pk) #decache
        self.assertTrue(self.item1.name == "change 2")
        for s in self.item1.statuses.all():
            self.assertContains(
                response,
                '%s is %s'%(self.item1.name,s.get_state_display())
            )

    def test_editor_can_revert_item_and_status_goes_back_too(self):
        self.login_editor()
        
        from reversion import revisions as reversion
        with reversion.create_revision():
            self.item1.readyToReview = True
            self.item1.save()
        original_name = self.item1.name
        
        response = self.client.get(reverse('aristotle:edit_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)
        
        updated_item = utils.model_to_dict_with_change_time(response.context['item'])
        updated_name = updated_item['name'] + " updated!"
        updated_item['name'] = updated_name
        change_comment = "I changed this because I can"
        updated_item['change_comments'] = change_comment
        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.item1 = self.itemType.objects.get(pk=self.item1.pk)
        self.assertEqual(self.item1.name,updated_name)

        r = self.ra.register(
            item=self.item1,
            state=models.STATES.incomplete,
            user=self.registrar
        )
        self.item1 = self.itemType.objects.get(pk=self.item1.pk) #decache

        self.assertTrue(self.item1.statuses.all().count() == 1)
        self.assertTrue(self.item1.statuses.first().state == models.STATES.incomplete)

        response = self.client.get(reverse('aristotle:edit_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)
        updated_item = utils.model_to_dict_with_change_time(response.context['item'])
        updated_name_again = updated_item['name'] + " updated!"
        updated_item['name'] = updated_name_again
        change_comment = "I changed this again because I can"
        updated_item['change_comments'] = change_comment
        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.item1 = self.itemType.objects.get(pk=self.item1.pk)
        self.assertEqual(self.item1.name,updated_name_again)

        self.ra.register(self.item1,models.STATES.candidate,self.registrar)
        self.item1 = self.itemType.objects.get(pk=self.item1.pk) #decache
        self.assertTrue(self.item1.statuses.count() == 2)
        self.assertTrue(self.item1.statuses.last().state == models.STATES.candidate)

        versions = list(reversion.Version.objects.filter(object_id=self.item1.id))
        versions[4].revision.revert(delete=True) # The version that has the first status changes

        self.item1 = self.itemType.objects.get(pk=self.item1.pk) #decache

        self.assertTrue(self.item1.statuses.count() == 1)
        self.assertTrue(self.item1.statuses.first().state == models.STATES.incomplete)
        self.assertEqual(self.item1.name,updated_name)

        versions[0].revision.revert(delete=True)
        self.item1 = self.itemType.objects.get(pk=self.item1.pk) #decache
        self.assertTrue(self.item1.statuses.count() == 0)
        self.assertEqual(self.item1.name,original_name)

        versions[9].revision.revert(delete=True) # Back to the latest version
        self.item1 = self.itemType.objects.get(pk=self.item1.pk) #decache
        self.assertTrue(self.item1.statuses.count() == 2)
        self.assertTrue(self.item1.statuses.order_by('state')[0].state == models.STATES.incomplete)
        self.assertTrue(self.item1.statuses.order_by('state')[1].state == models.STATES.candidate)
        self.assertEqual(self.item1.name,updated_name_again)


    def test_anon_cannot_view_item_history(self):
        self.logout()
        response = self.client.get(reverse('aristotle:item_history',args=[self.item1.id]))
        self.assertEqual(response.status_code,302)
        response = self.client.get(reverse('aristotle:item_history',args=[self.item2.id]))
        self.assertEqual(response.status_code,302)


        # Register to check if link is on page... it shouldn't be
        models.Status.objects.create(
            concept=self.item1,
            registrationAuthority=self.ra,
            registrationDate = datetime.date(2009,4,28),
            state =  models.STATES.standard
            )
        # Anon users shouldn't even have the link to history *any* items
        response = self.client.get(self.item1.get_absolute_url())
        self.assertEqual(response.status_code,200)
        self.assertFalse(reverse('aristotle:item_history',args=[self.item1.id]) in response.content)

    def test_viewer_can_favourite(self):
        self.login_viewer()
        self.assertTrue(perms.user_can_view(self.viewer,self.item1))

        response = self.client.post(reverse('friendly_login'), {'username': 'vicky', 'password': 'viewer'})
        self.assertEqual(response.status_code,302)
        self.assertEqual(self.viewer.profile.favourites.count(),0)

        response = self.client.get(
            reverse('aristotle:toggleFavourite', args=[self.item1.id]),
            follow=True
        )
        self.assertEqual(
            response.redirect_chain,
            [('http://testserver'+url_slugify_concept(self.item1),302)]
        )
        self.assertEqual(self.viewer.profile.favourites.count(),1)
        self.assertEqual(self.viewer.profile.favourites.first().item,self.item1)
        self.assertTrue("added to favourites" in response.content)

        response = self.client.get(
            reverse('aristotle:toggleFavourite', args=[self.item1.id]),
            follow=True
        )
        self.assertEqual(
            response.redirect_chain,
            [('http://testserver'+url_slugify_concept(self.item1),302)]
        )
        self.assertEqual(self.viewer.profile.favourites.count(),0)
        self.assertTrue("removed from favourites" in response.content)

        response = self.client.get(reverse('aristotle:toggleFavourite', args=[self.item2.id]))
        self.assertEqual(response.status_code,403)
        self.assertEqual(self.viewer.profile.favourites.count(),0)

    def test_anon_cannot_favourite(self):
        self.logout()

        response = self.client.get(reverse('aristotle:toggleFavourite', args=[self.item1.id]))
        self.assertRedirects(response,reverse('friendly_login')+"?next="+reverse('aristotle:toggleFavourite', args=[self.item1.id]))

    def test_registrar_can_change_status(self):
        self.login_registrar()

        self.assertFalse(perms.user_can_view(self.registrar,self.item1))
        self.item1.readyToReview = True
        self.item1.save()
        self.item1 = self.itemType.objects.get(pk=self.item1.pk)

        self.assertTrue(perms.user_can_view(self.registrar,self.item1))
        self.assertTrue(perms.user_can_change_status(self.registrar,self.item1))

        response = self.client.get(reverse('aristotle:changeStatus',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)

        self.assertEqual(self.item1.statuses.count(),0)
        response = self.client.post(
            reverse('aristotle:changeStatus',args=[self.item1.id]),
            {
                'registrationAuthorities': [str(self.ra.id)],
                'state': self.ra.public_state,
                'changeDetails': "testing",
                'cascadeRegistration': 0, # no
            }
        )
        self.assertRedirects(response,url_slugify_concept(self.item1))

        self.item1 = self.itemType.objects.get(pk=self.item1.pk)
        self.assertEqual(self.item1.statuses.count(),1)
        self.assertTrue(self.item1.is_registered)
        self.assertTrue(self.item1.is_public())

    def test_registrar_can_change_status_with_cascade(self):
        if not hasattr(self,"run_cascade_tests"):
            return
        self.login_registrar()

        self.assertFalse(perms.user_can_view(self.registrar,self.item1))
        self.item1.readyToReview = True
        self.item1.save()
        self.item1 = self.itemType.objects.get(pk=self.item1.pk)

        self.assertTrue(perms.user_can_view(self.registrar,self.item1))
        self.assertTrue(perms.user_can_change_status(self.registrar,self.item1))

        response = self.client.get(reverse('aristotle:changeStatus',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)

        self.assertEqual(self.item1.statuses.count(),0)
        for sub_item in self.item1.registry_cascade_items:
            if sub_item is not None:
                self.assertEqual(sub_item.statuses.count(),0)

        response = self.client.post(
            reverse('aristotle:changeStatus',args=[self.item1.id]),
            {
                'registrationAuthorities': [str(self.ra.id)],
                'state': self.ra.public_state,
                'changeDetails': "testing",
                'cascadeRegistration': 1, # yes
            }
        )
        self.assertRedirects(response,url_slugify_concept(self.item1))

        self.item1 = self.itemType.objects.get(pk=self.item1.pk)
        self.assertEqual(self.item1.statuses.count(),1)
        self.assertTrue(self.item1.is_registered)
        self.assertTrue(self.item1.is_public())
        for sub_item in self.item1.registry_cascade_items:
            if sub_item is not None and perms.user_can_change_status(self.registrar,sub_item) :
                if not sub_item.is_registered: # pragma: no cover
                    # This is debug code, and should never happen
                    print sub_item
                self.assertTrue(sub_item.is_registered)

    def test_registrar_can_change_status_of_registry_owned_item(self):
        self.login_registrar()
        wg = self.item1.workgroup
        wg.ownership = models.WORKGROUP_OWNERSHIP.registry
        wg.registrationAuthorities = []
        wg.save()
        
        self.assertFalse(perms.user_can_view(self.registrar,self.item1))
        self.item1.readyToReview = True
        self.item1.save()
        self.item1 = self.itemType.objects.get(pk=self.item1.pk)

        self.assertTrue(perms.user_can_view(self.registrar,self.item1))
        self.assertTrue(perms.user_can_change_status(self.registrar,self.item1))

        response = self.client.get(reverse('aristotle:changeStatus',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)

        self.assertEqual(self.item1.statuses.count(),0)
        response = self.client.post(
            reverse('aristotle:changeStatus',args=[self.item1.id]),
            {
                'registrationAuthorities': [str(self.ra.id)],
                'state': self.ra.public_state,
                'changeDetails': "testing",
                'cascadeRegistration': 0, # no
            }
        )
        self.assertRedirects(response,url_slugify_concept(self.item1))

        self.item1 = self.itemType.objects.get(pk=self.item1.pk)
        self.assertEqual(self.item1.statuses.count(),1)
        self.assertTrue(self.item1.is_registered)
        self.assertTrue(self.item1.is_public())

    def test_registrar_cannot_use_faulty_statuses(self):
        self.login_registrar()

        self.assertFalse(perms.user_can_view(self.registrar,self.item1))
        self.item1.readyToReview = True
        self.item1.save()
        self.item1 = self.itemType.objects.get(pk=self.item1.pk)

        self.assertTrue(perms.user_can_view(self.registrar,self.item1))
        self.assertTrue(perms.user_can_change_status(self.registrar,self.item1))

        response = self.client.get(reverse('aristotle:changeStatus',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)

        self.assertEqual(self.item1.statuses.count(),0)
        response = self.client.post(
            reverse('aristotle:changeStatus', args=[self.item1.id]),
            {
                'registrationAuthorities': [str(self.ra.id)],
                'state': "Not a number", # obviously wrong
                'changeDetails': "testing",
                'cascadeRegistration': 0, # no
            }
        )
        self.assertFormError(response, 'form', 'state', 'Select a valid choice. Not a number is not one of the available choices.')

        response = self.client.post(
            reverse('aristotle:changeStatus',args=[self.item1.id]),
            {
                'registrationAuthorities': [str(self.ra.id)],
                'state': "343434", # also wrong
                'changeDetails': "testing",
                'cascadeRegistration': 0, # no
            }
        )
        self.assertFormError(response, 'form', 'state', 'Select a valid choice. 343434 is not one of the available choices.')

    def test_viewer_cannot_change_status(self):
        self.login_viewer()

        response = self.client.get(reverse('aristotle:changeStatus',args=[self.item1.id]))
        self.assertEqual(response.status_code,403)


    def test_anon_cannot_change_status(self):
        self.logout()

        response = self.client.get(reverse('aristotle:changeStatus',args=[self.item1.id]))
        self.assertRedirects(response,reverse('friendly_login')+"?next="+reverse('aristotle:changeStatus', args=[self.item1.id]))

class ObjectClassViewPage(LoggedInViewConceptPages,TestCase):
    url_name='objectClass'
    itemType=models.ObjectClass
class PropertyViewPage(LoggedInViewConceptPages,TestCase):
    url_name='property'
    itemType=models.Property
class UnitOfMeasureViewPage(LoggedInViewConceptPages,TestCase):
    url_name='unitOfMeasure'
    itemType=models.UnitOfMeasure
class ValueDomainViewPage(LoggedInViewConceptPages,TestCase):
    url_name='valueDomain'
    itemType=models.ValueDomain
    def setUp(self):
        super(ValueDomainViewPage, self).setUp()

        for i in range(4):
            models.PermissibleValue.objects.create(
                value=i,meaning="test permissible meaning %d"%i,order=i,valueDomain=self.item1
                )
        for i in range(4):
            models.SupplementaryValue.objects.create(
                value=i,meaning="test supplementary meaning %d"%i,order=i,valueDomain=self.item1
                )

    def test_anon_cannot_use_value_page(self):
        self.logout()
        response = self.client.get(reverse('aristotle:valueDomain_edit_values',args=[self.item1.id,'permissible']))
        self.assertRedirects(response,reverse('friendly_login')+"?next="+reverse('aristotle:valueDomain_edit_values',args=[self.item1.id,'permissible']))
        response = self.client.get(reverse('aristotle:valueDomain_edit_values',args=[self.item1.id,'supplementary']))
        self.assertRedirects(response,reverse('friendly_login')+"?next="+reverse('aristotle:valueDomain_edit_values',args=[self.item1.id,'supplementary']))

    def loggedin_user_can_use_value_page(self,value_type,current_item,http_code):
        response = self.client.get(reverse('aristotle:valueDomain_edit_values',args=[current_item.id,value_type]))
        self.assertEqual(response.status_code,http_code)

    def submitter_user_can_use_value_edit_page(self,value_type):
        self.login_editor()
        self.loggedin_user_can_use_value_page(value_type,self.item1,200)
        self.loggedin_user_can_use_value_page(value_type,self.item2,403)
        self.loggedin_user_can_use_value_page(value_type,self.item3,200)

        # Invalid value domain types are caught in the URL runner. This test isn't required yet.
        # response = self.client.get(reverse('aristotle:valueDomain_edit_values',args=[self.item1.id,'accidentally'])) # a fake value domain type
        # self.assertTrue(response.status_code,404)

        data = {}
        num_vals = getattr(self.item1,value_type+"Values").count()
        i=0
        for i,v in enumerate(getattr(self.item1,value_type+"Values").all()):
            data.update({"form-%d-id"%i: v.pk, "form-%d-order"%i : v.order, "form-%d-value"%i : v.value, "form-%d-meaning"%i : v.meaning+" -updated"})
        data.update({"form-%d-DELETE"%i: 'checked', "form-%d-meaning"%i : v.meaning+" - deleted"}) # delete the last one.
        # now add a new one
        i=i+1
        data.update({"form-%d-order"%i : i, "form-%d-value"%i : 100, "form-%d-meaning"%i : "new value -updated"})

        data.update({
            "form-TOTAL_FORMS":num_vals+1, "form-INITIAL_FORMS": num_vals, "form-MAX_NUM_FORMS":1000,

            })
        response = self.client.post(reverse('aristotle:valueDomain_edit_values',args=[self.item1.id,value_type]),data)
        self.item1 = models.ValueDomain.objects.get(pk=self.item1.pk)

        self.assertTrue(num_vals == getattr(self.item1,value_type+"Values").count())
        new_value_seen = False
        for v in getattr(self.item1,value_type+"Values").all():
            self.assertTrue('updated' in v.meaning) # This will fail if the deleted item isn't deleted
            if v.value == '100':
                new_value_seen = True
        self.assertTrue(new_value_seen)


        # Item is now locked, submitter is no longer able to edit
        models.Status.objects.create(
                concept=self.item1,
                registrationAuthority=self.ra,
                registrationDate=timezone.now(),
                state=self.ra.locked_state
                )

        self.item1 = models.ValueDomain.objects.get(pk=self.item1.pk)
        self.assertTrue(self.item1.is_locked())
        self.assertFalse(perms.user_can_edit(self.editor,self.item1))
        self.loggedin_user_can_use_value_page(value_type,self.item1,403)


    def test_submitter_can_use_permissible_value_edit_page(self):
        self.submitter_user_can_use_value_edit_page('permissible')

    def test_submitter_can_use_supplementary_value_edit_page(self):
        self.submitter_user_can_use_value_edit_page('supplementary')

    def test_su_can_download_pdf(self):
        self.login_superuser()
        response = self.client.get(reverse('aristotle:download',args=['csv-vd',self.item1.id]))
        self.assertEqual(response.status_code,200)
        response = self.client.get(reverse('aristotle:download',args=['csv-vd',self.item2.id]))
        self.assertEqual(response.status_code,200)

    def test_editor_can_download_csv(self):
        self.login_editor()
        response = self.client.get(reverse('aristotle:download',args=['csv-vd',self.item1.id]))
        self.assertEqual(response.status_code,200)
        response = self.client.get(reverse('aristotle:download',args=['csv-vd',self.item2.id]))
        self.assertEqual(response.status_code,403)

    def test_viewer_can_download_csv(self):
        self.login_viewer()
        response = self.client.get(reverse('aristotle:download',args=['csv-vd',self.item1.id]))
        self.assertEqual(response.status_code,200)
        response = self.client.get(reverse('aristotle:download',args=['csv-vd',self.item2.id]))
        self.assertEqual(response.status_code,403)

    def test_values_shown_on_page(self):
        self.login_viewer()

        response = self.client.get(self.get_page(self.item1))
        self.assertEqual(response.status_code,200)
        for pv in self.item1.permissiblevalue_set.all():
            self.assertContains(response,pv.meaning,1)
        for sv in self.item1.supplementaryvalue_set.all():
            self.assertContains(response,sv.meaning,1)

class ConceptualDomainViewPage(LoggedInViewConceptPages,TestCase):
    url_name='conceptualDomain'
    itemType=models.ConceptualDomain
class DataElementConceptViewPage(LoggedInViewConceptPages,TestCase):
    url_name='dataElementConcept'
    itemType=models.DataElementConcept
    run_cascade_tests = True
    
    def setUp(self, *args, **kwargs):
        super(DataElementConceptViewPage, self).setUp(*args, **kwargs)
        oc = models.ObjectClass.objects.create(
            name="sub item OC",
            workgroup=self.item1.workgroup,
            readyToReview = True
        )
        prop = models.Property.objects.create(
            name="sub item prop",
            workgroup=self.item1.workgroup
        )
        self.item1.objectClass = oc
        self.item1.property = prop
        self.item1.save()

class DataElementViewPage(LoggedInViewConceptPages,TestCase):
    url_name='dataElement'
    itemType=models.DataElement

class DataElementDerivationViewPage(LoggedInViewConceptPages,TestCase):
    url_name='dataelementderivation'
    @property
    def defaults(self):
        return {'derives':models.DataElement.objects.create(name='derivedDE',definition="",workgroup=self.wg1)}
    itemType=models.DataElementDerivation

class LoggedInViewUnmanagedPages(utils.LoggedInViewPages):
    defaults = {}
    def setUp(self):
        super(LoggedInViewUnmanagedPages, self).setUp()
        self.item1 = self.itemType.objects.create(name="OC1",**self.defaults)

    def get_page(self,item):
        url_name = "".join(item._meta.verbose_name.title().split())
        url_name = url_name[0].lower() + url_name[1:]
        return reverse('aristotle:%s'%url_name,args=[item.id])

    def test_help_page_exists(self):
        self.logout()
        #response = self.client.get(self.get_help_page())
        #self.assertEqual(response.status_code,200)

    def test_item_page_exists(self):
        self.logout()
        response = self.client.get(self.get_page(self.item1))
        self.assertEqual(response.status_code,200)

class MeasureViewPage(LoggedInViewUnmanagedPages,TestCase):
    url_name='measure'
    itemType=models.Measure

    def setUp(self):
        super(MeasureViewPage, self).setUp()

        self.item2 = models.UnitOfMeasure.objects.create(name="OC1",workgroup=self.wg1,measure=self.item1,**self.defaults)

class RegistrationAuthorityViewPage(LoggedInViewUnmanagedPages,TestCase):
    url_name='registrationAuthority'
    itemType=models.RegistrationAuthority

    def setUp(self):
        super(RegistrationAuthorityViewPage, self).setUp()

        self.item2 = models.DataElement.objects.create(name="OC1",workgroup=self.wg1,**self.defaults)

        s = models.Status.objects.create(
                concept=self.item2,
                registrationAuthority=self.item1,
                registrationDate=timezone.now(),
                state=models.STATES.standard
                )

    def get_page(self,item):
        return item.get_absolute_url()

    def test_view_all_ras(self):
        self.logout()
        response = self.client.get(reverse('aristotle:allRegistrationAuthorities'))
        self.assertTrue(response.status_code,200)
