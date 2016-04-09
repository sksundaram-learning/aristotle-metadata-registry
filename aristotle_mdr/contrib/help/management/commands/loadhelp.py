from __future__ import unicode_literals

"""
This is literally forked from djangos own loaddata, expect it saves the
object not the serialisation.
It also uses a modified fixture finder that allows for wildcard entry
"""

import gzip
import os
import warnings
import zipfile
from itertools import product

from django.apps import apps
from django.conf import settings
from django.core import serializers
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.core.management.color import no_style
from django.db import (
    DEFAULT_DB_ALIAS, DatabaseError, IntegrityError, connections, router,
    transaction,
)
from django.forms.models import model_to_dict
from django.utils._os import upath
from django.utils.encoding import force_text
from django.utils.functional import cached_property

from django.core.management.commands.loaddata import Command as loaddata
from django.core.management.commands.loaddata import humanize

import glob
from django.utils import lru_cache


class Command(loaddata):
    help = 'Installs the named help fixture(s) in the database.'
    missing_args_message = ("No database fixture specified. Please provide the "
                            "path of at least one fixture in the command line.")

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '--update', '-U', action='store_true',
            dest='update', default=False,
            help='Updates existing helps files if they exist.'
        )

    def handle(self, *fixture_labels, **options):

        self.ignore = options.get('ignore')
        self.using = options.get('database')
        self.app_label = options.get('app_label')
        self.hide_empty = options.get('hide_empty', False)
        self.verbosity = options.get('verbosity')
        self.update = options.get('update')

        with transaction.atomic(using=self.using):
            self.loaddata(fixture_labels)

        # Close the DB connection -- unless we're still in a transaction. This
        # is required as a workaround for an  edge case in MySQL: if the same
        # connection is used to create tables, load data, and query, the query
        # can return incorrect results. See Django #7572, MySQL #37735.
        if transaction.get_autocommit(self.using):
            connections[self.using].close()

    def load_label(self, fixture_label):
        """
        Loads fixtures files for a given label.
        """
        show_progress = self.verbosity >= 3
        for fixture_file, fixture_dir, fixture_name in self.find_fixtures(fixture_label):
            _, ser_fmt, cmp_fmt = self.parse_name(os.path.basename(fixture_file))
            open_method, mode = self.compression_formats[cmp_fmt]
            fixture = open_method(fixture_file, mode)
            try:
                self.fixture_count += 1
                objects_in_fixture = 0
                loaded_objects_in_fixture = 0
                if self.verbosity >= 2:
                    self.stdout.write(
                        "Installing %s fixture '%s' from %s." %
                        (ser_fmt, fixture_name, humanize(fixture_dir))
                    )

                objects = serializers.deserialize(
                    ser_fmt, fixture,
                    using=self.using, ignorenonexistent=self.ignore
                )

                for obj in objects:
                    objects_in_fixture += 1
                    if router.allow_migrate_model(self.using, obj.object.__class__):
                        loaded_objects_in_fixture += 1
                        self.models.add(obj.object.__class__)
                        try:
                            if self.update:
                                keys = dict([
                                    (key, getattr(obj.object, key))
                                    for key in obj.object.unique_together
                                ])
                                vals = dict([
                                    (k, v)
                                    for k, v in model_to_dict(obj.object).items()
                                    if v is not None
                                    ])

                                item, created = obj.object.__class__.objects.get_or_create(
                                    defaults=vals,
                                    **keys
                                )
                                if not created:
                                    if show_progress:
                                        self.stdout.write(
                                            'Updated an object(s).',
                                            ending=''
                                        )
                                    for k, v in vals.items():
                                        setattr(item, k, v)
                                    item.save()
                            else:
                                obj.object.save()
                            if show_progress:
                                self.stdout.write(
                                    '\rProcessed %i object(s).' % loaded_objects_in_fixture,
                                    ending=''
                                )
                        except (DatabaseError, IntegrityError) as e:
                            e.args = ("Could not load %(app_label)s.%(object_name)s(pk=%(pk)s): %(error_msg)s" % {
                                'app_label': obj.object._meta.app_label,
                                'object_name': obj.object._meta.object_name,
                                'pk': obj.object.pk,
                                'error_msg': force_text(e)
                            },)
                            raise
                if objects and show_progress:
                    self.stdout.write('')  # add a newline after progress indicator
                self.loaded_object_count += loaded_objects_in_fixture
                self.fixture_object_count += objects_in_fixture
            except Exception as e:
                if not isinstance(e, CommandError):
                    e.args = ("Problem installing fixture '%s': %s" % (fixture_file, e),)
                raise
            finally:
                fixture.close()

            # Warn if the fixture we loaded contains 0 objects.
            if objects_in_fixture == 0:
                warnings.warn(
                    "No fixture data found for '%s'. (File format may be "
                    "invalid.)" % fixture_name,
                    RuntimeWarning
                )

    @lru_cache.lru_cache(maxsize=None)
    def find_fixtures(self, fixture_label):
        """
        Finds fixture files for a given label.
        """
        fixture_name, ser_fmt, cmp_fmt = self.parse_name(fixture_label)
        databases = [self.using, None]
        cmp_fmts = list(self.compression_formats.keys()) if cmp_fmt is None else [cmp_fmt]
        ser_fmts = serializers.get_public_serializer_formats() if ser_fmt is None else [ser_fmt]

        if self.verbosity >= 2:
            self.stdout.write("Loading '%s' fixtures..." % fixture_name)

        if os.path.isabs(fixture_name):
            fixture_dirs = [os.path.dirname(fixture_name)]
            fixture_name = os.path.basename(fixture_name)
        else:
            fixture_dirs = self.fixture_dirs
            if os.path.sep in os.path.normpath(fixture_name):
                fixture_dirs = [os.path.join(dir_, os.path.dirname(fixture_name))
                                for dir_ in fixture_dirs]
                fixture_name = os.path.basename(fixture_name)

        suffixes = (
            '.'.join(ext for ext in combo if ext)
            for combo in product(databases, ser_fmts, cmp_fmts)
        )

        if fixture_name == "*":
            search_name = ""
        else:
            search_name = fixture_name

        targets = set('.'.join((search_name, suffix)) for suffix in suffixes)

        fixture_files = []
        for fixture_dir in fixture_dirs:
            if self.verbosity >= 2:
                self.stdout.write("Checking %s for fixtures..." % humanize(fixture_dir))
            fixture_files_in_dir = []
            for candidate in glob.iglob(os.path.join(fixture_dir, search_name + '*')):
                if any([os.path.basename(candidate).endswith(t) for t in targets]):
                    # Save the fixture_dir and fixture_name for future error messages.
                    fixture_files_in_dir.append((candidate, fixture_dir, fixture_name))

            if self.verbosity >= 2 and not fixture_files_in_dir:
                self.stdout.write("No fixture '%s' in %s." %
                                  (fixture_name, humanize(fixture_dir)))

            # Check kept for backwards-compatibility; it isn't clear why
            # duplicates are only allowed in different directories.
            # Commented out from django
            # if len(fixture_files_in_dir) > 1:
            #    raise CommandError(
            #        "Multiple fixtures named '%s' in %s. Aborting." %
            #        (fixture_name, humanize(fixture_dir)))
            fixture_files.extend(fixture_files_in_dir)

        return fixture_files
