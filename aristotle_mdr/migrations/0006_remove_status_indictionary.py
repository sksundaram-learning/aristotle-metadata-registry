# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aristotle_mdr', '0005_auto_20150526_1058'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='status',
            name='inDictionary',
        ),
    ]
