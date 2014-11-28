from django import forms
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

import aristotle_mdr.models as MDR

class ConceptForm(forms.ModelForm):
    """
    Add this in when we look at reintroducing the fancy templates.
    required_css_class = 'required'
    """
    def __init__(self, *args, **kwargs):
        #TODO: Have tis throw a 'no user' error
        self.user = kwargs.pop('user', None)
        first_load = kwargs.pop('first_load', None)
        super(ConceptForm, self).__init__(*args, **kwargs)
        if not self.user.is_superuser:
            self.fields['workgroup'].queryset = self.user.profile.myWorkgroups
        self.fields['name'].widget = forms.widgets.TextInput()

    class Meta:
        exclude = ['readyToReview','superseded_by','_is_public','_is_locked','originURI']

class Concept_1_Search(forms.Form):
    template = "aristotle_mdr/create/concept_wizard_1_search.html"
    # Object class fields
    name = forms.CharField(max_length=256)
    version = forms.CharField(max_length=256,required=False)
    description = forms.CharField(widget = forms.Textarea,required=False)
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(Concept_1_Search, self).__init__(*args, **kwargs)
    def save(self, *args, **kwargs):
        pass
def subclassed_wizard_2_Results(wizard):
    class MyForm(Concept_2_Results):
        class Meta(Concept_2_Results.Meta):
            model = wizard.model
        def __init__(self, *args, **kwargs):
            kwargs.update({'user':wizard.request.user})
            super(MyForm, self).__init__(*args, **kwargs)
            for field,widget in wizard.widgets.items():
                self.fields[field].widget = widget
    return MyForm

class Concept_2_Results(forms.ModelForm):
    make_new_item = forms.BooleanField(initial=False,
        label=_("I've reviewed these items, and none of them meet my needs. Make me a new one."),
        error_messages={'required': 'You must select this to ackowledge you have reviewed the above items.'}
    )
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.check_similar = kwargs.pop('check_similar')

        super(Concept_2_Results, self).__init__(*args, **kwargs)
        if not self.user.is_superuser:
            self.fields['workgroup'].queryset = self.user.profile.myWorkgroups
        self.fields['workgroup'].initial = self.user.profile.activeWorkgroup
        self.fields['name'].widget = forms.widgets.TextInput()
        if not self.check_similar:
            self.fields.pop('make_new_item')
    class Meta:
        model = MDR._concept
        exclude = ['readyToReview','superseded_by','_is_public','_is_locked','originURI']

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

class DEC_OCP_Search(forms.Form):
    template = "aristotle_mdr/create/dec_1_initial_search.html"
    # Object class fields
    oc_name = forms.CharField(max_length=256)
    oc_desc = forms.CharField(widget = forms.Textarea,required=False)
    # Property fields
    pr_name = forms.CharField(max_length=256)
    pr_desc = forms.CharField(widget = forms.Textarea,required=False)

class DEC_OCP_Results(forms.Form):
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
        try:
            return MDR.ObjectClass.objects.get(pk=self.cleaned_data['oc_options'])
        except:
            return None
    def clean_pr_options(self):
        try:
            return MDR.Property.objects.get(pk=self.cleaned_data['pr_options'])
        except:
            return None

class DEC_Find_DEC_Results(forms.Form):
    def __init__(self, dec_matches=None, *args, **kwargs):
        super(DEC_Find_DEC_Results, self).__init__(*args, **kwargs)
        # this is silly, they are trying to create something. giving them an option
        # field here makes no sense.
        if dec_matches:
            dec_options = [(dec.id,dec) for dec in dec_matches]
            dec_options.append(("X","None of the above meet my needs"))
            self.fields['dec_options'] = forms.ChoiceField(label="Similar Data Element Concepts",
                                        choices=dec_options, widget=forms.RadioSelect())
