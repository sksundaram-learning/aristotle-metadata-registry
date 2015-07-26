# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aristotle_mdr', '0006_remove_status_indictionary'),
    ]

    operations = [
        migrations.RenameField(
            model_name='_concept',
            old_name='description',
            new_name='definition',
        ),
        migrations.RenameField(
            model_name='Measure',
            old_name='description',
            new_name='definition',
        ),
        migrations.RenameField(
            model_name='RegistrationAuthority',
            old_name='description',
            new_name='definition',
        ),
        migrations.RenameField(
            model_name='Workgroup',
            old_name='description',
            new_name='definition',
        ),
        migrations.RenameField(
            model_name='ConceptualDomain',
            old_name='value_description',
            new_name='description',
        ),
        migrations.RenameField(
            model_name='ValueDomain',
            old_name='value_description',
            new_name='description',
        ),
    ]
