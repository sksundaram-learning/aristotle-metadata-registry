# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('aristotle_mdr', '0011_update_ckeditor_remove_d19_errors'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReviewRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('message', models.TextField(help_text='An optional message accompanying a request', null=True, blank=True)),
                ('response', models.TextField(help_text='An optional message responding to a request', null=True, blank=True)),
                ('status', models.IntegerField(default=0, help_text='Status of a review', choices=[(0, 'Submitted'), (5, 'Cancelled'), (10, 'Accepted'), (15, 'Rejected')])),
                ('state', models.IntegerField(blank=True, help_text='The state at which a user wishes a metadata item to be endorsed', null=True, choices=[(0, 'Not Progressed'), (1, 'Incomplete'), (2, 'Candidate'), (3, 'Recorded'), (4, 'Qualified'), (5, 'Standard'), (6, 'Preferred Standard'), (7, 'Superseded'), (8, 'Retired')])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='_concept',
            name='readyToReview',
        ),
        migrations.RemoveField(
            model_name='workgroup',
            name='ownership',
        ),
        migrations.RemoveField(
            model_name='workgroup',
            name='registrationAuthorities',
        ),
        migrations.AddField(
            model_name='_concept',
            name='submitter',
            field=models.ForeignKey(related_name='created_items', blank=True, to=settings.AUTH_USER_MODEL, help_text='This is the person who first created an item. Users can always see items they made.', null=True),
        ),
        migrations.AlterField(
            model_name='_concept',
            name='workgroup',
            field=models.ForeignKey(related_name='items', blank=True, to='aristotle_mdr.Workgroup', null=True),
        ),
        migrations.AddField(
            model_name='reviewrequest',
            name='concepts',
            field=models.ManyToManyField(related_name='review_requests', to='aristotle_mdr._concept'),
        ),
        migrations.AddField(
            model_name='reviewrequest',
            name='registration_authority',
            field=models.ForeignKey(help_text='The registration authority the requester wishes to endorse the metadata item', to='aristotle_mdr.RegistrationAuthority'),
        ),
        migrations.AddField(
            model_name='reviewrequest',
            name='requester',
            field=models.ForeignKey(related_name='requested_reviews', to=settings.AUTH_USER_MODEL, help_text='The user requesting a review'),
        ),
        migrations.AddField(
            model_name='reviewrequest',
            name='reviewer',
            field=models.ForeignKey(related_name='reviewed_requests', to=settings.AUTH_USER_MODEL, help_text='The user performing a review', null=True),
        ),
    ]
