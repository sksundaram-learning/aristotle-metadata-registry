import re
from aristotle_mdr.views.bulk_actions import get_bulk_actions


# This allows us to pass the Aristotle settings through to the final rendered page
def settings(request):
    from django.conf import settings
    from aristotle_mdr.models import WORKGROUP_OWNERSHIP

    config = getattr(settings, 'ARISTOTLE_SETTINGS', {})

    return {
        "config": config,
        'bulk_actions': get_bulk_actions(),
        'workgroup_ownership': WORKGROUP_OWNERSHIP
    }
