from django.db.models.signals import post_save, post_delete, pre_delete
from reversion.signals import post_revision_commit
import haystack.signals as signals  # .RealtimeSignalProcessor as RealtimeSignalProcessor
# Don't import aristotle_mdr.models directly, only pull in whats required,
#  otherwise Haystack gets into a circular dependancy.

# class AristotleSignalProcessor(signals.BaseSignalProcessor):
# Replace below with this when doing a dataload (shuts off Haystack)
#    pass


class AristotleSignalProcessor(signals.BaseSignalProcessor):
    def setup(self):
        from aristotle_mdr.models import _concept, Workgroup
        # post_save.connect(self.handle_concept_save, sender=_concept)
        post_revision_commit.connect(self.handle_concept_revision)
        pre_delete.connect(self.handle_concept_delete, sender=_concept)
        super(AristotleSignalProcessor, self).setup()

    def teardown(self):  # pragma: no cover
        from aristotle_mdr.models import _concept
        # post_save.disconnect(self.handle_concept_save, sender=_concept)
        post_revision_commit.disconnect(self.handle_concept_revision)
        pre_delete.disconnect(self.handle_concept_delete, sender=_concept)
        super(AristotleSignalProcessor, self).teardown()

    def handle_concept_revision(self, instances, **kwargs):
        from aristotle_mdr.models import _concept
        for instance in instances:
            if isinstance(instance, _concept) and type(instance) is not _concept:
                self.handle_save(instance.__class__, instance)

    """
    # Keeping this just in case, but its unlikely to be used again after the
    transition to post_revision_commit signals.
    Safe to delete after 2016-07-01
    def handle_concept_save(self, sender, instance, **kwargs):
        obj = instance.item
        self.handle_save(obj.__class__,obj, **kwargs)
    """
    def handle_concept_delete(self, sender, instance, **kwargs):
        # Delete index *before* the object, as we need to query it to check the actual subclass.
        obj = instance.item
        self.handle_delete(obj.__class__, obj, **kwargs)
