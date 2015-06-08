from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils import timezone

import datetime

import aristotle_mdr.models as models
import aristotle_mdr.perms as perms
from aristotle_mdr.utils import url_slugify_concept

from django_tools.unittest_utils.BrowserDebug import debug_response

from time import sleep
def wait_for_signal_to_fire(seconds=1):
    sleep(seconds)

# Since all managed objects have the same rules, these can be used to cover everything
# This isn't an actual TestCase, we'll just pretend it is
class ManagedObjectVisibility(object):
    def setUpClass(cls):
        cls.ra = models.RegistrationAuthority.objects.create(name="Test RA",
                        public_state=models.STATES.qualified,
                        locked_state=models.STATES.candidate)

        cls.wg = models.Workgroup.objects.create(name="Test WG")
        cls.wg.registrationAuthorities.add(cls.ra)

    def tearDownClass(cls):
        cls.ra.delete()
        cls.wg.delete()
        super(ManagedObjectVisibility, cls).tearDownClass()

    def test_object_is_public(self):
        self.assertEqual(self.item.is_public(),False)
        s = models.Status.objects.create(
                concept=self.item,
                registrationAuthority=self.ra,
                registrationDate=timezone.now(),
                state=models.STATES.notprogressed
                )
        self.assertEqual(self.item.is_public(),False)

        s.state = self.ra.public_state
        s.save()

        self.item = models._concept.objects.get(id=self.item.id) # Stupid cache
        self.assertEqual(self.item.is_public(),True)

        s.state = self.ra.locked_state
        s.save()

        self.item = models._concept.objects.get(id=self.item.id) # Stupid cache
        self.assertEqual(self.item.is_public(),False)

    def test_object_visibility_over_time(self):
        date = datetime.date
        s1 = models.Status.objects.create(
            concept=self.item,
            registrationAuthority=self.ra,
            registrationDate=datetime.date(2000,1,1),
            state=models.STATES.incomplete,
            changeDetails="s1",
            )

        # Overlaps s1 (it has no end)
        s2 = models.Status.objects.create(
            concept=self.item,
            registrationAuthority=self.ra,
            registrationDate=datetime.date(2005,1,1),
            until_date=datetime.date(2005,06,29),
            state=self.ra.public_state,
            changeDetails="s2",
            )
        # Deliberately miss 2005-06-30
        # Overlaps s1 (no end)
        s3 = models.Status.objects.create(
            concept=self.item,
            registrationAuthority=self.ra,
            registrationDate=datetime.date(2005,7,1),
            state=self.ra.public_state,
            changeDetails="s3",
            )

        # Overlaps s1 and s3 (no end)
        s4 = models.Status.objects.create(
            concept=self.item,
            registrationAuthority=self.ra,
            registrationDate=datetime.date(2006,1,1),
            until_date=datetime.date(2006,12,30),
            state=self.ra.locked_state,
            changeDetails="s4",
            )

        # Overlaps s1 and s3 (no end), completely contanied within s4
        s5 = models.Status.objects.create(
            concept=self.item,
            registrationAuthority=self.ra,
            registrationDate=datetime.date(2006,3,1),
            until_date=datetime.date(2006,7,30),
            state=self.ra.public_state,
            changeDetails="s5",
            )

        # Overlaps s1 and s3 (no end), overlaps s4 in 2006-11
        s6 = models.Status.objects.create(
            concept=self.item,
            registrationAuthority=self.ra,
            registrationDate=datetime.date(2006,11,1),
            until_date=datetime.date(2008,7,30),
            state=self.ra.public_state,
            changeDetails="s6",
            )

        # Overlaps s1 and s3
        the_future = (timezone.now() + datetime.timedelta(days=100)).date()
        s7 = models.Status.objects.create(
            concept=self.item,
            registrationAuthority=self.ra,
            registrationDate=the_future,
            state=self.ra.locked_state,
            changeDetails="s7",
            )

        d = date(1999,1,1)
        self.assertEqual(self.item.check_is_public(when=d),False)
        self.assertEqual(self.item.check_is_locked(when=d),False)
        self.assertEqual(self.item.current_statuses(when=d),[])

        d = date(2000,1,1)
        self.assertEqual(self.item.check_is_public(when=d),False)
        self.assertEqual(self.item.check_is_locked(when=d),False)
        self.assertEqual(self.item.current_statuses(when=d),[s1])

        d = date(2005,1,1)
        self.assertEqual(self.item.check_is_public(when=d),True)
        self.assertEqual(self.item.check_is_locked(when=d),True)
        self.assertEqual(self.item.current_statuses(when=d),[s2])

        d = date(2005,6,29)
        self.assertEqual(self.item.check_is_public(when=d),True)
        self.assertEqual(self.item.check_is_locked(when=d),True)
        self.assertEqual(self.item.current_statuses(when=d),[s2])

        d = date(2005,6,30)
        self.assertEqual(self.item.check_is_public(when=d),False)
        self.assertEqual(self.item.check_is_locked(when=d),False)
        self.assertEqual(self.item.current_statuses(when=d),[s1])

        d = date(2005,7,1)
        self.assertEqual(self.item.check_is_public(when=d),True)
        self.assertEqual(self.item.check_is_locked(when=d),True)
        self.assertEqual(self.item.current_statuses(when=d),[s3])

        d = date(2006,2,1)
        self.assertEqual(self.item.check_is_public(when=d),False)
        self.assertEqual(self.item.check_is_locked(when=d),True)
        self.assertEqual(self.item.current_statuses(when=d),[s4])

        d = date(2006,3,1)
        self.assertEqual(self.item.check_is_public(when=d),True)
        self.assertEqual(self.item.check_is_locked(when=d),True)
        self.assertEqual(self.item.current_statuses(when=d),[s5])

        d = date(2006,8,1)
        self.assertEqual(self.item.check_is_public(when=d),False)
        self.assertEqual(self.item.check_is_locked(when=d),True)
        self.assertEqual(self.item.current_statuses(when=d),[s4])

        d = date(2006,10,31)
        self.assertEqual(self.item.check_is_public(when=d),False)
        self.assertEqual(self.item.check_is_locked(when=d),True)
        self.assertEqual(self.item.current_statuses(when=d),[s4])

        d = date(2006,11,1)
        self.assertEqual(self.item.check_is_public(when=d),True)
        self.assertEqual(self.item.check_is_locked(when=d),True)
        self.assertEqual(self.item.current_statuses(when=d),[s6])

        d = date(2008,07,30)
        self.assertEqual(self.item.check_is_public(when=d),True)
        self.assertEqual(self.item.check_is_locked(when=d),True)
        self.assertEqual(self.item.current_statuses(when=d),[s6])

        d = date(2008,8,1)
        self.assertEqual(self.item.check_is_public(when=d),True)
        self.assertEqual(self.item.check_is_locked(when=d),True)
        self.assertEqual(self.item.current_statuses(when=d),[s3])

        self.assertEqual(self.item.check_is_public(),True)
        self.assertEqual(self.item.check_is_locked(),True)
        self.assertEqual(self.item.current_statuses(),[s3])

        d = the_future - datetime.timedelta(days=1)
        self.assertEqual(self.item.check_is_public(when=d),True)
        self.assertEqual(self.item.check_is_locked(when=d),True)
        self.assertEqual(self.item.current_statuses(when=d),[s3])

        d = the_future + datetime.timedelta(days=1)
        self.assertEqual(self.item.check_is_public(when=d),False)
        self.assertEqual(self.item.check_is_locked(when=d),True)
        self.assertEqual(self.item.current_statuses(when=d),[s7])

    def test_object_is_public_after_ra_state_changes(self):
        self.assertEqual(self.item.is_public(),False)
        s = models.Status.objects.create(
                concept=self.item,
                registrationAuthority=self.ra,
                registrationDate=timezone.now(),
                state=models.STATES.candidate
                )
        self.item = models._concept.objects.get(id=self.item.id) # Stupid cache
        self.assertEqual(self.item.is_public(),False)

        self.ra.public_state = models.STATES.candidate
        self.ra.save()

        from django.core import management # Lets recache this workgroup
        management.call_command('recache_registration_authority_item_visibility', ra=[self.ra.pk], verbosity=0)
        wait_for_signal_to_fire(seconds=10) # Not sure if the above in async or not

        self.item = models._concept.objects.get(id=self.item.id) # Stupid cache
        self.assertEqual(self.item.is_public(),True)

        self.ra.public_state = models.STATES.qualified
        self.ra.save()

        from django.core import management # Lets recache this workgroup
        management.call_command('recache_registration_authority_item_visibility', ra=[self.ra.pk], verbosity=0)
        wait_for_signal_to_fire(seconds=10) # Not sure if the above in async or not

        self.item = models._concept.objects.get(id=self.item.id) # Stupid cache
        self.assertEqual(self.item.is_public(),False)

    def test_object_is_locked(self):
        self.assertEqual(self.item.is_locked(),False)
        s = models.Status.objects.create(
                concept=self.item,
                registrationAuthority=self.ra,
                registrationDate=timezone.now(),
                state=models.STATES.notprogressed
                )
        self.assertEqual(self.item.is_locked(),False)

        s.state = self.ra.public_state
        s.save()

        self.item = models._concept.objects.get(id=self.item.id) # Stupid cache
        self.assertEqual(self.item.is_public(),True)

        s.state = self.ra.locked_state
        s.save()

        self.item = models._concept.objects.get(id=self.item.id) # Stupid cache
        self.assertEqual(self.item.is_locked(),True)

    def test_object_is_locked_after_ra_state_changes(self):
        self.assertEqual(self.item.is_locked(),False)
        s = models.Status.objects.create(
                concept=self.item,
                registrationAuthority=self.ra,
                registrationDate=timezone.now(),
                state=models.STATES.candidate
                )
        self.item = models._concept.objects.get(id=self.item.id) # Stupid cache
        self.assertEqual(self.item.is_locked(),True)

        self.ra.locked_state = models.STATES.standard
        self.ra.save()

        from django.core import management # Lets recache this RA
        management.call_command('recache_registration_authority_item_visibility', ra=[self.ra.pk], verbosity=0)
        wait_for_signal_to_fire(seconds=10) # Not sure if the above in async or not

        self.item = models._concept.objects.get(id=self.item.id) # Stupid cache
        self.assertEqual(self.item.is_locked(),False)

        self.ra.locked_state = models.STATES.candidate
        self.ra.save()

        from django.core import management # Lets recache this RA
        management.call_command('recache_registration_authority_item_visibility', ra=[self.ra.pk], verbosity=0)
        wait_for_signal_to_fire(seconds=10) # Not sure if the above in async or not

        self.item = models._concept.objects.get(id=self.item.id) # Stupid cache
        self.assertEqual(self.item.is_locked(),True)

    def test_registrar_can_view(self):
        # make editor for wg1
        r1 = User.objects.create_user('reggie','','reg')

        self.assertEqual(perms.user_can_view(r1,self.item),False)
        s = models.Status.objects.create(
                concept=self.item,
                registrationAuthority=self.ra,
                registrationDate=timezone.now(),
                state=self.ra.locked_state
                )
        self.assertEqual(perms.user_can_view(r1,self.item),False)
        # Caching issue, refresh from DB with correct permissions
        self.ra.giveRoleToUser('registrar',r1)
        r1 = User.objects.get(pk=r1.pk)

        self.assertEqual(perms.user_can_view(r1,self.item),True)


    def test_object_submitter_can_view(self):
        # make editor for wg1
        wg1 = models.Workgroup.objects.create(name="Test WG 1")
        e1 = User.objects.create_user('editor1','','editor1')
        wg1.giveRoleToUser('submitter',e1)

        # make editor for wg2
        wg2 = models.Workgroup.objects.create(name="Test WG 2")
        e2 = User.objects.create_user('editor2','','editor2')
        wg2.giveRoleToUser('submitter',e2)

        wg1.registrationAuthorities.add(self.ra)
        wg2.registrationAuthorities.add(self.ra)

        # ensure object is in wg1
        self.item.workgroup = wg1
        self.item.save()

        # test editor 1 can view, editor 2 cannot
        self.assertEqual(perms.user_can_view(e1,self.item),True)
        self.assertEqual(perms.user_can_view(e2,self.item),False)

        # move object to wg2
        self.item.workgroup = wg2
        self.item.save()

        # test editor 2 can view, editor 1 cannot
        self.assertEqual(perms.user_can_view(e2,self.item),True)
        self.assertEqual(perms.user_can_view(e1,self.item),False)

        s = models.Status.objects.create(
                concept=self.item,
                registrationAuthority=self.ra,
                registrationDate=timezone.now(),
                state=self.ra.locked_state
                )
        # Editor 2 can view. Editor 1 cannot
        self.assertEqual(perms.user_can_view(e2,self.item),True)
        self.assertEqual(perms.user_can_view(e1,self.item),False)

        # Set status to a public state
        s.state = self.ra.public_state
        s.save()
        # Both can view, neither can edit.
        self.assertEqual(perms.user_can_view(e1,self.item),True)
        self.assertEqual(perms.user_can_view(e2,self.item),True)

    def test_object_submitter_can_edit(self):
        registrar = User.objects.create_user('registrar','','registrar')
        self.ra.registrars.add(registrar)

        # make editor for wg1
        wg1 = models.Workgroup.objects.create(name="Test WG 1")
        e1 = User.objects.create_user('editor1','','editor1')
        wg1.giveRoleToUser('submitter',e1)

        # make editor for wg2
        wg2 = models.Workgroup.objects.create(name="Test WG 2")
        e2 = User.objects.create_user('editor2','','editor2')
        wg2.giveRoleToUser('submitter',e2)

        wg1.registrationAuthorities.add(self.ra)
        wg2.registrationAuthorities.add(self.ra)

        # ensure object is in wg1
        self.item.workgroup = wg1
        self.item.save()

        # test editor 1 can edit, editor 2 cannot
        self.assertEqual(perms.user_can_edit(e1,self.item),True)
        self.assertEqual(perms.user_can_edit(e2,self.item),False)

        # move Object Class to wg2
        self.item.workgroup = wg2
        self.item.save()

        # test editor 2 can edit, editor 1 cannot
        self.assertEqual(perms.user_can_edit(e2,self.item),True)
        self.assertEqual(perms.user_can_edit(e1,self.item),False)

        #self.ra.register(self.item,self.ra.locked_state,registrar,timezone.now(),)
        s = models.Status.objects.create(
                concept=self.item,
                registrationAuthority=self.ra,
                registrationDate=timezone.now(),
                state=self.ra.locked_state
                )
        # Editor 2 can no longer edit. Neither can Editor 1
        self.assertEqual(perms.user_can_edit(e2,self.item),False)
        self.assertEqual(perms.user_can_view(e1,self.item),False)

class LoggedInViewPages(object):
    """
    This helps us manage testing across different user types.
    """
    def setUpClass(cls):
        from django.test import Client

        cls.client = Client()
        cls.wg1 = models.Workgroup.objects.create(name="Test WG 1") # Editor is member
        cls.wg2 = models.Workgroup.objects.create(name="Test WG 2")
        cls.ra = models.RegistrationAuthority.objects.create(name="Test RA")
        cls.wg1.registrationAuthorities.add(cls.ra)
        cls.wg1.save()

        cls.su = User.objects.create_superuser('super','','user')
        cls.manager = User.objects.create_user('mandy','','manager')
        cls.manager.is_staff=True
        cls.manager.save()
        cls.editor = User.objects.create_user('eddie','','editor')
        cls.editor.is_staff=True
        cls.editor.save()
        cls.viewer = User.objects.create_user('vicky','','viewer')
        cls.registrar = User.objects.create_user('reggie','','registrar')

        cls.wg1.submitters.add(cls.editor)
        cls.wg1.managers.add(cls.manager)
        cls.wg1.viewers.add(cls.viewer)
        cls.ra.registrars.add(cls.registrar)

        cls.editor = User.objects.get(pk=cls.editor.pk)
        cls.manager = User.objects.get(pk=cls.manager.pk)
        cls.viewer = User.objects.get(pk=cls.viewer.pk)
        cls.registrar = User.objects.get(pk=cls.registrar.pk)


    def tearDownClass(cls):
        cls.ra.delete()

        cls.su.delete()
        cls.manager.delete()
        cls.editor.delete()
        cls.viewer.delete()
        cls.registrar.delete()

        cls.wg1.delete()
        cls.wg2.delete()
        super(LoggedInViewPages, cls).tearDownClass()

    def get_page(self,item):
        return url_slugify_concept(item)

    def get_help_page(self):
        return reverse('aristotle:about',args=[self.item1._meta.model_name])

    def logout(self):
        self.client.post(reverse('django.contrib.auth.views.logout'), {})

    def login_superuser(self):
        self.logout()
        response = self.client.post(reverse('friendly_login'), {'username': 'super', 'password': 'user'})
        self.assertEqual(response.status_code,302)
        return response
    def login_viewer(self):
        self.logout()
        response = self.client.post(reverse('friendly_login'), {'username': 'vicky', 'password': 'viewer'})
        self.assertEqual(response.status_code,302)
        return response
    def login_registrar(self):
        self.logout()
        response = self.client.post(reverse('friendly_login'), {'username': 'reggie', 'password': 'registrar'})
        self.assertEqual(response.status_code,302)
        return response
    def login_editor(self):
        self.logout()
        response = self.client.post(reverse('friendly_login'), {'username': 'eddie', 'password': 'editor'})
        self.assertEqual(response.status_code,302)
        return response
    def login_manager(self):
        self.logout()
        response = self.client.post(reverse('friendly_login'), {'username': 'mandy', 'password': 'manager'})
        self.assertEqual(response.status_code,302)
        return response

    def test_logins(self):
        # Failed logins reutrn 200, not 401
        # See http://stackoverflow.com/questions/25839434/
        response = self.client.post(reverse('friendly_login'), {'username': 'super', 'password': 'the_wrong_password'})
        self.assertEqual(response.status_code,200)
        # Success redirects to the homepage, so its 302 not 200
        response = self.client.post(reverse('friendly_login'), {'username': 'super', 'password': 'user'})
        self.assertEqual(response.status_code,302)
        self.logout()
        response = self.client.post(reverse('friendly_login'), {'username': 'eddie', 'password': 'editor'})
        self.assertEqual(response.status_code,302)
        self.logout()
        response = self.client.post(reverse('friendly_login'), {'username': 'vicky', 'password': 'viewer'})
        self.assertEqual(response.status_code,302)
        self.logout()
        response = self.client.post(reverse('friendly_login'), {'username': 'reggie', 'password': 'registrar'})
        self.assertEqual(response.status_code,302)
        self.logout()

    # These are lovingly lifted from django-reversion-compare
    # https://github.com/jedie/django-reversion-compare/blob/master/tests/test_utils/test_cases.py
    def assertContainsHtml(self, response, *args):
        for html in args:
            try:
                self.assertContains(response, html, html=True)
            except AssertionError as e: #pragma: no cover
                # Needs no coverage as the test should pass to be successful
                debug_response(response, msg="%s" % e) # from django-tools
                raise
    def assertNotContainsHtml(self, response, *args):
        for html in args:
            try:
                self.assertNotContains(response, html, html=True)
            except AssertionError as e: #pragma: no cover
                # Needs no coverage as the test should pass to be successful
                debug_response(response, msg="%s" % e) # from django-tools
                raise

    def assertResponseStatusCodeEqual(self,response,code):
            try:
                self.assertEqual(response.status_code, code)
            except AssertionError as e: #pragma: no cover
                # Needs no coverage as the test should pass to be successful
                print(response)
                print(e)
                raise
