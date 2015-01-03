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

class Questionnaire(aristotle_mdr.models.concept):
    # Questionnaire is a test of a lazy developer who has done the bare minimum
    # To get an object in the system. This is a test of how little a dev can to
    # get a functional object. Ideally the string 'Questionnaire' should exist only here.

    #template = "extension_test/concepts/question.html" # Blank to test default template
    questions = models.ManyToManyField(
            Question,
            related_name="questionnaires",
            null=True,blank=True)
