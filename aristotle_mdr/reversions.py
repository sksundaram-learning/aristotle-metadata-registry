from reversion.models import has_int_pk
from reversion_compare.admin import CompareVersionAdmin,CompareObjects, CompareObject
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string
class ReverseCompareObject(CompareObject):
    def __eq__(self, other):
        if hasattr(self.field,'get_internal_type'):
            assert self.field.get_internal_type() != "ManyToManyField"

        if self.value != other.value:
            return False

        if not hasattr(self.field,'get_internal_type') or self.field.get_internal_type() == "ForeignKey":  # FIXME!
            if self.version.field_dict != other.version.field_dict:
                return False

        return True
    def get_related(self):
        if hasattr(self.field,'rel') and self.field.rel is not None:
            obj = self.version.object_version.object
            if hasattr(obj, self.field.name):
                related = getattr(obj, self.field.name)
                return related

    def get_reverse_related(self):
        obj = self.version.object_version.object
        #self = getattr(obj, self.field.related_name) #self.field.field_name
        if self.has_int_pk and self.field.related_name and hasattr(obj, self.field.related_name):
            ids = [v.id for v in getattr(obj, str(self.field.related_name)).all()]  # is: version.field_dict[field.name]
        else:
            return (None,None,None)

        # get instance of reversion.models.Revision():
        # A group of related object versions.
        old_revision = self.version.revision

        # Get the related model of the current field:
        related_model = self.field.field.model #self.field.to

        # Get a queryset with all related objects.
        queryset = old_revision.version_set.filter(
            content_type=ContentType.objects.get_for_model(related_model),
            object_id__in=ids
        )

        versions = sorted(list(queryset))

        if self.has_int_pk:
            # The primary_keys would be stored in a text field -> convert
            # it to integers
            # This is interesting in different places!
            for version in versions:
                version.object_id = int(version.object_id)

        missing_objects = []
        missing_ids = []

        if self.field_name not in self.adapter.follow:
            # This models was not registered with follow relations
            # Try to fill missing related objects
            target_ids = set(ids)
            actual_ids = set([version.object_id for version in versions])
            missing_ids1 = target_ids.difference(actual_ids)
            # logger.debug(self.field_name, "target: %s - actual: %s - missing: %s" % (target_ids, actual_ids, missing_ids1))
            if missing_ids1:
                missing_objects = related_model.objects.all().filter(pk__in=missing_ids1)
                missing_ids = list(target_ids.difference(set(missing_objects.values_list('pk', flat=True))))

        return versions, missing_objects, missing_ids


class ReverseCompareObjects(CompareObjects):
    def __init__(self, field, field_name, obj, version1, version2, manager):
        self.field = field
        self.field_name = field_name
        self.obj = obj

        model = self.obj.__class__
        self.has_int_pk = has_int_pk(model)
        self.adapter = manager.get_adapter(model) # VersionAdapter instance

        # is a related field (ForeignKey, ManyToManyField etc.)
        try:
            self.is_related = self.field.rel is not None
        except:
            # is a reverse relationship
            self.is_related = False

        if not self.is_related:
            self.follow = None
        elif self.field_name in self.adapter.follow:
            self.follow = True
        else:
            self.follow = False

        self.compare_obj1 = ReverseCompareObject(field, field_name, obj, version1, self.has_int_pk, self.adapter)
        self.compare_obj2 = ReverseCompareObject(field, field_name, obj, version2, self.has_int_pk, self.adapter)

        self.value1 = self.compare_obj1.value
        self.value2 = self.compare_obj2.value
    def changed(self):
        """ return True if at least one field has changed values. """

        if hasattr(self.field,'get_internal_type') and self.field.get_internal_type() == "ManyToManyField":  # FIXME!
            info = self.get_m2m_change_info()
            keys = (
                "changed_items", "removed_items", "added_items",
                "removed_missing_objects", "added_missing_objects"
            )
            for key in keys:
                if info[key]:
                    return True
            return False

        return self.compare_obj1 != self.compare_obj2

    def get_reverse_related(self):
        return self._get_both_results("get_reverse_related")

    RFK_CHANGE_INFO = None

    def get_rfk_change_info(self):
        if self.RFK_CHANGE_INFO is not None:
            return self.RFK_CHANGE_INFO

        m2m_data1, m2m_data2 = self.get_reverse_related()


        result1, missing_objects1, missing_ids1 = m2m_data1
        result2, missing_objects2, missing_ids2 = m2m_data2
        if result1 is None:
            return {}

#        missing_objects_pk1 = [obj.pk for obj in missing_objects1]
#        missing_objects_pk2 = [obj.pk for obj in missing_objects2]
        missing_objects_dict2 = dict([(obj.pk, obj) for obj in missing_objects2])

        # logger.debug("missing_objects1: %s", missing_objects1)
        # logger.debug("missing_objects2: %s", missing_objects2)
        # logger.debug("missing_ids1: %s", missing_ids1)
        # logger.debug("missing_ids2: %s", missing_ids2)

        missing_object_set1 = set(missing_objects1)
        missing_object_set2 = set(missing_objects2)
        # logger.debug("%s %s", missing_object_set1, missing_object_set2)

        same_missing_objects = missing_object_set1.intersection(missing_object_set2)
        removed_missing_objects = missing_object_set1.difference(missing_object_set2)
        added_missing_objects = missing_object_set2.difference(missing_object_set1)

        # logger.debug("same_missing_objects: %s", same_missing_objects)
        # logger.debug("removed_missing_objects: %s", removed_missing_objects)
        # logger.debug("added_missing_objects: %s", added_missing_objects)


        # Create same_items, removed_items, added_items with related m2m items

        changed_items = []
        removed_items = []
        added_items = []
        same_items = []

        primary_keys1 = [version.object_id for version in result1]
        primary_keys2 = [version.object_id for version in result2]

        result_dict1 = dict([(version.object_id, version) for version in result1])
        result_dict2 = dict([(version.object_id, version) for version in result2])

        for primary_key in set(primary_keys1).union(set(primary_keys2)):
            if primary_key in result_dict1:
                version1 = result_dict1[primary_key]
            else:
                version1 = None

            if primary_key in result_dict2:
                version2 = result_dict2[primary_key]
            else:
                version2 = None


            if version1 is not None and version2 is not None:
                # In both -> version changed or the same
                if version1.serialized_data == version2.serialized_data:
                    same_items.append(version1)
                else:
                    changed_items.append((version1, version2))
            elif version1 is not None and version2 is None:
                # In 1 but not in 2 -> removed
                if primary_key in missing_objects_dict2:
                    missing_object = missing_objects_dict2[primary_key]
                    added_missing_objects.remove(missing_object)
                    same_missing_objects.add(missing_object)
                    continue

                removed_items.append(version1)
            elif version1 is None and version2 is not None:
                # In 2 but not in 1 -> added
                added_items.append(version2)
            else:
                raise RuntimeError()

        self.RFK_CHANGE_INFO = {
            "changed_items": changed_items,
            "removed_items": removed_items,
            "added_items": added_items,
            "same_items": same_items,
            "same_missing_objects": same_missing_objects,
            "removed_missing_objects": removed_missing_objects,
            "added_missing_objects": added_missing_objects,
        }
        return self.RFK_CHANGE_INFO


class ConceptCompareVersionAdmin(CompareVersionAdmin):
    """
    expand the base class with prepered compare methods.
    """
    def compare(self, obj, version1, version2):
        diff = []

        # Create a list of all normal fields and append many-to-many fields
        fields = [field for field in obj._meta.fields]
        concrete_model = obj._meta.concrete_model
        fields += concrete_model._meta.many_to_many

        from django.db import models
        self.extraFields = []
        for field_name in obj._meta.get_all_field_names() :
            f = getattr(
                    obj._meta.get_field_by_name(field_name)[0],
                    'field',
                    None
                )
            if isinstance(f, models.ForeignKey) and f not in fields:
                self.extraFields.append(f.rel)

        fields += self.extraFields

        has_unfollowed_fields = False
        for field in fields:
            try:
                field_name = field.name
            except:
                field_name = field.field_name

            if self.compare_fields and field_name not in self.compare_fields:
                continue
            if self.compare_exclude and field_name in self.compare_exclude:
                continue

            obj_compare = ReverseCompareObjects(field, field_name, obj, version1, version2, self.revision_manager)

            is_related = obj_compare.is_related
            follow = obj_compare.follow
            if is_related and not follow:
                has_unfollowed_fields = True

            if not obj_compare.changed():
                # Skip all fields that aren't changed
                continue
            try:
                html = self._get_compare(obj_compare)
            except:
                if field_name != 'workgroup':
                    html = self._get_compare(obj_compare)
                print obj_compare
                html = ""

            diff.append({
                "field": field,
                "is_related": is_related,
                "follow": follow,
                "diff": html,
            })
        return diff, has_unfollowed_fields

    def _get_compare(self, obj_compare):
        """
        Call the methods to create the compare html part.
        Try:
            1. name scheme: "compare_%s" % field_name
            2. name scheme: "compare_%s" % field.get_internal_type()
            3. Fallback to: self.fallback_compare()
        """
        def _get_compare_func(suffix):
            func_name = "compare_%s" % suffix
            # logger.debug("func_name: %s", func_name)
            if hasattr(self, func_name):
                func = getattr(self, func_name)
                return func

        # Try method in the name scheme: "compare_%s" % field_name
        func = _get_compare_func(obj_compare.field_name)
        if func is not None:
            html = func(obj_compare)
            return html

        if not hasattr(obj_compare.field,'get_internal_type') and obj_compare.field in self.extraFields:
            func = _get_compare_func("ManyToOneRel")
            if func is not None:
                html = func(obj_compare)
                return html

        # Try method in the name scheme: "compare_%s" % field.get_internal_type()
        internal_type = obj_compare.field.get_internal_type()
        func = _get_compare_func(internal_type)
        if func is not None:
            html = func(obj_compare)
            return html

        # Fallback to self.fallback_compare()
        html = self.fallback_compare(obj_compare)
        return html

    def compare_ManyToOneRel(self, obj_compare):
        change_info = obj_compare.get_rfk_change_info()
        context = {"change_info": change_info}
        return render_to_string("reversion-compare/compare_generic_many_to_many.html", context)
