from __future__ import unicode_literals

from django.db import models

import aristotle_mdr

class Question(aristotle_mdr.models.concept):
    template = "extension_test/concepts/question.html"
    questionText = models.TextField(blank=True, null=True)
    responseLength = models.PositiveIntegerField(blank=True, null=True)
    collectedDataElement = models.ForeignKey(
            aristotle_mdr.models.DataElement,
            related_name="questions",
            null=True,blank=True)
