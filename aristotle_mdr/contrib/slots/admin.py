from django.contrib import admin
from reversion_compare.admin import CompareVersionAdmin
from aristotle_mdr.contrib.slots import models
import reversion


class SlotDefinitionAdmin(admin.ModelAdmin):
    list_display = ('slot_name', 'help_text', 'app_label', 'concept_type', 'datatype', 'cardinality')
    list_filter = ('app_label', 'concept_type', 'datatype', 'cardinality')
    search_fields = ('slot_name', 'help_text')


admin.site.register(models.SlotDefinition, SlotDefinitionAdmin)


class SlotInline(admin.TabularInline):
    model = models.Slot


reversion.revisions.register(models.Slot)
