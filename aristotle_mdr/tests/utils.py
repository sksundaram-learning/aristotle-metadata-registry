from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils import timezone

import aristotle_mdr.models as models
import aristotle_mdr.perms as perms
from aristotle_mdr.utils import url_slugify_concept

# Since all managed objects have the same rules, these can be used to cover everything
# This isn't an actual TestCase, we'll just pretend it is
class ManagedObjectVisibility(object):
    def setUp(self):
        self.ra = models.RegistrationAuthority.objects.create(name="Test RA")
        self.wg = models.Workgroup.objects.create(name="Test WG")
        self.wg.registrationAuthorities.add(self.ra)

    def test_object_is_public(self):
        self.assertEqual(self.item.is_public(),False)
        s = models.Status.objects.create(
                concept=self.item,
                registrationAuthority=self.ra,
                registrationDate=timezone.now(),
                state=self.ra.public_state
                )
        self.assertEqual(s.registrationAuthority,self.ra)
        self.assertEqual(self.item.is_public(),True)
        self.ra.public_state = models.STATES.standard
        self.ra.save()

        self.item = models._concept.objects.get(id=self.item.id) # Stupid cache
        self.assertEqual(self.item.is_public(),False)
        self.item.statuses.first().state = models.STATES.standard
        self.item.save()
        self.assertEqual(self.item.is_public(),False)

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
    def setUp(self):
        from django.test import Client

        self.client = Client()
        self.wg1 = models.Workgroup.objects.create(name="Test WG 1") # Editor is member
        self.wg2 = models.Workgroup.objects.create(name="Test WG 2")
        self.ra = models.RegistrationAuthority.objects.create(name="Test RA")
        self.wg1.registrationAuthorities.add(self.ra)
        self.wg1.save()

        self.su = User.objects.create_superuser('super','','user')
        self.manager = User.objects.create_user('mandy','','manager')
        self.manager.is_staff=True
        self.manager.save()
        self.editor = User.objects.create_user('eddie','','editor')
        self.editor.is_staff=True
        self.editor.save()
        self.viewer = User.objects.create_user('vicky','','viewer')
        self.registrar = User.objects.create_user('reggie','','registrar')

        self.wg1.submitters.add(self.editor)
        self.wg1.managers.add(self.manager)
        self.wg1.viewers.add(self.viewer)
        self.ra.registrars.add(self.registrar)

        self.editor = User.objects.get(pk=self.editor.pk)
        self.manager = User.objects.get(pk=self.manager.pk)
        self.viewer = User.objects.get(pk=self.viewer.pk)
        self.registrar = User.objects.get(pk=self.registrar.pk)

    def get_page(self,item):
        return url_slugify_concept(item)

    def get_help_page(self):
        return reverse('aristotle:about',args=[self.item1._meta.model_name])

    def logout(self):
        self.client.post(reverse('django.contrib.auth.views.logout'), {})

    def login_superuser(self):
        self.logout()
        response = self.client.post(reverse('django.contrib.auth.views.login'), {'username': 'super', 'password': 'user'})
        self.assertEqual(response.status_code,302)
        return response
    def login_viewer(self):
        self.logout()
        response = self.client.post(reverse('django.contrib.auth.views.login'), {'username': 'vicky', 'password': 'viewer'})
        self.assertEqual(response.status_code,302)
        return response
    def login_registrar(self):
        self.logout()
        response = self.client.post(reverse('django.contrib.auth.views.login'), {'username': 'reggie', 'password': 'registrar'})
        self.assertEqual(response.status_code,302)
        return response
    def login_editor(self):
        self.logout()
        response = self.client.post(reverse('django.contrib.auth.views.login'), {'username': 'eddie', 'password': 'editor'})
        self.assertEqual(response.status_code,302)
        return response
    def login_manager(self):
        self.logout()
        response = self.client.post(reverse('django.contrib.auth.views.login'), {'username': 'mandy', 'password': 'manager'})
        self.assertEqual(response.status_code,302)
        return response

    def test_logins(self):
        # Failed logins reutrn 200, not 401
        # See http://stackoverflow.com/questions/25839434/
        response = self.client.post(reverse('django.contrib.auth.views.login'), {'username': 'super', 'password': 'the_wrong_password'})
        self.assertEqual(response.status_code,200)
        # Success redirects to the homepage, so its 302 not 200
        response = self.client.post(reverse('django.contrib.auth.views.login'), {'username': 'super', 'password': 'user'})
        self.assertEqual(response.status_code,302)
        self.logout()
        response = self.client.post(reverse('django.contrib.auth.views.login'), {'username': 'eddie', 'password': 'editor'})
        self.assertEqual(response.status_code,302)
        self.logout()
        response = self.client.post(reverse('django.contrib.auth.views.login'), {'username': 'vicky', 'password': 'viewer'})
        self.assertEqual(response.status_code,302)
        self.logout()
        response = self.client.post(reverse('django.contrib.auth.views.login'), {'username': 'reggie', 'password': 'registrar'})
        self.assertEqual(response.status_code,302)
        self.logout()
