import autocomplete_light

from django import forms
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

import aristotle_mdr.models as MDR
from aristotle_mdr.forms import ChangeStatusForm
from aristotle_mdr.perms import user_can_view, user_is_registrar


class BulkActionForm(forms.Form):
    classes=""
    confirm_page = None
    items = forms.ModelMultipleChoiceField(
                queryset=MDR._concept.objects.all(),
                label="Related items",required=False,
                )
    item_label="Select some items"
    
    def __init__(self, *args, **kwargs):
        if 'user' in kwargs.keys():
            self.user = kwargs.pop('user', None)
            queryset = MDR._concept.objects.visible(self.user)
        else:
            queryset = MDR._concept.objects.public()
        initial_items = kwargs.pop('items',[])

        super(BulkActionForm, self).__init__(*args, **kwargs)

        self.fields['items']=forms.ModelMultipleChoiceField(
            label = self.item_label,
            queryset = queryset,
            initial = initial_items,
            widget=autocomplete_light.MultipleChoiceWidget('Autocomplete_concept')
        )

    @classmethod
    def can_use(cls,user):
        return True

    @classmethod
    def text(cls):
        if hasattr(cls,'action_text'):
            return cls.action_text
        from django.utils.text import camel_case_to_spaces
        txt = cls.__name__
        print txt
        txt = txt.replace('Form','')
        txt = camel_case_to_spaces(txt)
        return txt

class AddFavouriteForm(BulkActionForm):
    classes="fa-bookmark"
    action_text = _('Add bookmark')
    def make_changes(self):
        items = self.cleaned_data.get('items')
        items = [i for i in items if user_can_view(self.user,i)]
        self.user.profile.favourites.add(*items)
        return '%d items favourited'%(len(items))

class RemoveFavouriteForm(BulkActionForm):
    classes="fa-minus-square"
    action_text = _('Remove bookmark')
    def make_changes(self):
        items = self.cleaned_data.get('items')
        self.user.profile.favourites.remove(*items)
        return '%d items removed from favourites'%(len(items))

class ChangeStateForm(ChangeStatusForm,BulkActionForm):
    confirm_page = "aristotle_mdr/actions/bulk_change_status.html"
    classes="fa-university"
    action_text = _('Change state')
    items_label="These are the items that will be be registered. Add or remove additional items with the autocomplete box.",
    
    def __init__(self, *args, **kwargs):
        super(ChangeStateForm, self).__init__(*args, **kwargs)
        self.add_registration_authority_field()

    def make_changes(self):
        import reversion
        if not self.user.profile.is_registrar:
            raise PermissionDenied
        ras = self.cleaned_data['registrationAuthorities']
        state = self.cleaned_data['state']
        items = self.cleaned_data['items']
        regDate = self.cleaned_data['registrationDate']
        cascade = self.cleaned_data['cascadeRegistration']
        changeDetails = self.cleaned_data['changeDetails']
        with transaction.atomic(), reversion.revisions.create_revision():
            reversion.revisions.set_user(self.user)

            if regDate is None:
                regDate = timezone.now().date()
            for item in items:
                for ra in ras:
                    ra.register(item,state,self.user,regDate,cascade,changeDetails)
            message = '%d items registered in %d registration authorities'%(len(items),len(ras))
            reversion.revisions.set_comment(message)
            return message
    
    @classmethod
    def can_use(cls,user):
        return user_is_registrar(user)
