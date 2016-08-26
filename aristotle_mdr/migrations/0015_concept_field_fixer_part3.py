# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from aristotle_mdr.utils.migrations import ConceptMigrationRenameConceptFields

class Migration(ConceptMigrationRenameConceptFields):
    dependencies = [
        ('aristotle_mdr', '0014_concept_field_fixer_part2'),
    ]
