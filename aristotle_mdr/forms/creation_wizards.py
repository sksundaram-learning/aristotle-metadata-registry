from django import forms
from django.utils.safestring import mark_safe
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
        exclude = ['readyToReview','superseded_by','_is_public','_is_locked']

class Concept_1_Search(forms.Form):
    template = "aristotle_mdr/create/concept_wizard_1_search.html"
    # Object class fields
    name = forms.CharField(max_length=256)
    description = forms.CharField(widget = forms.Textarea,required=False)

class Concept_2_Results(forms.Form):
    def __init__(self , similar=None, *args, **kwargs):
        super(Concept_2_Results, self).__init__(*args, **kwargs)

#    def __init__(self, *args, **kwargs):
#        hasSimilarItems = kwargs.get('hasSimilarItems', False)
#        if 'hasSimilarItems' in kwargs:
#            del kwargs['hasSimilarItems']
#        super(ConceptForm, self).__init__(*args, **kwargs)
#        if hasSimilarItems:
#            del self.fields['userAware']

class ValueDomainForm(ConceptForm):
    template = "aristotle_mdr/create/valueDomain.html"

    class Meta:
        model = MDR.ValueDomain
        exclude = ['readyToReview','superseded_by']

class DataElementConceptForm(ConceptForm):
    template = "aristotle_mdr/create/dataElementConcept.html"

    class Meta(ConceptForm.Meta):
        model = MDR.DataElementConcept

class PropertyForm(ConceptForm):
    template = "aristotle_mdr/create/property.html"

    class Meta(ConceptForm.Meta):
        model = MDR.Property

class ObjectClassForm(ConceptForm):
    template = "aristotle_mdr/create/objectClass.html"

    class Meta(ConceptForm.Meta):
        model = MDR.ObjectClass

class DEC_Initial_Search(forms.Form):
    template = "aristotle_mdr/create/dec_1_initial_search.html"
    # Object class fields
    oc_name = forms.CharField(max_length=100)
    oc_desc = forms.CharField(widget = forms.Textarea,required=False)
    # Property fields
    pr_name = forms.CharField(max_length=100)
    pr_desc = forms.CharField(widget = forms.Textarea,required=False)

class DEC_Results(forms.Form):
    def __init__(self, oc_results=None, pr_results=None , *args, **kwargs):
        super(DEC_Results, self).__init__(*args, **kwargs)

        # If we are passed a
        if oc_results:
            oc_options = []
            for oc in oc_results:
                # TODO: THIS IS A BAAAAD CHOICE, BUT WE'LL ACCEPT IT FOR NOW!!!
                # HTML in code is a BAD IDEA... but we accept it here because we need
                # links on the options for users to preview the possible options.
                label = mark_safe('<a href="/item/{id}">{name}</a>'.format(id=oc.id,name=oc.name))
                oc_options.append((oc.id,label))
            oc_options.append(("X","None of the above meet my needs"))
            oc_options=tuple(oc_options)
            self.fields['oc_options'] = forms.ChoiceField(verbose_name="Similar Object Classes",
                                        choices=oc_options, widget=forms.RadioSelect())
