from django.test import TestCase

import aristotle_mdr.models as models
import aristotle_mdr.perms as perms
import aristotle_mdr.tests.utils as utils
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from aristotle_mdr.tests.utils import ManagedObjectVisibility

from django.test.utils import setup_test_environment
setup_test_environment()

from extension_test.models import Question

class QuestionVisibility(TestCase,ManagedObjectVisibility):
    def setUp(self):
        self.wg = models.Workgroup.objects.create(name="Setup WG")
        self.item = Question.objects.create(name="Test Question",
            workgroup=self.wg,
            )
