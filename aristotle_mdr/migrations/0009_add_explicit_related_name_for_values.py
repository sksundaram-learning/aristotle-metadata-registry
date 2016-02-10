# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aristotle_mdr', '0008_auto_20151216_0339'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permissiblevalue',
            name='valueDomain',
            field=models.ForeignKey(related_name='permissiblevalue_set', to='aristotle_mdr.ValueDomain'),
        ),
        migrations.AlterField(
            model_name='supplementaryvalue',
            name='valueDomain',
            field=models.ForeignKey(related_name='supplementaryvalue_set', to='aristotle_mdr.ValueDomain'),
        ),
    ]
