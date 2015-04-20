from __future__ import absolute_import
import autocomplete_light

from django.contrib import admin
from aristotle_mdr import admin as aristotle_admin # Must include 'admin' directly, otherwise causes issues.
from aristotle_mdr import autocomplete_light_registry as reg
from aristotle_mdr.search_indexes import conceptIndex

import aristotle_mdr.search_indexes as search_index

from haystack import connections
from haystack.constants import DEFAULT_ALIAS
from haystack import indexes

def register_concept(concept_class, *args, **kwargs):
    _register_concept_autocomplete(concept_class, *args, **kwargs)
    _register_concept_admin(concept_class, *args, **kwargs)
    _register_concept_search_index(concept_class, *args, **kwargs)
    #return si

def _register_concept_autocomplete(concept_class, *args, **kwargs):
    x = reg.autocompleteTemplate.copy()
    x['name']='Autocomplete'+concept_class.__name__
    autocomplete_light.register(concept_class,reg.PermissionsAutocomplete,**x)

def _register_concept_search_index(concept_class, *args, **kwargs):
    class_name = "%s_%sSearchIndex"%(concept_class._meta.app_label,concept_class.__name__)
    setattr(search_index, class_name, create(concept_class))

    # Since we've added a new class, kill the index so it is rebuilt.
    connections[DEFAULT_ALIAS]._index = None

def create(cls):
    class SubclassedConceptIndex(conceptIndex, indexes.Indexable):
        def get_model(self):
            return cls
    return SubclassedConceptIndex


def _register_concept_admin(concept_class, *args, **kwargs):
    """
    """
    extra_fieldsets = kwargs.get('extra_fieldsets',[])
    auto_fieldsets = kwargs.get('auto_fieldsets',False)
    auto_fieldsets_name = kwargs.get('auto_fieldsets_name',False)
    extra_inlines = kwargs.get('extra_inlines',[])

    if not extra_fieldsets and auto_fieldsets:
        handled_fields = [ x
            for name, k in aristotle_admin.ConceptAdmin.fieldsets
                for x in k.get('fields',[]) ]

        auto_fieldset = [f.name for f in concept_class._meta.fields if f.name not in handled_fields]

        extra_fieldsets_name = None
        if auto_fieldsets_name:
            extra_fieldsets_name = concept_class._meta.verbose_name.title()

        extra_fieldsets = [(extra_fieldsets_name, {'fields': auto_fieldset}),]

    class SubclassedConceptAdmin(aristotle_admin.ConceptAdmin):
        model = concept_class
        fieldsets = aristotle_admin.ConceptAdmin.fieldsets + extra_fieldsets
        inlines = aristotle_admin.ConceptAdmin.inlines + extra_inlines

    admin.site.register(concept_class,SubclassedConceptAdmin)

#def _register_concept_(concept_class, *args, **kwargs):
#    pass

