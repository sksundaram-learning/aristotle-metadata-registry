# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from aristotle_mdr.utils.migrations import ConceptMigrationRenameConceptFields

class Migration(ConceptMigrationRenameConceptFields):
    dependencies = [
        ('aristotle_mdr', '0014_concept_field_fixer_part2'),
        ('aristotle_dse', '0012_fix_concept_fields'),
        ('aristotle_glossary', '0003_fix_concept_fields'),
        ('comet', '0008_fix_concept_fields'),
        ('mallard_qr', '0005_fix_concept_fields'),
    ]
