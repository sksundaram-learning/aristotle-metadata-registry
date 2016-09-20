# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ckeditor_uploader.fields


class Migration(migrations.Migration):

    dependencies = [
        ('aristotle_mdr', '0015_concept_field_fixer_part3'),
    ]

    operations = [
        migrations.AlterField(
            model_name='_concept',
            name='comments',
            field=ckeditor_uploader.fields.RichTextUploadingField(help_text='Descriptive comments about the metadata item (8.1.2.2.3.4)', blank=True),
        ),
        migrations.AlterField(
            model_name='_concept',
            name='definition',
            field=ckeditor_uploader.fields.RichTextUploadingField(help_text='Representation of a concept by a descriptive statement which serves to differentiate it from related concepts. (3.2.39)', verbose_name='definition'),
        ),
        migrations.AlterField(
            model_name='dataelement',
            name='dataElementConcept',
            field=models.ForeignKey(blank=True, to='aristotle_mdr.DataElementConcept', help_text='binds with a Value_Domain that describes a set of possible values that may be recorded in an instance of the Data_Element', null=True, verbose_name='Data Element Concept'),
        ),
        migrations.AlterField(
            model_name='dataelement',
            name='valueDomain',
            field=models.ForeignKey(blank=True, to='aristotle_mdr.ValueDomain', help_text='binds with a Data_Element_Concept that provides the meaning for the Data_Element', null=True, verbose_name='Value Domain'),
        ),
        migrations.AlterField(
            model_name='dataelementconcept',
            name='conceptualDomain',
            field=models.ForeignKey(blank=True, to='aristotle_mdr.ConceptualDomain', help_text='references a Conceptual_Domain that is part of the specification of the Data_Element_Concept', null=True),
        ),
        migrations.AlterField(
            model_name='dataelementconcept',
            name='objectClass',
            field=models.ForeignKey(blank=True, to='aristotle_mdr.ObjectClass', help_text='references an Object_Class that is part of the specification of the Data_Element_Concept', null=True),
        ),
        migrations.AlterField(
            model_name='dataelementconcept',
            name='property',
            field=models.ForeignKey(blank=True, to='aristotle_mdr.Property', help_text='references a Property that is part of the specification of the Data_Element_Concept', null=True),
        ),
        migrations.AlterField(
            model_name='dataelementderivation',
            name='derivation_rule',
            field=models.TextField(help_text='text of a specification of a data element Derivation_Rule', blank=True),
        ),
        migrations.AlterField(
            model_name='dataelementderivation',
            name='derives',
            field=models.ForeignKey(related_name='derived_from', blank=True, to='aristotle_mdr.DataElement', help_text='binds with one or more output Data_Elements that are the result of the application of the Data_Element_Derivation.', null=True),
        ),
        migrations.AlterField(
            model_name='dataelementderivation',
            name='inputs',
            field=models.ManyToManyField(help_text='binds one or more input Data_Element(s) with a Data_Element_Derivation.', related_name='input_to_derivation', to='aristotle_mdr.DataElement', blank=True),
        ),
        migrations.AlterField(
            model_name='measure',
            name='definition',
            field=ckeditor_uploader.fields.RichTextUploadingField(help_text='Representation of a concept by a descriptive statement which serves to differentiate it from related concepts. (3.2.39)', verbose_name='definition'),
        ),
        migrations.AlterField(
            model_name='permissiblevalue',
            name='meaning',
            field=models.CharField(help_text="A textual designation of a value, where a relation to a Value meaning doesn't exist", max_length=255),
        ),
        migrations.AlterField(
            model_name='permissiblevalue',
            name='value',
            field=models.CharField(help_text='the actual value of the Value', max_length=32),
        ),
        migrations.AlterField(
            model_name='permissiblevalue',
            name='valueDomain',
            field=models.ForeignKey(related_name='permissiblevalue_set', to='aristotle_mdr.ValueDomain', help_text='Enumerated Value Domain that this value meaning relates to'),
        ),
        migrations.AlterField(
            model_name='permissiblevalue',
            name='value_meaning',
            field=models.ForeignKey(blank=True, to='aristotle_mdr.ValueMeaning', help_text='A reference to the value meaning that this designation relates to', null=True),
        ),
        migrations.AlterField(
            model_name='registrationauthority',
            name='definition',
            field=ckeditor_uploader.fields.RichTextUploadingField(help_text='Representation of a concept by a descriptive statement which serves to differentiate it from related concepts. (3.2.39)', verbose_name='definition'),
        ),
        migrations.AlterField(
            model_name='status',
            name='registrationDate',
            field=models.DateField(help_text='date and time an Administered_Item became/becomes available to registry users', verbose_name='Date registration effective'),
        ),
        migrations.AlterField(
            model_name='status',
            name='state',
            field=models.IntegerField(default=1, help_text='Designation (3.2.51) of the status in the registration life-cycle of an Administered_Item', choices=[(0, 'Not Progressed'), (1, 'Incomplete'), (2, 'Candidate'), (3, 'Recorded'), (4, 'Qualified'), (5, 'Standard'), (6, 'Preferred Standard'), (7, 'Superseded'), (8, 'Retired')]),
        ),
        migrations.AlterField(
            model_name='status',
            name='until_date',
            field=models.DateField(help_text='date and time the Registration of an Administered_Item by a Registration_Authority in a registry is no longer effective', null=True, verbose_name='Date registration expires', blank=True),
        ),
        migrations.AlterField(
            model_name='supplementaryvalue',
            name='meaning',
            field=models.CharField(help_text="A textual designation of a value, where a relation to a Value meaning doesn't exist", max_length=255),
        ),
        migrations.AlterField(
            model_name='supplementaryvalue',
            name='value',
            field=models.CharField(help_text='the actual value of the Value', max_length=32),
        ),
        migrations.AlterField(
            model_name='supplementaryvalue',
            name='valueDomain',
            field=models.ForeignKey(related_name='supplementaryvalue_set', to='aristotle_mdr.ValueDomain', help_text='Enumerated Value Domain that this value meaning relates to'),
        ),
        migrations.AlterField(
            model_name='supplementaryvalue',
            name='value_meaning',
            field=models.ForeignKey(blank=True, to='aristotle_mdr.ValueMeaning', help_text='A reference to the value meaning that this designation relates to', null=True),
        ),
        migrations.AlterField(
            model_name='valuedomain',
            name='conceptual_domain',
            field=models.ForeignKey(blank=True, to='aristotle_mdr.ConceptualDomain', help_text='The Conceptual Domain that this Value Domain which provides representation.', null=True),
        ),
        migrations.AlterField(
            model_name='valuedomain',
            name='data_type',
            field=models.ForeignKey(blank=True, to='aristotle_mdr.DataType', help_text='Datatype used in a Value Domain', null=True),
        ),
        migrations.AlterField(
            model_name='valuedomain',
            name='format',
            field=models.CharField(help_text='template for the structure of the presentation of the value(s)', max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='valuedomain',
            name='maximum_length',
            field=models.PositiveIntegerField(help_text='maximum number of characters available to represent the Data Element value', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='valuedomain',
            name='unit_of_measure',
            field=models.ForeignKey(blank=True, to='aristotle_mdr.UnitOfMeasure', help_text='Unit of Measure used in a Value Domain', null=True),
        ),
        migrations.AlterField(
            model_name='valuemeaning',
            name='meaning',
            field=models.CharField(help_text='The semantic content of a possible value (3.2.141)', max_length=255),
        ),
        migrations.AlterField(
            model_name='workgroup',
            name='definition',
            field=ckeditor_uploader.fields.RichTextUploadingField(help_text='Representation of a concept by a descriptive statement which serves to differentiate it from related concepts. (3.2.39)', verbose_name='definition'),
        ),
    ]
