# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('aristotle_mdr', '0002_auto_20150409_0656'),
    ]

    operations = [
        migrations.AddField(
            model_name='workgroup',
            name='ownership',
            field=models.IntegerField(default=1, help_text="Specifies the 'owner' of the content of the workgroup. Selecting 'registry' allows any registration authority to progress and make items public, 'Registration authorities' specifies that only registration authorities associated with this workgroup may control their visibility.", choices=[(0, 'Registry'), (1, 'Registration Authorities')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='registrationauthority',
            name='managers',
            field=models.ManyToManyField(related_name='registrationauthority_manager_in', verbose_name='Managers', to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='registrationauthority',
            name='registrars',
            field=models.ManyToManyField(related_name='registrar_in', verbose_name='Registrars', to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='workgroup',
            name='archived',
            field=models.BooleanField(default=False, help_text='Archived workgroups can no longer have new items or discussions created within them.', verbose_name='Archived'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='workgroup',
            name='managers',
            field=models.ManyToManyField(related_name='workgroup_manager_in', verbose_name='Managers', to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='workgroup',
            name='registrationAuthorities',
            field=models.ManyToManyField(related_name='workgroups', null=True, verbose_name='Registration Authorities', to='aristotle_mdr.RegistrationAuthority', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='workgroup',
            name='stewards',
            field=models.ManyToManyField(related_name='steward_in', verbose_name='Stewards', to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='workgroup',
            name='submitters',
            field=models.ManyToManyField(related_name='submitter_in', verbose_name='Submitters', to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='workgroup',
            name='viewers',
            field=models.ManyToManyField(related_name='viewer_in', verbose_name='Viewers', to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
    ]
