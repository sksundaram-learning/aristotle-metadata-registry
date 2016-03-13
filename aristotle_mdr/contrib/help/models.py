from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.conf.global_settings import LANGUAGES
from aristotle_mdr.models import RichTextField


# class Help(models.Model):
#    pass


class ConceptHelp(models.Model):
    app_label = models.CharField(max_length=256)
    concept_type = models.CharField(max_length=256)
    language = models.CharField(
        max_length=7, choices=LANGUAGES
    )
    brief = models.TextField(
        help_text=_("A short description of the concept")
    )
    offical_definition = models.TextField(
        null=True, blank=True,
        help_text=_("An official description of the concept, e.g. the ISO/IEC definition for an Object Class")
    )
    official_reference = models.TextField(
        null=True, blank=True,
        help_text=_("The reference document that describes this concept type")
    )
    official_link = models.TextField(
        null=True, blank=True,
        help_text=_("An link to an official source for a description of the concept")
    )
    long_help = RichTextField(
        help_text=_("An longer definition for an object, including images and links")
    )
    unique_together = ("app_label", "concept_type", "languages")
