from aristotle_mdr import models as MDR
from aristotle_mdr import forms as MDRForms
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.formtools.wizard.views import SessionWizardView
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

"""
THis allows use to perform an inspection of the registered items
so extensions don't need to register to get fancy creation wizards,
they are available based on either the model name, or if that is
ambiguous, present an option to make the right item.
"""
def create_item(request,app_label=None,model_name=None):
    if not model_name:
        raise ImproperlyConfigured

    mod = None
    if app_label is None:
        models = ContentType.objects.filter(model=model_name)
        if models.count() == 0:
            raise Http404 # TODO: Throw better, more descriptive error
        elif models.count() == 1:
            mod = models.first().model_class()
        else: # models.count() > 1:
            # TODO: make this template
            return render(request,"aristotle_mdr/ambiguous_create_request.html",
                {'models':models,}
        )
    else:
        mod = ContentType.objects.get(app_label=app_label,model=model_name).model_class()

    class DynamicAristotleWizard(ConceptWizard):
        model = mod
    return DynamicAristotleWizard.as_view()(request)

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
        return HttpResponseRedirect(reverse("aristotle:item",args=[item.id]))

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

def no_valid_property(wizard):
    return not wizard.get_property()
def no_valid_object_class(wizard):
    return not wizard.get_object_class()
def no_valid_valuedomain(wizard):
    return not wizard.get_value_domain()

class MultiStepAristotleWizard(PermissionWizard):
    def get_object_class(self):
        if hasattr(self,'_object_class'):
            return self._object_class
        else:
            ocp = self.get_cleaned_data_for_step('component_results')
            if ocp:
                oc = ocp.get('oc_options',None)
                if oc:
                    self._object_class = oc
                    return self._object_class
        return None

    def get_property(self):
        if hasattr(self,'_property'):
            return self._property
        else:
            ocp = self.get_cleaned_data_for_step('component_results')
            if ocp:
                pr = ocp.get('pr_options',None)
                if pr:
                    self._property = pr
                    return self._property
        return None

    def get_value_domain(self):
        if hasattr(self,'_valuedomain'):
            return self._valuedomain
        else:
            ocp = self.get_cleaned_data_for_step('component_results')
            if ocp:
                pr = ocp.get('vd_options',None)
                if pr:
                    self._valuedomain = pr
                    return self._valuedomain
        return None

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

        similar = PSQS().models(model).auto_query(name + " " + description).apply_permission_checks(user=self.request.user)
        self.similar_items[model] = similar
        return similar

    def get_field_defaults(self,field_prefix):
        ocp = self.get_cleaned_data_for_step('component_search')
        fd = {}
        if ocp:
            fd = {  'name'        : ocp.get(field_prefix+'_name',""),
                    'description' : ocp.get(field_prefix+'_desc',"")
                }
        return fd


class DataElementConceptWizard(MultiStepAristotleWizard):
    model = MDR.DataElementConcept
    templates = {
        "component_search": "aristotle_mdr/create/dec_1_initial_search.html",
        "component_results": "aristotle_mdr/create/dec_2_search_results.html",
        "make_oc": "aristotle_mdr/create/concept_wizard_2_results.html",
        "make_p": "aristotle_mdr/create/concept_wizard_2_results.html",
        "find_dec_results": "aristotle_mdr/create/dec_3_dec_search_results.html",
        "completed": "aristotle_mdr/create/dec_4_complete.html",
        }
    template_name = "aristotle_mdr/create/dec_template_wrapper.html"
    form_list = [ ("component_search", MDRForms.wizards.DEC_OCP_Search),
                  ("component_results", MDRForms.wizards.DEC_OCP_Results),
                  ("make_oc", MDRForms.wizards.subclassed_wizard_2_Results(MDR.ObjectClass)),
                  ("make_p", MDRForms.wizards.subclassed_wizard_2_Results(MDR.Property)),
                  ("find_dec_results", MDRForms.wizards.DEC_Find_DEC_Results),
                  ("completed", MDRForms.wizards.DEC_Complete),
                 ]
    condition_dict = {
        "make_oc": no_valid_object_class ,
        "make_p": no_valid_property,
        }

    def get_data_element_concept(self):
        if hasattr(self,'_data_element_concept'):
            return self._data_element_concept
        oc = self.get_object_class()
        pr = self.get_property()
        if oc and pr:
            self._data_element_concept = MDR.DataElementConcept.objects.filter(objectClass=oc,property=pr).visible(self.request.user)
            return self._data_element_concept
        else:
            return []

    def get_form_kwargs(self, step):
        # determine the step if not given
        if step is None:
            step = self.steps.current
        kwargs = super(DataElementConceptWizard, self).get_form_kwargs(step)

        if step == 'component_results':
            ocp = self.get_cleaned_data_for_step('component_search')
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
        elif step in ['make_oc','make_p']:
            kwargs.update({
                'check_similar': False # They waived this on the previous page
            })
        elif step == 'find_dec_results':
            kwargs.update({
                'check_similar': self.get_data_element_concept()
                })
        return kwargs

    def get_context_data(self, form, **kwargs):
        context = super(DataElementConceptWizard, self).get_context_data(form=form, **kwargs)

        context.update({
            'component_search'  : {'percent_complete':20, 'step_title':_('Search for components')},
            'component_results' : {'percent_complete':40, 'step_title':_('Refine components')},
            'make_oc'           : {'percent_complete':50, 'step_title':_('Create Object Class')},
            'make_p'            : {'percent_complete':60, 'step_title':_('Create Property')},
            'find_dec_results'  : {'percent_complete':80, 'step_title':_('Review Data Element Concept')},
            'completed'         : {'percent_complete':100,'step_title':_('Complete and Save')},
            }.get(self.steps.current,{}))

        if self.steps.current == 'make_oc':
            context.update({
                'model_name': MDR.ObjectClass._meta.verbose_name,
                'help_guide':self.help_guide(MDR.ObjectClass),
                })
        if self.steps.current == 'make_p':
            context.update({
                'model_name': MDR.Property._meta.verbose_name,
                'help_guide':self.help_guide(MDR.Property),
                })
        if self.steps.current == 'find_dec_results':
            context.update({
                'oc_match':self.get_object_class(),
                'pr_match':self.get_property(),
                'dec_matches':self.get_data_element_concept()
                })
        if self.steps.current == 'completed':
            context.update({
                'made_oc':not self.get_object_class(),
                'made_pr':not self.get_property(),
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
            initial.update(self.get_field_defaults('oc'))
        elif step == "make_p":
            initial.update(self.get_field_defaults('pr'))
        elif step == 'find_dec_results':
            made_oc = self.get_cleaned_data_for_step('make_oc')
            if self.get_object_class():
                oc_name = self.get_object_class().name
                oc_desc = self.get_object_class().description
            elif made_oc:
                oc_name = made_oc.get('name',_("No object class name found"))
                oc_desc = made_oc.get('description',_("No object class description found"))
            else:
                oc_name = _("No object class name found")
                oc_desc = _("No object class description found")
            if oc_desc:
                # lower case the first letter as this will be the latter part of a sentence
                oc_desc = oc_desc[0].lower() + oc_desc[1:]

            made_pr = self.get_cleaned_data_for_step('make_p')
            if self.get_property():
                pr_name = self.get_property().name
                pr_desc = self.get_property().description
            elif made_pr:
                pr_name = made_pr.get('name',_("No property name found"))
                pr_desc = made_pr.get('description',_("No property description found"))
            else:
                pr_name = _("No property name found")
                pr_desc = _("No property description found")
            if pr_desc and pr_desc[-1] == ".":
                # remove the tailing period as we are going to try to make a sentence
                pr_desc = pr_desc[:-1]

            SEPARATORS = getattr(settings, 'ARISTOTLE_SETTINGS', {}).get('SEPARATORS',{})

            initial.update({
                'name' :        u"{oc}{separator}{pr}".format(
                    oc=oc_name,
                    separator=SEPARATORS["DataElementConcept"],
                    pr=pr_name,
                    ),
                'description' : _(u"{pr} of a {oc} \n\n - This was an autogenerated description.").format(oc=oc_desc,pr=pr_desc)
                })
        return initial

    def done(self, form_list, **kwargs):
        oc = self.get_object_class()
        pr = self.get_property()
        dec = None
        for form in form_list:
            saved_item = form.save()
            if type(saved_item) == MDR.Property:
                pr = saved_item
                messages.success(self.request,
                        mark_safe(_("New Property '{name}' Saved - <a href='url'>id:{id}</a>").format(name=saved_item.name,id=saved_item.id))
                )
            if type(saved_item) == MDR.ObjectClass:
                oc = saved_item
                messages.success(self.request,
                        mark_safe(_("New Object Class '{name}' Saved - <a href='url'>id:{id}</a>").format(name=saved_item.name,id=saved_item.id))
                )
            if type(saved_item) == MDR.DataElementConcept:
                dec = saved_item
                messages.success(self.request,
                        mark_safe(_("New Data Element Concept '{name}' Saved - <a href='url'>id:{id}</a>").format(
                            name=saved_item.name,id=saved_item.id
                            ))
                )
        if dec is not None:
            dec.objectClass = oc
            dec.property = pr
            dec.save()
        return HttpResponseRedirect(reverse("aristotle:%s"%dec.url_name,args=[dec.id]))

class DataElementWizard(MultiStepAristotleWizard):
    model = MDR.DataElement
    templates = {
        "component_search": "aristotle_mdr/create/de_1_initial_search.html",
        "component_results": "aristotle_mdr/create/de_2_search_results.html",
        "make_oc": "aristotle_mdr/create/concept_wizard_2_results.html",
        "make_p": "aristotle_mdr/create/concept_wizard_2_results.html",
        "find_dec_results": "aristotle_mdr/create/de_3_dec_search_results.html",
        "make_vd": "aristotle_mdr/create/concept_wizard_2_results.html",
        "find_de_results": "aristotle_mdr/create/de_4_de_search_results.html",
        "completed": "aristotle_mdr/create/dec_5_complete.html",
        }
    form_list = [ ("component_search", MDRForms.wizards.DE_OCPVD_Search),
                  ("component_results", MDRForms.wizards.DE_OCPVD_Results),
                  ("make_oc", MDRForms.wizards.subclassed_wizard_2_Results(MDR.ObjectClass)),
                  ("make_p", MDRForms.wizards.subclassed_wizard_2_Results(MDR.Property)),
                  ("find_dec_results", MDRForms.wizards.DE_Find_DEC_Results),
                  ("make_vd", MDRForms.wizards.subclassed_wizard_2_Results(MDR.ValueDomain)),
                  ("find_de_results", MDRForms.wizards.DE_Find_DE_Results),
                  ("completed", MDRForms.wizards.DE_Complete),
                 ]
    condition_dict = {
        "make_oc": no_valid_object_class,
        "make_p": no_valid_property,
        "make_vd": no_valid_valuedomain,
        }


    def get_data_element_concepts(self):
        if hasattr(self,'_data_element_concepts'):
            return self._data_element_concepts
        oc = self.get_object_class()
        pr = self.get_property()
        if oc and pr:
            self._data_element_concepts = MDR.DataElementConcept.objects.filter(objectClass=oc,property=pr).visible(self.request.user)
            return self._data_element_concepts
        else:
            return []

    def get_data_element_concept(self):
        if hasattr(self,'_data_element_concept'):
            return self._data_element_concept
        else:
            results = self.get_cleaned_data_for_step('find_dec_results')
            if results:
                dec = results.get('dec_options',None)
                if dec:
                    self._data_element_concept = dec
                    return self._data_element_concept
        return None

    def get_data_element(self):
        if hasattr(self,'_data_element'):
            return self._data_element
        dec = self.get_data_element_concept()
        vd = self.get_value_domain()
        if dec and vd:
            self._data_element = MDR.DataElement.objects.filter(dataElementConcept=dec,valueDomain=vd).visible(self.request.user)
            return self._data_element
        else:
            return []

    def get_form_kwargs(self, step):
        # determine the step if not given
        kwargs = super(DataElementWizard, self).get_form_kwargs(step)
        if step is None:
            step = self.steps.current

        if step == 'component_results':
            ocp = self.get_cleaned_data_for_step('component_search')
            if ocp:
                kwargs.update({
                    'oc_similar': self.find_similar(model=MDR.ObjectClass,
                            name        = ocp.get('oc_name',""),
                            description = ocp.get('oc_desc',"")
                        ),
                    'pr_similar': self.find_similar(model=MDR.Property,
                            name        = ocp.get('pr_name',""),
                            description = ocp.get('pr_desc',"")
                        ),
                    'vd_similar': self.find_similar(model=MDR.ValueDomain,
                            name        = ocp.get('vd_name',""),
                            description = ocp.get('vd_desc',"")
                        )
                    })
        elif step in ['make_oc','make_p','make_vd']:
            kwargs.update({
                'check_similar': False # They waived this on a previous page
            })
        elif step == 'find_dec_results':
            kwargs.update({
                'check_similar': False, # They waived this on a previous page
                'dec_similar': self.get_data_element_concepts()
                })
        elif step == 'find_de_results':
            kwargs.update({
                })
        return kwargs

    def get_context_data(self, form, **kwargs):
        context = super(DataElementWizard, self).get_context_data(form=form, **kwargs)

        context.update({
            'component_search'  : {'percent_complete':12, 'step_title':_('Search for components')},
            'component_results' : {'percent_complete':25, 'step_title':_('Refine components')},
            'make_oc'           : {'percent_complete':38, 'step_title':_('Create Object Class')},
            'make_p'            : {'percent_complete':50, 'step_title':_('Create Property')},
            'find_dec_results'  : {'percent_complete':62, 'step_title':_('Review Data Element Concept')},
            'make_vd'           : {'percent_complete':75, 'step_title':_('Create Value Domain')},
            'find_de_results'   : {'percent_complete':88, 'step_title':_('Review Data Element')},
            'completed'         : {'percent_complete':100,'step_title':_('Complete and Save')},
            }.get(self.steps.current,{}))

        if self.steps.current == 'make_vd':
            context.update({
                'model_name': MDR.ValueDomain._meta.verbose_name,
                'help_guide':self.help_guide(MDR.Property),
                })
        if self.steps.current == 'find_dec_results':
            context.update({
                'oc_match':self.get_object_class(),
                'pr_match':self.get_property(),
                'dec_matches':self.get_data_element_concepts()
                })
        if self.steps.current == 'find_de_results':
            context.update({
                'dec_match':self.get_data_element_concept(),
                'vd_match':self.get_value_domain(),
                'de_matches':self.get_data_element()
                })
        if self.steps.current == 'completed':
            context.update({
                'made_oc':not self.get_object_class(),
                'made_pr':not self.get_property(),
                'made_vd':not self.get_value_domain(),
                'made_dec':self.get_data_element_concept(),
                'de_matches':self.get_data_element()
                })
        return context

    def get_form_initial(self, step):
        initial = super(DataElementWizard,self).get_form_initial(step)
        if step is None:
            step = self.steps.current
        if step == "make_vd":
            initial.update(self.get_field_defaults('vd'))
        return initial

    def done(self, form_list, **kwargs):
        oc = self.get_object_class()
        pr = self.get_property()
        vd = self.get_value_domain()
        dec = self.get_data_element_concept()
        de = None
        for form in form_list:
            saved_item = form.save()
            if type(saved_item) == MDR.Property:
                pr = saved_item
                messages.success(self.request,
                        mark_safe(_("New Property '{name}' Saved - <a href='url'>id:{id}</a>").format(name=saved_item.name,id=saved_item.id))
                )
            if type(saved_item) == MDR.ObjectClass:
                oc = saved_item
                messages.success(self.request,
                        mark_safe(_("New Object Class '{name}' Saved - <a href='url'>id:{id}</a>").format(name=saved_item.name,id=saved_item.id))
                )
            if type(saved_item) == MDR.DataElementConcept:
                dec = saved_item
                messages.success(self.request,
                        mark_safe(_("New Data Element Concept '{name}' Saved - <a href='url'>id:{id}</a>").format(
                            name=saved_item.name,id=saved_item.id
                            ))
                )
        if dec is not None:
            dec.objectClass = oc
            dec.property = pr
            dec.save()
        if de is not None:
            dec.dataElementConcept = dec
            dec.valueDomain = vd
            dec.save()
        return HttpResponseRedirect(reverse("aristotle:%s"%dec.url_name,args=[dec.id]))
