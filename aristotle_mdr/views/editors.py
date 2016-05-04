from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.db import transaction
from django.forms import ValidationError, ModelForm
from django.forms.models import modelformset_factory, inlineformset_factory
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.template import RequestContext, TemplateDoesNotExist
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView
from django.utils import timezone
from django.utils.decorators import method_decorator

import reversion
from reversion.revisions import default_revision_manager

from aristotle_mdr.perms import user_can_view, user_can_edit, user_can_change_status
from aristotle_mdr.utils import cache_per_item_user, concept_to_clone_dict, concept_to_dict, construct_change_message, url_slugify_concept
from aristotle_mdr import forms as MDRForms
from aristotle_mdr import models as MDR

import logging

logger = logging.getLogger(__name__)
logger.debug("Logging started for " + __name__)


class PermissionFormView(FormView):
    item = None

    def dispatch(self, request, *args, **kwargs):
        if not self.item:
            self.item = get_object_or_404(
                MDR._concept, pk=self.kwargs['iid']
            ).item
        self.model = self.item.__class__
        if not user_can_edit(self.request.user, self.item):
            if request.user.is_anonymous():
                return redirect(reverse('friendly_login') + '?next=%s' % request.path)
            else:
                raise PermissionDenied
        return super(PermissionFormView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(PermissionFormView, self).get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
        })
        return kwargs

    def get_context_data(self, form, **kwargs):
        context = super(PermissionFormView, self).get_context_data(form=form, **kwargs)
        context.update({'model': self.model._meta.model_name,
                        'app_label': self.model._meta.app_label,
                        'item': self.item})
        return context


class EditItemView(PermissionFormView):
    template_name = "aristotle_mdr/actions/advanced_editor.html"

    def get_form_class(self):
        return MDRForms.wizards.subclassed_edit_modelform(self.model)

    def get_form_kwargs(self):
        kwargs = super(EditItemView, self).get_form_kwargs()
        kwargs.update({
            'instance': self.item,
        })
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        slot_formset = None

        new_wg = request.POST.get('workgroup', None)
        workgroup_changed = not(str(self.item.workgroup.pk) == (new_wg))

        if form.is_valid():
            workgroup_changed = self.item.workgroup.pk != form.cleaned_data['workgroup'].pk

            with transaction.atomic(), reversion.revisions.create_revision():
                item = form.save(commit=False)
                slot_formset = self.get_slots_formset()(request.POST, request.FILES, item.concept)

                if slot_formset.is_valid():

                    # Save the slots
                    slot_formset.save()

                    # Save the change comments
                    reversion.revisions.set_user(request.user)
                    change_comments = form.data.get('change_comments', None)
                    if not change_comments:
                        change_comments = construct_change_message(request, form, [slot_formset])
                    reversion.revisions.set_comment(change_comments)

                    item.save()
                    return HttpResponseRedirect(url_slugify_concept(self.item))

        return self.form_invalid(form, slot_formset)

    def get_slots_formset(self):
        from aristotle_mdr.contrib.slots.forms import slot_inlineformset_factory
        return slot_inlineformset_factory(model=self.model)

    def form_invalid(self, form, slots_FormSet=None):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        return self.render_to_response(self.get_context_data(form=form, slots_FormSet=slots_FormSet))

    def get_context_data(self, form, **kwargs):
        from aristotle_mdr.contrib.slots.models import Slot, SlotDefinition
        context = super(EditItemView, self).get_context_data(form=form, **kwargs)
        if kwargs.get('slots_FormSet', None):
            context['slots_FormSet'] = kwargs['slots_FormSet']
        else:
            context['slots_FormSet'] = self.get_slots_formset()(
                queryset=Slot.objects.filter(concept=self.item.id),
                instance=self.item.concept
                )
        context['show_slots_tab'] = True
        context['concept_slots'] = SlotDefinition.objects.filter(app_label=self.model._meta.app_label, concept_type=self.model._meta.model_name)
        return context


class CloneItemView(PermissionFormView):
    template_name = "aristotle_mdr/create/clone_item.html"

    def dispatch(self, request, *args, **kwargs):
        self.item_to_clone = get_object_or_404(
            MDR._concept, pk=self.kwargs['iid']
        ).item
        self.item = self.item_to_clone
        return super(CloneItemView, self).dispatch(request, *args, **kwargs)

    def get_form_class(self):
        return MDRForms.wizards.subclassed_clone_modelform(self.model)

    def get_form_kwargs(self):
        kwargs = super(CloneItemView, self).get_form_kwargs()
        kwargs.update({
            'initial': concept_to_clone_dict(self.item_to_clone)
        })
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            with transaction.atomic(), reversion.revisions.create_revision():
                new_clone = form.save()
                reversion.revisions.set_user(self.request.user)
                reversion.revisions.set_comment("Cloned from %s (id: %s)" % (self.item_to_clone.name, str(self.item_to_clone.pk)))
                return HttpResponseRedirect(url_slugify_concept(new_clone))
        else:
            return self.form_invalid(form)


def valuedomain_value_edit(request, iid, value_type):
    item = get_object_or_404(MDR.ValueDomain, pk=iid).item
    if not user_can_edit(request.user, item):
        if request.user.is_anonymous():
            return redirect(reverse('friendly_login') + '?next=%s' % request.path)
        else:
            raise PermissionDenied
    value_model = {
        'permissible': MDR.PermissibleValue,
        'supplementary': MDR.SupplementaryValue
    }.get(value_type, None)
    if not value_model:
        raise Http404

    num_values = value_model.objects.filter(valueDomain=item.id).count()
    if num_values > 0:
        extra = 0
    else:
        extra = 1
    ValuesFormSet = modelformset_factory(
        value_model,
        can_delete=True,  # dont need can_order is we have an order field
        fields=('order', 'value', 'meaning'),
        extra=extra
        )
    if request.method == 'POST':
        formset = ValuesFormSet(request.POST, request.FILES)
        if formset.is_valid():
                with transaction.atomic(), reversion.revisions.create_revision():
                    item.save()  # do this to ensure we are saving reversion records for the value domain, not just the values
                    formset.save(commit=False)
                    for form in formset.forms:
                        if form['value'].value() == '' and form['meaning'].value() == '':
                            continue  # Skip over completely blank entries.
                        if form['id'].value() not in [deleted_record['id'].value() for deleted_record in formset.deleted_forms]:
                            value = form.save(commit=False)  # Don't immediately save, we need to attach the value domain
                            value.valueDomain = item
                            value.save()
                    for obj in formset.deleted_objects:
                        obj.delete()
                    # formset.save(commit=True)
                    reversion.revisions.set_user(request.user)
                    reversion.revisions.set_comment(construct_change_message(request, None, [formset]))

                return redirect(reverse("aristotle_mdr:item", args=[item.id]))
    else:
        formset = ValuesFormSet(
            queryset=value_model.objects.filter(valueDomain=item.id),
            initial=[{'order': num_values, 'value': '', 'meaning': ''}]
            )
    return render(
        request,
        "aristotle_mdr/actions/edit_value_domain_values.html",
        {'item': item, 'formset': formset, 'value_type': value_type, 'value_model': value_model}
    )
