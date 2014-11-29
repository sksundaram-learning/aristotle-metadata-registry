from aristotle_mdr import models as MDR
from aristotle_mdr import forms as MDRForms
from django.contrib.formtools.wizard.views import SessionWizardView
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect

class PermissionWizard(SessionWizardView):

    @method_decorator(permission_required('aristotle_mdr.user_is_editor'))
    def dispatch(self,  *args, **kwargs):
        return super(PermissionWizard,self).dispatch(*args, **kwargs)
    def get_template_names(self):
        return [self.templates[self.steps.current]]
    def get_form_kwargs(self, step):
        kwargs = super(PermissionWizard, self).get_form_kwargs(step)
        kwargs.update({ 'user': self.request.user})
        return kwargs

    def help_guide(self,model=None):
        if model is None:
            model=self.model
        from django.template import TemplateDoesNotExist
        try:
            from django.template.loader import get_template
            template_name = '%s/create/tips/%s.html'%(model._meta.app_label,model._meta.model_name)
            get_template(template_name)
            return template_name
        except TemplateDoesNotExist:
            # there is no extra content for this item, and thats ok.
            return None

class ConceptWizard(PermissionWizard):
    widgets = {}
    templates = {
            "initial": "aristotle_mdr/create/concept_wizard_1_search.html",
            "results": "aristotle_mdr/create/concept_wizard_2_results.html",
            }
    template_name = "aristotle_mdr/create/concept_wizard_wrapper.html"
    form_list = [("initial", MDRForms.wizards.Concept_1_Search),
                  ("results", MDRForms.wizards.Concept_2_Results),
                 ]

    def get_form(self, step=None, data=None, files=None):
        if step is None:
            step = self.steps.current
        if step == "results":
            similar = self.find_similar()
            duplicates = self.find_duplicates()
            kwargs = self.get_form_kwargs(step)
            kwargs.update({
                'data': data,
                'files': files,
                'prefix': self.get_form_prefix(step, self.form_list[step]),
                'initial': self.get_cleaned_data_for_step('initial'),
                'check_similar': similar or duplicates
            })
            if self.widgets:
                kwargs.update({'custom_widgets':self.widgets})
            return MDRForms.wizards.subclassed_wizard_2_Results(self.model)(**kwargs)
        return super(ConceptWizard, self).get_form(step, data, files)

    def get_context_data(self, form, **kwargs):
        context = super(ConceptWizard, self).get_context_data(form=form, **kwargs)

        if self.steps.current == 'results':
            self.search_terms = self.get_cleaned_data_for_step('initial')
            context.update({'search_name':self.search_terms['name'],})
            duplicates = self.find_duplicates()
            if duplicates:
                context.update({'duplicate_items': duplicates})
            else:
                context.update({'similar_items': self.find_similar()})
        context.update({'model_name': self.model._meta.verbose_name,
                        'template_name': self.template_name,
                        'help_guide':self.help_guide(),
                        'current_step':self.steps.current
                        })
        return context


    def done(self, form_list, **kwargs):
        item = None
        for form in form_list:
            item = form.save()
        return HttpResponseRedirect('/item/%s'%item.id)

    def find_duplicates(self):
        if hasattr(self,'duplicate_items'):
            return self.duplicate_items
        self.search_terms = self.get_cleaned_data_for_step('initial')
        name = self.search_terms['name']
        name = name.strip()
        self.duplicate_items = self.model.objects.filter(name__iexact=name).public().all()
        return self.duplicate_items

    """
        Looks for items of a given item type with the given search terms
    """
    def find_similar(self,model=None):
        if hasattr(self,'similar_items'):
            return self.similar_items
        self.search_terms = self.get_cleaned_data_for_step('initial')

        from aristotle_mdr.forms.search import PermissionSearchQuerySet as PSQS
        if model is None:
            model = self.model

        q = PSQS().models(model).auto_query(
            self.search_terms['description'] + " " + self.search_terms['name']
            ).filter(statuses__in=[MDR.STATES[int(s)] for s in [MDR.STATES.standard,MDR.STATES.preferred]])

            #.filter(states="Standard")
        similar = q
        self.similar_items = similar
        return self.similar_items


import autocomplete_light
autocomplete_light.autodiscover()

class ObjectClassWizard(ConceptWizard):
    model = MDR.ObjectClass
class PropertyWizard(ConceptWizard):
    model = MDR.Property
class ValueDomainWizard(ConceptWizard):
    model = MDR.ValueDomain
class ConceptualDomainWizard(ConceptWizard):
    model = MDR.ConceptualDomain

"""class DataElementConceptWizard(ConceptWizard):
    model = MDR.DataElementConcept
    widgets = {
        'conceptualDomain':autocomplete_light.ChoiceWidget('AutocompleteConceptualDomain'),
        'objectClass':autocomplete_light.ChoiceWidget('AutocompleteObjectClass'),
        'property':autocomplete_light.ChoiceWidget('AutocompleteProperty'),
        }
"""

def valid_object_class_and_property(wizard):
    if wizard.steps.current is None or wizard.steps.current is False or wizard.steps.current == "oc_p_search":
        return False
    try:
        oc = wizard.get_cleaned_data_for_step('oc_p_results').get('oc_options', None)
        pr = wizard.get_cleaned_data_for_step('oc_p_results').get('pr_options', None)
        return oc and pr
    except:
        return False
def no_valid_property(wizard):
    if not hasattr(wizard,'_property'):
        return False
    return not wizard.get_property()
def no_valid_object_class(wizard):
    if not hasattr(wizard,'_object_class'):
        return False
    return not wizard.get_object_class()

class DataElementConceptWizard(PermissionWizard):
    model = MDR.DataElementConcept
    templates = {
        "oc_p_search": "aristotle_mdr/create/dec_1_initial_search.html",
        "oc_p_results": "aristotle_mdr/create/dec_2_search_results.html",
        "make_oc": "aristotle_mdr/create/concept_wizard_2_results.html",
        "make_p": "aristotle_mdr/create/concept_wizard_2_results.html",
        "find_dec_results": "aristotle_mdr/create/dec_3_dec_search_results.html",
        }
    template_name = "aristotle_mdr/create/dec_template_wrapper.html"
    form_list = [("oc_p_search", MDRForms.wizards.DEC_OCP_Search),
                  ("oc_p_results", MDRForms.wizards.DEC_OCP_Results),
                  ("make_oc", MDRForms.wizards.subclassed_wizard_2_Results(MDR.ObjectClass)),
                  ("make_p", MDRForms.wizards.subclassed_wizard_2_Results(MDR.Property)),
                  ("find_dec_results", MDRForms.wizards.DEC_Find_DEC_Results),
                  #("make_dec", MDRForms.wizards.DEC_OCP_Search),
                  #("complete", MDRForms.wizards.DEC_Complete),
                 ]
    condition_dict = {
        #"find_dec_results": valid_object_class_and_property,
        "make_oc": no_valid_object_class ,
        #"make_p": no_valid_property,
        }

    widgets = {
        'conceptualDomain':autocomplete_light.ChoiceWidget('AutocompleteConceptualDomain'),
        'objectClass':autocomplete_light.ChoiceWidget('AutocompleteObjectClass'),
        'property':autocomplete_light.ChoiceWidget('AutocompleteProperty'),
        }

    def process_step(self, form):
        data = self.get_form_step_data(form)
        if self.steps.current == "oc_p_results":
            self._object_class = data.get('oc_options',None)
            self._property = data.get('pr_options',None)
        return data

    def get_object_class(self):
        if hasattr(self,'_object_class'):
            return self._object_class
        return None

    def get_property(self):
        if hasattr(self,'_property'):
            return self._property
        return None

    def get_data_element_concept(self):
        if hasattr(self,'_data_element_concept'):
            return self._data_element_concept
        oc = self.get_object_class()
        pr = self.get_property()
        if oc and pr:
            self._data_element_concept = MDR.DataElementConcept.objects.filter(objectClass=oc,property=pr).public()
            #.visible(self.request.user)
            return self._data_element_concept
        else:
            return []

    def get_form_kwargs(self, step):
        # determine the step if not given
        if step is None:
            step = self.steps.current
        kwargs = super(DataElementConceptWizard, self).get_form_kwargs(step)

        if step == 'oc_p_results':
            ocp = self.get_cleaned_data_for_step('oc_p_search')
            if ocp:
                kwargs.update({
                    'oc_similar': self.find_similar(model=MDR.ObjectClass,
                            name        = ocp.get('oc_name',""),
                            description = ocp.get('oc_desc',"")
                        ),
                    'pr_similar': self.find_similar(model=MDR.Property,
                            name        = ocp.get('pr_name',""),
                            description = ocp.get('pr_desc',"")
                        )
                    })
        elif step == 'make_oc':
            kwargs.update({
                'check_similar': False # They waived this on the previous page
            })
        elif step == 'find_dec_results':
            kwargs.update({
                'objectClass':self.get_object_class(),
                'property':self.get_property(),
                'custom_widgets':self.widgets
                })
        return kwargs

    def get_context_data(self, form, **kwargs):
        context = super(DataElementConceptWizard, self).get_context_data(form=form, **kwargs)

        if self.steps.current == 'make_oc':
            context.update({
                'model_name': MDR.ObjectClass._meta.verbose_name,
                'help_guide':self.help_guide(MDR.ObjectClass),
                })
        if self.steps.current == 'find_dec_results':
            context.update({
                'objectClass':self.get_object_class(),
                'property':self.get_property(),
                'dec_matches':self.get_data_element_concept()
                })
        context.update({
            'template_name':'aristotle_mdr/create/dec_template_wrapper.html',
            })
        return context

    def get_form_initial(self, step):
        initial = super(DataElementConceptWizard,self).get_form_initial(step)
        if step is None:
            step = self.steps.current
        if step == "make_oc":
            ocp = self.get_cleaned_data_for_step('oc_p_search')
            if ocp:
                initial.update({
                        'name'        : ocp.get('oc_name',""),
                        'description' : ocp.get('oc_desc',"")
                        })
        elif step == "make_p":
            ocp = self.get_cleaned_data_for_step('oc_p_search')
            if ocp:
                initial.update({
                        'name'        : ocp.get('pr_name',""),
                        'description' : ocp.get('pr_desc',"")
                        })
        elif self.steps.current == 'find_dec_results':
            oc_name,pr_name = ""
            ocp = self.get_cleaned_data_for_step('oc_p_search')
            if ocp:
                oc_name = self.get_object_class().name or ocp.get('oc_name',""),
                pr_name = self.get_property().name or ocp.get('pr_name',""),
                oc_desc = self.get_object_class().description or ocp.get('oc_desc',""),
                pr_desc = self.get_property().description or ocp.get('pr_desc',""),
            initial.update({
                'name' :        "%s - %s"%(oc_name,pr_name),
                'description' : "%s - %s"%(oc_desc,pr_desc)
                })
        return initial

    """
        Looks for items of a given item type with the given search terms
    """
    def find_similar(self,name,description,model=None):
        from aristotle_mdr.forms.search import PermissionSearchQuerySet as PSQS
        if model is None:
            model = self.model
        if not hasattr(self,"similar_items"):
            self.similar_items = {}
        cached_items = self.similar_items.get(model,None)
        if cached_items:
            return cached_items

        similar = PSQS().models(model).auto_query(name + " " + description).filter(
                statuses__in=[  MDR.STATES[int(s)]
                                for s in [MDR.STATES.standard,MDR.STATES.preferred]
                            ])

        self.similar_items[model] = similar
        return similar

    def done(self, form_list, **kwargs):
        item = None
        for form in form_list:
            item = form.save()
        return HttpResponseRedirect('/item/%s'%item.id)
