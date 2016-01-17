# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aristotle_mdr', '0007_rename_description_fields'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='discussioncomment',
            options={'ordering': ['created']},
        ),
    ]
