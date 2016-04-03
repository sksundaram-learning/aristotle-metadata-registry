from django.contrib import admin
from reversion_compare.admin import CompareVersionAdmin
from aristotle_mdr.contrib.slots import models


class SlotDefinitionAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.SlotDefinition, SlotDefinitionAdmin)
