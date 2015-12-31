import autocomplete_light

from django import forms
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone

import aristotle_mdr.models as MDR
from aristotle_mdr.forms import ChangeStatusForm
from aristotle_mdr.perms import user_can_view


class BulkActionForm(forms.Form):
    confirm_page = None
    items = forms.ModelMultipleChoiceField(
                queryset=MDR._concept.objects.all(),
                label="Related items",required=False,
                )
    def __init__(self, *args, **kwargs):
        if 'user' in kwargs.keys():
            self.user = kwargs.pop('user', None)
        super(BulkActionForm, self).__init__(*args, **kwargs)

class AddFavouriteForm(BulkActionForm):
    def make_changes(self):
        items = self.cleaned_data.get('items')
        items = [i for i in items if user_can_view(self.user,i)]
        self.user.profile.favourites.add(*items)
        return '%d items favourited'%(len(items))

class RemoveFavouriteForm(BulkActionForm):
    def make_changes(self):
        items = self.cleaned_data.get('items')
        self.user.profile.favourites.remove(*items)
        return '%d items removed from favourites'%(len(items))

class ChangeStateForm(ChangeStatusForm):
    confirm_page = "aristotle_mdr/actions/bulk_change_status.html"

    def __init__(self, *args, **kwargs):
        initial_items = kwargs.pop('items')
        super(ChangeStateForm, self).__init__(*args, **kwargs)
        self.fields['items']=forms.ModelMultipleChoiceField(
            label="These are the items that will be be registered. Add or remove additional items with the autocomplete box.",
            queryset=MDR._concept.objects.all(),
            initial = initial_items,
            widget=autocomplete_light.MultipleChoiceWidget('Autocomplete_concept')
        )
        self.add_registration_authority_field()

    def make_changes(self):
        import reversions
        if not self.user.profile.is_registrar:
            raise PermissionDenied
        ras = self.cleaned_data['registrationAuthorities']
        state = self.cleaned_data['state']
        items = self.cleaned_data['items']
        regDate = self.cleaned_data['registrationDate']
        cascade = self.cleaned_data['cascadeRegistration']
        changeDetails = self.cleaned_data['changeDetails']
        with transaction.atomic(), reversion.revisions.create_revision():
            reversion.revisions.set_user(request.user)

            if regDate is None:
                regDate = timezone.now().date()
            for item in items:
                for ra in ras:
                    ra.register(item,state,self.user,regDate,cascade,changeDetails)
            message = '%d items registered in %d registration authorities'%(len(items),len(ras))
            reversion.revisions.set_comment(message)
            return message
