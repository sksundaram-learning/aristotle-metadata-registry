from django.contrib import admin
from aristotle_mdr import admin as aristotle_admin # Must include 'admin' directly, otherwise causes issues.
from extension_test import models


class QuestionAdmin(aristotle_admin.ConceptAdmin):
    fieldsets = aristotle_admin.ConceptAdmin.fieldsets + [
            ('Question',
                {'fields': ['questionText','responseLength','collectedDataElement',]}),
    ]

class QuestionnaireAdmin(aristotle_admin.ConceptAdmin):
    fieldsets = aristotle_admin.ConceptAdmin.fieldsets + [
            ('Questions',
                {'fields': ['questions',]}),
    ]

admin.site.register(models.Question,QuestionAdmin)
admin.site.register(models.Questionnaire,QuestionnaireAdmin)
