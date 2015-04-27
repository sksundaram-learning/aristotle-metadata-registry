from django.contrib import admin
from extension_test import models

from aristotle_mdr.register import register_concept

register_concept(models.Question,
    extra_fieldsets=[
            ('Question',
                {'fields': ['questionText','responseLength','collectedDataElement',]}),
    ])

register_concept(models.Questionnaire,
    extra_fieldsets=[
            ('Questions',
                {'fields': ['questions',]}),
    ])
