from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings, modify_settings
from django.test.utils import setup_test_environment
from django.contrib.auth.models import User

from aristotle_mdr.contrib.self_publish import models as pub
from aristotle_mdr.forms.search import PermissionSearchQuerySet
from aristotle_mdr.models import ObjectClass, Workgroup
from aristotle_mdr.tests import utils
setup_test_environment()


@override_settings(
    ARISTOTLE_SETTINGS=dict(
        settings.ARISTOTLE_SETTINGS,
        EXTRA_CONCEPT_QUERYSETS={
            'visible': ['aristotle_mdr.contrib.self_publish.models.concept_visibility_query'],
            'public': ['aristotle_mdr.contrib.self_publish.models.concept_public_query']
        }
    )
)
class TestSelfPublishing(utils.LoggedInViewPages, TestCase):

    def test_self_publish_queryset_anon(self):
        u = User.objects.create_user(
            username="self-publisher",
            email="self@publisher.net",
            password="self-publisher")
        oc = ObjectClass.objects.create(
            name="A self-published item",
            definition="test",
            submitter=u
        )
        self.logout()
        response = self.client.get(oc.get_absolute_url())
        self.assertTrue(response.status_code == 302)

        oc = ObjectClass.objects.get(pk=oc.pk)
        self.assertFalse(oc._is_public)

        psqs = PermissionSearchQuerySet()
        psqs = psqs.auto_query('published').apply_permission_checks()
        self.assertEqual(len(psqs), 0)

        pub.PublicationRecord.objects.create(
            user=u,
            concept=oc,
            visibility=pub.PublicationRecord.VISIBILITY.public
        )

        response = self.client.get(oc.get_absolute_url())
        self.assertTrue(response.status_code == 200)

        oc = ObjectClass.objects.get(pk=oc.pk)
        self.assertTrue(oc._is_public)

        psqs = PermissionSearchQuerySet()
        psqs = psqs.auto_query('published').apply_permission_checks()
        self.assertEqual(len(psqs), 1)
