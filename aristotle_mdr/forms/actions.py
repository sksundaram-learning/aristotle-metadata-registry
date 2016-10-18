from django import forms
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

import aristotle_mdr.models as MDR
from aristotle_mdr.forms.creation_wizards import UserAwareModelForm
from aristotle_mdr.forms import ChangeStatusForm


class RequestReviewForm(UserAwareModelForm):
    class Meta:
        model = MDR.ReviewRequest
        fields = ['state', 'registration_authority', 'message']


class RequestReviewCancelForm(UserAwareModelForm):
    class Meta:
        model = MDR.ReviewRequest
        fields = []


class RequestReviewRejectForm(UserAwareModelForm):
    class Meta:
        model = MDR.ReviewRequest
        fields = ['response']


class RequestReviewAcceptForm(ChangeStatusForm):
    response = forms.CharField(
        max_length=512,
        required=True,
        label=_("Reply to the original review request below."),
        widget=forms.Textarea
    )

    # TODO: This is from aristotle_mdr.bulk_actions.ChangeStateForm - See if this can share a superclass
    def make_changes(self, items):
        import reversion
        if not self.user.profile.is_registrar:
            raise PermissionDenied
        ras = self.cleaned_data['registrationAuthorities']
        state = self.cleaned_data['state']
        # items = self.items_to_change
        regDate = self.cleaned_data['registrationDate']
        cascade = self.cleaned_data['cascadeRegistration']
        changeDetails = self.cleaned_data['changeDetails']
        failed = []
        success = []
        with transaction.atomic(), reversion.revisions.create_revision():
            reversion.revisions.set_user(self.user)

            if regDate is None:
                regDate = timezone.now().date()
            for item in items:
                for ra in ras:
                    r = ra.register(item, state, self.user, regDate, cascade, changeDetails)
                    for f in r['failed']:
                        failed.append(f)
                    for s in r['success']:
                        success.append(s)
            failed = list(set(failed))
            success = list(set(success))
            bad_items = sorted([str(i.id) for i in failed])
            message = _(
                "%(num_items)s items registered in %(num_ra)s registration authorities. \n"
                "Some items failed, they had the id's: %(bad_ids)s"
            ) % {
                'num_items': len(items),
                'num_ra': len(ras),
                'bad_ids': ",".join(bad_items)
            }
            reversion.revisions.set_comment(changeDetails + "\n\n" + message)
            return message
