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
    """ .. py:function:: register_concept(concept_class, *args, **kwargs)

    A handler for third-party apps to make registering
    extension models based on ``aristotle_mdr.models.concept`` easier.

    Sets up the search index, django administrator page and autocomplete handlers.
    All ``args`` and ``kwargs`` are passed to the called methods.

    Example usage (based on the models in the extensions test suite):

        register_concept(Question, extra_fieldsets=[('Question','question_text'),]

    :param concept concept_class: The model that is to be registered
    :param list extra_fieldsets: A list of additional fieldsets to be displayed
    :param list extra_inlines: A list of additional fieldsets to be displayed
    """
    register_concept_autocomplete(concept_class, *args, **kwargs)
    register_concept_admin(concept_class, *args, **kwargs)
    register_concept_search_index(concept_class, *args, **kwargs)

def register_concept_autocomplete(concept_class, *args, **kwargs):
    """ .. py:function:: register_concept_autocomplete(concept_class, *args, **kwargs)

    Registers the given ``concept`` with ``autocomplete_light`` based on the
    in-built ``aristotle_mdr.autocomplete_light_registry.PermissionsAutocomplete``.
    This ensures the autocomplete for the registered conforms to Aristotle permissions.

    :param concept concept_class: The model that is to be registered
    """
    x = reg.autocompleteTemplate.copy()
    x['name']='Autocomplete'+concept_class.__name__
    autocomplete_light.register(concept_class,reg.PermissionsAutocomplete,**x)

def register_concept_search_index(concept_class, *args, **kwargs):
    """ .. py:function:: register_concept_search_index(concept_class, *args, **kwargs)

    Registers the given ``concept`` with a Haystack search index that
    registered conforms to Aristotle permissions.

    :param concept concept_class: The model that is to be registered for searching.
    """
    class_name = "%s_%sSearchIndex"%(concept_class._meta.app_label,concept_class.__name__)
    setattr(search_index, class_name, create(concept_class))

    # Since we've added a new class, kill the index so it is rebuilt.
    connections[DEFAULT_ALIAS]._index = None

def create(cls):
    class SubclassedConceptIndex(conceptIndex, indexes.Indexable):
        def get_model(self):
            return cls
    return SubclassedConceptIndex


def register_concept_admin(concept_class, *args, **kwargs):
    """ .. py:function:: register_concept_admin(concept_class, *args, **kwargs)

    Registers the given ``concept`` with the Django admin backend based on the default
    ``aristotle_mdr.admin.ConceptAdmin``.

    Additional parameters are only required if a model has additional fields or
    references to other models.

    :param concept concept_class: The model that is to be registered
    :param list extra_fieldsets: Model-specific `fieldsets <https://docs.djangoproject.com/en/1.8/ref/contrib/admin/#django.contrib.admin.ModelAdmin.fieldsets>`_ to be displayed. Fields in the tuples given should be those *not* defined by the base ``aristotle_mdr.models._concept``class.
    :param list extra_inlines: Model-specific `inline <https://docs.djangoproject.com/en/1.8/ref/contrib/admin/#django.contrib.admin.ModelAdmin.inlines>`_ admin forms to be displayed.
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

