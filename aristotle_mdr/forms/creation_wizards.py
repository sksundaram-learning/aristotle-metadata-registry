from django import forms
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

import aristotle_mdr.models as MDR
import autocomplete_light

class UserAwareForm(forms.Form):
    def __init__(self,*args,**kwargs):
        self.user = kwargs.pop('user')
        super(UserAwareForm, self).__init__(*args, **kwargs)
class UserAwareModelForm(autocomplete_light.ModelForm):
    class Meta:
        model = MDR._concept
        exclude = ['readyToReview','superseded_by','_is_public','_is_locked','originURI']

    def __init__(self,*args,**kwargs):
        self.user = kwargs.pop('user')
        super(UserAwareModelForm, self).__init__(*args, **kwargs)

    def _media(self):
        js = ('aristotle_mdr/aristotle.wizard.js','/static/tiny_mce/tiny_mce.js','/static/aristotle_mdr/aristotle.tinymce.js')
        #js = ('/static/admin/js/jquery.min.js','aristotle_mdr/aristotle.wizard.js','/static/tiny_mce/tiny_mce.js')
        media = forms.Media(js=js)
        for field in self.fields.values():
            media = media + field.widget.media
        return media
    media = property(_media)


class ConceptForm(UserAwareModelForm):
    """
    Add this in when we look at reintroducing the fancy templates.
    required_css_class = 'required'
    """
    def __init__(self, *args, **kwargs):
        #TODO: Have tis throw a 'no user' error
        first_load = kwargs.pop('first_load', None)
        super(ConceptForm, self).__init__(*args, **kwargs)
        if not self.user.is_superuser:
            self.fields['workgroup'].queryset = self.user.profile.myWorkgroups
        self.fields['name'].widget = forms.widgets.TextInput()


    def concept_fields(self):
        field_names = [field.name for field in MDR.baseAristotleObject._meta.fields]+['version','workgroup'] #version/workgroup are displayed with name/definition
        concept_field_names = [ field.name
                                for field in MDR.concept._meta.fields
                                if field.name not in field_names
                                ]
        for name in self.fields:
            if name in concept_field_names and name != 'make_new_item':
                yield self[name]
    def object_specific_fields(self):
        # returns every field that isn't in a concept
        field_names = [field.name for field in MDR.concept._meta.fields]
        for name in self.fields:
            if name not in field_names and name != 'make_new_item':
                yield self[name]

class Concept_1_Search(UserAwareForm):
    template = "aristotle_mdr/create/concept_wizard_1_search.html"
    # Object class fields
    name = forms.CharField(max_length=256)
    version = forms.CharField(max_length=256,required=False)
    description = forms.CharField(widget = forms.Textarea,required=False)

    def save(self, *args, **kwargs):
        pass

def subclassed_modelform(set_model):
    class MyForm(ConceptForm):
        class Meta(ConceptForm.Meta):
            model = set_model
            fields = '__all__'
    return MyForm

def subclassed_edit_modelform(set_model):
    class MyForm(ConceptForm):
        change_comments = forms.CharField(widget = forms.Textarea,required=False)
        class Meta(ConceptForm.Meta):
            model = set_model
            fields = '__all__'
    return MyForm

def subclassed_wizard_2_Results(set_model):
    class MyForm(Concept_2_Results):
        class Meta(Concept_2_Results.Meta):
            model = set_model
            fields = '__all__'
    return MyForm

class Concept_2_Results(ConceptForm):
    make_new_item = forms.BooleanField(initial=False,
        label=_("I've reviewed these items, and none of them meet my needs. Make me a new one."),
        error_messages={'required': 'You must select this to ackowledge you have reviewed the above items.'}
    )
    def __init__(self, *args, **kwargs):
        self.check_similar = kwargs.pop('check_similar',True)
        super(Concept_2_Results, self).__init__(*args, **kwargs)
        if not self.user.is_superuser:
            self.fields['workgroup'].queryset = self.user.profile.myWorkgroups
        self.fields['workgroup'].initial = self.user.profile.activeWorkgroup
        self.fields['name'].widget = forms.widgets.TextInput()
        #self.fields['description'].widget = forms.widgets.TextInput()
        if not self.check_similar:
            self.fields.pop('make_new_item')

class DEC_OCP_Search(UserAwareForm):
    template = "aristotle_mdr/create/dec_1_initial_search.html"
    # Object class fields
    oc_name = forms.CharField(max_length=256)
    oc_desc = forms.CharField(widget = forms.Textarea,required=False)
    # Property fields
    pr_name = forms.CharField(max_length=256)
    pr_desc = forms.CharField(widget = forms.Textarea,required=False)
    def save(self, *args, **kwargs):
        pass

class DEC_OCP_Results(UserAwareForm):
    def __init__(self, oc_similar=None, pr_similar=None, oc_duplicate=None, pr_duplicate=None, *args, **kwargs):
        super(DEC_OCP_Results, self).__init__(*args, **kwargs)

        if oc_similar:
            oc_options = [(oc.object.id,oc) for oc in oc_similar]
            oc_options.append(("X","None of the above meet my needs"))
            self.fields['oc_options'] = forms.ChoiceField(label="Similar Object Classes",
                                        choices=oc_options, widget=forms.RadioSelect())
        if pr_similar:
            pr_options = [(pr.object.id,pr) for pr in pr_similar]
            pr_options.append(("X","None of the above meet my needs"))
            self.fields['pr_options'] = forms.ChoiceField(label="Similar Properties",
                                        choices=tuple(pr_options), widget=forms.RadioSelect())
    def clean_oc_options(self):
        if self.cleaned_data['oc_options'] == "X":
            # The user chose to make their own item, so return No item.
            return None
        try:
            oc = MDR.ObjectClass.objects.get(pk=self.cleaned_data['oc_options'])
            return oc
        except ObjectDoesNotExist:
            return None
    def clean_pr_options(self):
        if self.cleaned_data['pr_options'] == "X":
            # The user chose to make their own item, so return No item.
            return None
        try:
            return MDR.Property.objects.get(pk=self.cleaned_data['pr_options'])
        except ObjectDoesNotExist:
            return None
    def save(self, *args, **kwargs):
        pass

class DEC_Find_DEC_Results(Concept_2_Results):
    class Meta(Concept_2_Results.Meta):
        model = MDR.DataElementConcept

class DEC_Complete(UserAwareForm):
    make_items = forms.BooleanField(initial=False,
        label=_("I've reviewed these items, and wish to create them."),
        error_messages={'required': 'You must select this to ackowledge you have reviewed the above items.'}
    )
    def save(self, *args, **kwargs):
        pass


class DE_OCPVD_Search(UserAwareForm):
    template = "aristotle_mdr/create/de_1_initial_search.html"
    # Object Class fields
    oc_name = forms.CharField(max_length=256)
    oc_desc = forms.CharField(widget = forms.Textarea,required=False)
    # Property fields
    pr_name = forms.CharField(max_length=256)
    pr_desc = forms.CharField(widget = forms.Textarea,required=False)
    # Value Domain fields
    vd_name = forms.CharField(max_length=256)
    vd_desc = forms.CharField(widget = forms.Textarea,required=False)
    def save(self, *args, **kwargs):
        pass


class DE_OCPVD_Results(DEC_OCP_Results):
    def __init__(self, vd_similar=None, vd_duplicate=None, *args, **kwargs):
        super(DE_OCPVD_Results, self).__init__(*args, **kwargs)

        if vd_similar:
            vd_options = [(vd.object.id,vd) for vd in vd_similar]
            vd_options.append(("X","None of the above meet my needs"))
            self.fields['vd_options'] = forms.ChoiceField(label="Similar Value Domains",
                                        choices=tuple(vd_options), widget=forms.RadioSelect())
    def clean_vd_options(self):
        if self.cleaned_data['vd_options'] == "X":
            # The user chose to make their own item, so return No item.
            return None
        try:
            return MDR.ValueDomain.objects.get(pk=self.cleaned_data['vd_options'])
        except ObjectDoesNotExist:
            return None
    def save(self, *args, **kwargs):
        pass

class DE_Find_DEC_Results(UserAwareForm):
    def __init__(self, *args, **kwargs):
        dec_similar = kwargs.pop('dec_similar')
        super(DE_Find_DEC_Results, self).__init__(*args, **kwargs)
        if dec_similar:
            dec_options = [(dec.id,dec) for dec in dec_similar]
            dec_options.append(("X","None of the above meet my needs"))
            self.fields['dec_options'] = forms.ChoiceField(label="Similar Data Element Concepts",
                                        choices=tuple(dec_options), widget=forms.RadioSelect())
    def clean_dec_options(self):
        if self.cleaned_data['dec_options'] == "X":
            # The user chose to make their own item, so return No item.
            return None
        try:
            dec = MDR.DataElementConcept.objects.get(pk=self.cleaned_data['dec_options'])
            return dec
        except ObjectDoesNotExist:
            return None
    def save(self, *args, **kwargs):
        pass

class DE_Find_DE_Results_from_components(UserAwareForm):
    make_new_item = forms.BooleanField(initial=False,
        label=_("I've reviewed these items, and none of them meet my needs. Make me a new one."),
        error_messages={'required': 'You must select this to ackowledge you have reviewed the above items.'}
    )
    def save(self, *args, **kwargs):
        pass

class DE_Find_DE_Results(Concept_2_Results):
    class Meta(Concept_2_Results.Meta):
        model = MDR.DataElement

class DE_Complete(UserAwareForm):
    make_items = forms.BooleanField(initial=False,
        label=_("I've reviewed these items, and wish to create them."),
        error_messages={'required': 'You must select this to ackowledge you have reviewed the above items.'}
    )
    def save(self, *args, **kwargs):
        pass

