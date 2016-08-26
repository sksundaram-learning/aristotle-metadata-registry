# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from aristotle_mdr.utils.migrations import ConceptMigration

class Migration(ConceptMigration):
    dependencies = [
        ('aristotle_mdr', '0013_concept_field_fixer_part1'),
    ]
    models_to_fix = [
        'conceptualdomain', 'dataelement', 'dataelementconcept',
        'dataelementderivation', 'datatype', 'objectclass',
        'property', 'unitofmeasure', 'valuedomain'
    ]
