from django.contrib.auth.models import User

from django.core.urlresolvers import reverse
from django.template import Context, Template
from django.test import TestCase

import aristotle_mdr.models as models
import aristotle_mdr.perms as perms
import aristotle_mdr.tests.utils as utils

from django.test.utils import setup_test_environment
setup_test_environment()

from django.core.exceptions import FieldDoesNotExist

preamble = "{% load aristotle_tags %}"

class TestTemplateTags_aristotle_tags_py(TestCase):

    def setUp(self):
        self.ra = models.RegistrationAuthority.objects.create(name="Test RA")
        self.wg = models.Workgroup.objects.create(name="Test WG 1")
        self.wg.registrationAuthorities=[self.ra]
        self.wg.save()
        self.item = models.ObjectClass.objects.create(name="Test OC1",workgroup=self.wg)

    def test_doc(self):
        context = Context({"item": self.item})

        template = Template(preamble+"{% doc item 'definition' %}")
        template.render(context)

        template = Template(preamble+"{% doc item %}")
        template.render(context)
        
        with self.assertRaises(FieldDoesNotExist):
            template = Template(preamble+"{% doc item 'not_an_attribute' %}")
            template.render(context)
        

        
        