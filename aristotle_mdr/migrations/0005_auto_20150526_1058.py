# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aristotle_mdr', '0004_auto_20150424_0059'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='package',
            name='_concept_ptr',
        ),
        migrations.RemoveField(
            model_name='package',
            name='items',
        ),
        migrations.RemoveField(
            model_name='package',
            name='superseded_by',
        ),
        migrations.DeleteModel(
            name='Package',
        ),
    ]
