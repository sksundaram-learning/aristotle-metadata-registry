import autocomplete_light

from django import forms
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

import aristotle_mdr.models as MDR
from aristotle_mdr.forms import ChangeStatusForm
from aristotle_mdr.perms import (
    user_can_view,
    user_is_registrar,
    user_is_workgroup_manager,
    user_can_move_any_workgroup
)
from aristotle_mdr.forms.creation_wizards import UserAwareModelForm

class RequestReviewForm(UserAwareModelForm):
    class Meta:
        model = MDR.ReviewRequest
        #exclude = ['concepts', 'status', 'requester', 'reviewer', 'response']
        fields = ['state','registration_authority', 'message']
