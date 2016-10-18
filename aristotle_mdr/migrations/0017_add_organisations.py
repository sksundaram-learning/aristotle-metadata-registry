# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings
import model_utils.fields
import ckeditor_uploader.fields
from django.db.migrations.operations.base import Operation

class CopyFieldsBetweenTables(Operation):

    reversible = False

    def __init__(self, model_from_name, model_to_name, columns):
        self.model_from_name = model_from_name
        self.model_to_name = model_to_name
        self.columns = columns

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        columns = ", ".join(self.columns)
        base_query = """
            INSERT INTO %s_%s
            (%s)
            SELECT %s
            FROM %s_%s;
        """ % tuple(
            [app_label, self.model_to_name, columns, columns, app_label, self.model_from_name]
        )
        schema_editor.execute(base_query)

    def describe(self):
        return "Copies between two tables for %s" % self.name


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('aristotle_mdr', '0016_auto_20160919_1939'),
    ]

    state_operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('name', models.TextField(help_text='The primary name used for human identification purposes.')),
                ('definition', ckeditor_uploader.fields.RichTextUploadingField(help_text='Representation of a concept by a descriptive statement which serves to differentiate it from related concepts. (3.2.39)', verbose_name='definition')),
                ('uri', models.URLField(help_text='uri for Organization', null=True, blank=True)),
                ('managers', models.ManyToManyField(related_name='organization_manager_in', verbose_name='Managers', to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        CopyFieldsBetweenTables(
            model_from_name='registrationauthority',
            model_to_name='organization',
            columns=['created', 'definition', 'id', 'modified', 'name' ],
        ),
        migrations.RemoveField(
            model_name='registrationauthority',
            name='created',
        ),
        migrations.RemoveField(
            model_name='registrationauthority',
            name='definition',
        ),
        migrations.RemoveField(
            model_name='registrationauthority',
            name='managers',
        ),
        migrations.RemoveField(
            model_name='registrationauthority',
            name='modified',
        ),
        migrations.RemoveField(
            model_name='registrationauthority',
            name='name',
        ),

        migrations.RenameField(
            model_name='registrationauthority',
            old_name='id',
            new_name='organization_ptr'
        ),

        migrations.AlterField(
            model_name='registrationauthority',
            name='organization_ptr',
            field=models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='aristotle_mdr.Organization'),
            preserve_default=False,
        ),

    ]

    database_operations = state_operations + [

        # This is a fake model to capture the M2M
        migrations.CreateModel(
            name='registrationauthority_registrars_temp',
            fields=[
                ('registrationauthority_id', models.IntegerField()),
                ('user_id', models.IntegerField()),
            ]
        ),
        
        # Fix registrars
        CopyFieldsBetweenTables(
            model_from_name='registrationauthority_registrars',
            model_to_name='registrationauthority_registrars_temp',
            columns=['registrationauthority_id', 'user_id'],
        ),

        migrations.RemoveField(
            model_name='registrationauthority',
            name='registrars',
        ),
        
        migrations.AddField(
            model_name='registrationauthority',
            name='registrars',
            field=models.ManyToManyField(related_name='registrar_in', to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True
        ),
        CopyFieldsBetweenTables(
            model_from_name='registrationauthority_registrars_temp',
            model_to_name='registrationauthority_registrars',
            columns=['registrationauthority_id', 'user_id'],
        ),

        migrations.DeleteModel('registrationauthority_registrars_temp'),

        # Fix status and review request fields
        migrations.AlterField(
            model_name='status',
            name='registrationAuthority',
            field=models.ForeignKey(to='aristotle_mdr.RegistrationAuthority'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='reviewrequest',
            name='registration_authority',
            field=models.ForeignKey(to='aristotle_mdr.RegistrationAuthority'),
            preserve_default=True,
        ),

    ]


    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=database_operations,
            state_operations=state_operations)
    ]
