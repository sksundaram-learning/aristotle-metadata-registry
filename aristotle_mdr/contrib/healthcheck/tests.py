import mock
from django.db import DatabaseError
from django.test import Client
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.unittest import TestCase
from django.test.utils import setup_test_environment

setup_test_environment()


class TestChaosMonkey(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    # eek
    def test_its_all_ok(self):
        # Test with no value
        response = self.client.get(reverse('aristotle_mdr_hb:health'))
        self.assertEqual(response.status_code, 200)

    def test_dead_database(self):
        from django.conf import settings

        response = self.client.get(reverse('aristotle_mdr_hb:health'))
        print response.content
        self.assertEqual(response.status_code, 500)


cursor_wrapper = mock.Mock()
cursor_wrapper.side_effect = DatabaseError


@mock.patch('django.db.backends.util.CursorWrapper', cursor_wrapper)
class NoDBTest(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_dead_database(self):
        print settings.DATABASES['default']['ENGINE']
        response = self.client.get(reverse('aristotle_mdr_hb:health'))
        print response.content
        self.assertEqual(response.status_code, 500)
