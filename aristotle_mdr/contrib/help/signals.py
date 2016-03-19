from django.db.models.signals import post_save, post_delete, pre_delete
# from reversion.signals import post_revision_commit
import haystack.signals as signals  # .RealtimeSignalProcessor as RealtimeSignalProcessor
# Don't import aristotle_mdr.models directly, only pull in whats required,
#  otherwise Haystack gets into a circular dependancy.


class AristotleHelpSignalProcessor(signals.BaseSignalProcessor):
    def setup(self):
        from aristotle_mdr.contrib.help.models import HelpPage, ConceptHelp
        post_save.connect(self.handle_save, sender=HelpPage)
        post_save.connect(self.handle_save, sender=ConceptHelp)
        # post_revision_commit.connect(self.handle_save, sender=HelpPage)
        super(AristotleHelpSignalProcessor, self).setup()
