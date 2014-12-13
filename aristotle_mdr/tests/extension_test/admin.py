from django.contrib import admin
from aristotle_mdr import admin as aristotle_admin # Must include 'admin' directly, otherwise causes issues.
import models


class QuestionAdmin(aristotle_admin.ConceptAdmin):
    fieldsets = aristotle_admin.ConceptAdmin.fieldsets + [
            ('Question',
                {'fields': ['questionText','responseLength','collectedDataElement',]}),
    ]

admin.site.register(models.Question,QuestionAdmin)