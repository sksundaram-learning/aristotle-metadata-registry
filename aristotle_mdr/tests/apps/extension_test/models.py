from __future__ import unicode_literals

# Start of the question model

from aristotle_mdr import models as MDR
from django.db import models


class Question(MDR.concept):
    template = "extension_test/concepts/question.html"
    questionText = models.TextField(blank=True, null=True)
    responseLength = models.PositiveIntegerField(blank=True, null=True)
    collectedDataElement = models.ForeignKey(
        MDR.DataElement,
        related_name="questions",
        null=True,
        blank=True
    )

# End of the question model


class Questionnaire(MDR.concept):
    # Questionnaire is a test of a lazy developer who has done the bare minimum
    # To get an object in the system. This is a test of how little a dev can to
    # get a functional object. Ideally the string 'Questionnaire' should exist only here.
    edit_page_excludes = ['questions', 'respondent_classes','targetrespondentclass']
    admin_page_excludes = ['respondent_classes','targetrespondentclass']
    # template = "extension_test/concepts/question.html"  # Blank to test default template
    questions = models.ManyToManyField(
        Question,
        related_name="questionnaires",
        null=True,
        blank=True
    )
    respondent_classes = models.ManyToManyField(
        MDR.ObjectClass,
        through='TargetRespondentClass'
    )

    # Start of get_download_items
    def get_download_items(self):
        return [
            (
                Question,
                self.questions.all().order_by('name')
            ),
            (
                MDR.DataElement,
                MDR.DataElement.objects.filter(questions__questionnaires=self).order_by('name')
            ),
        ]
    # End of get_download_items


# This is a pretty contrived testing model
class TargetRespondentClass(MDR.aristotleComponent):
    @property
    def parentItem(self):
        return self.questionnaire

    questionnaire = models.ForeignKey('Questionnaire')
    respondent_class = models.ForeignKey(MDR.ObjectClass)
    rationale = models.TextField(blank=True, null=True)
