import autocomplete_light

from django import forms
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

import aristotle_mdr.models as MDR
from aristotle_mdr.forms import ChangeStatusForm
from aristotle_mdr.perms import user_can_view, user_is_registrar
from aristotle_mdr.forms.creation_wizards import UserAwareForm

class BulkActionForm(UserAwareForm):
    classes=""
    confirm_page = None
    items = forms.ModelMultipleChoiceField(
                # queryset is all as we try to be nice and process what we can
                # in bulk actions.
                queryset=MDR._concept.objects.all(),
                label="Related items",required=False,
                )
    item_label="Select some items"
    
    def __init__(self, *args, **kwargs):
        initial_items = kwargs.pop('items',[])
        super(BulkActionForm, self).__init__(*args, **kwargs)
        #if 'user' in kwargs.keys():
        #    self.user = kwargs.pop('user', None)
            #queryset = MDR._concept.objects.visible(self.user)
        #else:
            #queryset = MDR._concept.objects.public()

        #self.fields['items']=forms.ModelMultipleChoiceField(
        #    label = self.item_label,
        #    queryset = queryset,
        #    initial = initial_items,
        #    widget=autocomplete_light.MultipleChoiceWidget('Autocomplete_concept')
        #)

    @classmethod
    def can_use(cls,user):
        return True

    @classmethod
    def text(cls):
        if hasattr(cls,'action_text'):
            return cls.action_text
        from django.utils.text import camel_case_to_spaces
        txt = cls.__name__
        txt = txt.replace('Form','')
        txt = camel_case_to_spaces(txt)
        return txt

class AddFavouriteForm(BulkActionForm):
    classes="fa-bookmark"
    action_text = _('Add bookmark')
    def make_changes(self):
        items = self.cleaned_data.get('items')
        bad_items = [str(i.id) for i in items if not user_can_view(self.user,i)]
        items = items.visible(self.user)
        self.user.profile.favourites.add(*items)
        return _("%(num_items)s items favourited. \n"
                 "Some items failed, they had the id's: %(bad_ids)s")%{
                        'num_items':len(items),'bad_ids':",".join(bad_items)}

class RemoveFavouriteForm(BulkActionForm):
    classes="fa-minus-square"
    action_text = _('Remove bookmark')
    def make_changes(self):
        items = self.cleaned_data.get('items')
        self.user.profile.favourites.remove(*items)
        return _('%(num_items)s items removed from favourites')%{'num_items':len(items)}

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
        failed = []
        success = []
        with transaction.atomic(), reversion.revisions.create_revision():
            reversion.revisions.set_user(self.user)

            if regDate is None:
                regDate = timezone.now().date()
            for item in items:
                for ra in ras:
                    r = ra.register(item,state,self.user,regDate,cascade,changeDetails)
                    for f in r['failed']:
                        failed.append(f)
                    for s in r['success']:
                        success.append(s)
            failed = list(set(failed))
            success = list(set(success))
            bad_items = sorted([str(i.id) for i in failed])
            message = _("%(num_items)s items registered in %(num_ra)s registration authorities. \n"
                        "Some items failed, they had the id's: %(bad_ids)s"
                        )%{ 'num_items':len(items),
                            'num_ra':len(ras),
                            'bad_ids':",".join(bad_items)
                        }
            reversion.revisions.set_comment(message)
            return message

    @classmethod
    def can_use(cls,user):
        return user_is_registrar(user)
