import autocomplete_light

from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy as _

import aristotle_mdr.models as MDR
from aristotle_mdr.forms.creation_wizards import UserAwareModelForm


class RequestReviewForm(UserAwareModelForm):
    class Meta:
        model = MDR.ReviewRequest
        fields = ['state', 'registration_authority', 'message']
