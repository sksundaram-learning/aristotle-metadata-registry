from aristotle_mdr import models as MDR
from aristotle_mdr import forms as MDRForms
from django.contrib.formtools.wizard.views import SessionWizardView
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator


class ConceptWizard(SessionWizardView):
    widgets = {}
    templates = {
            "initial": "aristotle_mdr/create/concept_wizard_1_search.html",
            "results": "aristotle_mdr/create/concept_wizard_2_results.html",
            }
    template_name = "aristotle_mdr/create/concept_wizard_wrapper.html"
    form_list = [("initial", MDRForms.wizards.Concept_1_Search),
                  ("results", MDRForms.wizards.Concept_2_Results),
                 ]

    @method_decorator(permission_required('aristotle_mdr.user_is_editor'))
    def dispatch(self,  *args, **kwargs):
        return super(ConceptWizard,self).dispatch(*args, **kwargs)

    def get_template_names(self):
        return [self.templates[self.steps.current]]

    def get_form_kwargs(self, step):
        kwargs = super(ConceptWizard, self).get_form_kwargs(step)
        kwargs.update({ 'user': self.request.user})
        return kwargs

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
            return MDRForms.wizards.subclassed_wizard_2_Results(self)(**kwargs)
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

    def help_guide(self):
        from django.template import TemplateDoesNotExist
        try:
            from django.template.loader import get_template
            template_name = '%s/create/tips/%s.html'%(self.model._meta.app_label,self.model._meta.model_name)
            get_template(template_name)
            return template_name
        except TemplateDoesNotExist:
            # there is no extra content for this item, and thats ok.
            return None

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

class _DataElementConceptWizard(ConceptWizard):
    model = MDR.DataElementConcept
    widgets = {
        'conceptualDomain':autocomplete_light.ChoiceWidget('AutocompleteConceptualDomain'),
        'objectClass':autocomplete_light.ChoiceWidget('AutocompleteObjectClass'),
        'property':autocomplete_light.ChoiceWidget('AutocompleteProperty'),
        }
    templates = {
            "initial": "aristotle_mdr/create/concept_wizard_1_search.html",
            "results": "aristotle_mdr/create/concept_wizard_2_results.html",
            }
    template_name = "aristotle_mdr/create/concept_wizard_wrapper.html"
    form_list = [("initial", MDRForms.wizards.Concept_1_Search),
                  ("results", MDRForms.wizards.Concept_2_Results),
                 ]

    @method_decorator(permission_required('aristotle_mdr.user_is_editor'))
    def dispatch(self,  *args, **kwargs):
        return super(ConceptWizard,self).dispatch(*args, **kwargs)

    def get_template_names(self):
        return [self.templates[self.steps.current]]
TEMPLATES = {
        "initial": "aristotle_mdr/create/dec_1_initial_search.html",
        "results": "aristotle_mdr/create/dec_2_search_results.html",
        }

class DataElementConceptWizard(SessionWizardView):
    template_name = "aristotle_mdr/create/dec_template_wrapper.html"
    form_list = [("initial", MDRForms.wizards.DEC_Initial_Search),
                  ("results", MDRForms.wizards.DEC_Results),
                 ]

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def process_step(self,form):
        if self.steps.current == 'initial':
            print form.cleaned_data['oc_name']
            self.search_terms = {
                'oc_name': form.cleaned_data['oc_name'],
                'oc_desc': form.cleaned_data['oc_desc'],
                'pr_name': form.cleaned_data['pr_name'],
                'pr_desc': form.cleaned_data['pr_desc'],
            }

    def get_form_kwargs(self, step):
        # determine the step if not given
        if step is None:
            step = self.steps.current

        if step == 'results':
            return { 'oc_results': self.find_similar(model=MDR.ObjectClass,
                                name=self.search_terms['oc_name'],
                                description=self.search_terms['oc_desc']
                            ),
                     'pr_results': self.find_similar(model=MDR.Property,
                                name=self.search_terms['pr_name'],
                                description=self.search_terms['pr_desc']
                            )}
        return {}

    def get_context_data(self, form, **kwargs):
        context = super(DataElementConceptWizard, self).get_context_data(form=form, **kwargs)
        return context
        if self.steps.current == 'initial':
            context.update({'test': "hello"})
        if self.steps.current == 'results':
            context.update({'oc_results': findSimilar(model=MDR.ObjectClass,
                                name=self.search_terms['oc_name'],
                                description=self.search_terms['oc_desc']
                            )})
            context.update({'pr_results': findSimilar(MDR.Property,
                                name=self.search_terms['pr_name'],
                                description=self.search_terms['pr_desc']
                            )})
        return context

    """
        Looks for items of a given item type with the given search terms
    """
    def find_similar(self,name,description,model=None):
        if hasattr(self,'similar_items'):
            return self.similar_items

        from aristotle_mdr.forms.search import PermissionSearchQuerySet as PSQS
        if model is None:
            model = self.model
        q = PSQS().models(model).auto_query(description + " " + name).filter(
                statuses__in=[  MDR.STATES[int(s)]
                                for s in [MDR.STATES.standard,MDR.STATES.preferred]
                            ])

            #.filter(states="Standard")
        similar = q
        self.similar_items = similar
        return self.similar_items

    def done(self, form_list, **kwargs):
        pass
