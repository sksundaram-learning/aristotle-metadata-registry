from aristotle_mdr.tests.settings.settings import *

CHANNEL_LAYERS = None

# Use an async signal processor during migration
HAYSTACK_SIGNAL_PROCESSOR = 'aristotle_mdr.contrib.help.signals.AristotleHelpSignalProcessor'
