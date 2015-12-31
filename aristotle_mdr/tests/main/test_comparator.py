from django.test import TestCase

import aristotle_mdr.models as models
import aristotle_mdr.perms as perms
import aristotle_mdr.tests.utils as utils
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

import datetime
from django.utils import timezone

from django.test.utils import setup_test_environment
setup_test_environment()

class ComparatorTester(utils.LoggedInViewPages):

    def setUp(self):
        super(ComparatorTester, self).setUp()
        self.ra = models.RegistrationAuthority.objects.create(name="Test RA")
        self.wg = models.Workgroup.objects.create(name="Setup WG")
        self.wg.registrationAuthorities.add(self.ra)

    def test_compare_page_loads(self):

        item1 = self.itemType.objects.create(name="Test OC",workgroup=self.wg)
        s = models.Status.objects.create(
                concept=item1,
                registrationAuthority=self.ra,
                registrationDate=timezone.now(),
                state=self.ra.public_state
                )
        item2 = self.itemType.objects.create(name="Test OC",workgroup=self.wg)
        s = models.Status.objects.create(
                concept=item2,
                registrationAuthority=self.ra,
                registrationDate=timezone.now(),
                state=self.ra.public_state
                )
        item1 = self.itemType.objects.get(pk=item1.pk) #decache
        item2 = self.itemType.objects.get(pk=item1.pk) #decache

        self.assertTrue(item1.is_public())
        self.assertTrue(item2.is_public())
        response = self.client.get(
            reverse('aristotle:compare_concepts')+"?item_a=%s&item_b=%s"%(item1.id,item2.id)
            )
        self.assertEqual(response.status_code,200)

class ObjectClassComparatorTester(ComparatorTester,TestCase):
    itemType=models.ObjectClass
    
class ValueDomainComparatorTester(ComparatorTester,TestCase):
    itemType=models.ValueDomain
