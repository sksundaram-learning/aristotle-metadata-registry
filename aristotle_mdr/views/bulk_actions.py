from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.template import RequestContext, TemplateDoesNotExist
from django.template.defaultfilters import slugify
from django.template.loader import select_template
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView
from django.utils import timezone
import datetime

import reversion
from reversion.revisions import default_revision_manager

from aristotle_mdr.perms import user_can_view, user_can_edit, user_can_change_status
from aristotle_mdr.utils import cache_per_item_user, concept_to_dict, construct_change_message, url_slugify_concept
from aristotle_mdr import forms as MDRForms
from aristotle_mdr import exceptions as registry_exceptions
from aristotle_mdr import models as MDR

from haystack.views import SearchView


"""
Dear future Sam,
Finish this off, move it to CBVs for issue 283
Develop a code for codfying the queryset, check against 'visible' because they will always be concepts

Then pass this into the form. It should work? Probably.
Love,
past Sam.
"""

legal_queryset_bases = {
    "wkgrp": MDR.Workgroup,
    "regauth": MDR.RegistrationAuthority,
}


# TODO: Check permissions for this
@login_required
class BulkAction(FormView):
    def post(self, request, *args, **kwargs):
        actions = get_bulk_actions()
        action = request.POST.get("bulkaction", None)

        if action is None:
            # no action, messed up, redirect
            return HttpResponseRedirect(url)
        action_form = actions[action]['form']
        if action_form.confirm_page is None:
            # if there is no confirm page or extra details required, do the action and redirect
            form = action_form(request.POST, user=request.user)  # A form bound to the POST data
            if form.is_valid():
                message = form.make_changes()
                messages.add_message(request, messages.INFO, message)
            else:
                messages.add_message(request, messages.ERROR, form.errors)
            return HttpResponseRedirect(url)
        else:
            form = action_form(request.POST, user=request.user)
            items = []
            if form.is_valid():
                items = form.cleaned_data['items']

            confirmed = request.POST.get("confirmed", None)

            if confirmed:
                # We've passed the confirmation page, try and save.
                form = action_form(request.POST, user=request.user, items=items)  # A form bound to the POST data
                # there was an error with the form redisplay
                if form.is_valid():
                    message = form.make_changes()
                    messages.add_message(request, messages.INFO, message)
                    return HttpResponseRedirect(url)
            else:
                # we need a confirmation, render the next form
                form = action_form(request.POST, user=request.user, items=items)
            return render(
                request,
                action_form.confirm_page,
                {
                    "items": items,
                    "form": form,
                    "next": url,
                    "action": action,
                }
            )
        return HttpResponseRedirect(url)


def bulk_action(request):
    url = request.GET.get("next", "/")
    message = ""
    if request.method == 'POST':  # If the form has been submitted...
        actions = get_bulk_actions()
        action = request.POST.get("bulkaction", None)

        if action is None:
            # no action, messed up, redirect
            return HttpResponseRedirect(url)
        action_form = actions[action]['form']
        if action_form.confirm_page is None:
            # if there is no confirm page or extra details required, do the action and redirect
            form = action_form(request.POST, user=request.user)  # A form bound to the POST data
            if form.is_valid():
                message = form.make_changes()
                messages.add_message(request, messages.INFO, message)
            else:
                messages.add_message(request, messages.ERROR, form.errors)
            return HttpResponseRedirect(url)
        else:
            form = action_form(request.POST, user=request.user)
            items = []
            if form.is_valid():
                items = form.cleaned_data['items']

            confirmed = request.POST.get("confirmed", None)

            if confirmed:
                # We've passed the confirmation page, try and save.
                form = action_form(request.POST, user=request.user, items=items)  # A form bound to the POST data
                # there was an error with the form redisplay
                if form.is_valid():
                    message = form.make_changes()
                    messages.add_message(request, messages.INFO, message)
                    return HttpResponseRedirect(url)
            else:
                # we need a confirmation, render the next form
                form = action_form(request.POST, user=request.user, items=items)
            return render(
                request,
                action_form.confirm_page,
                {
                    "items": items,
                    "form": form,
                    "next": url,
                    "action": action,
                }
            )
    return HttpResponseRedirect(url)


def get_bulk_actions():
    import re
    config = getattr(settings, 'ARISTOTLE_SETTINGS', {})
    if not hasattr(get_bulk_actions, 'actions') or not get_bulk_actions.actions:
        actions = {}
        for action_name, form in config.get('BULK_ACTIONS', {}).items():
            if not re.search('^[a-zA-Z0-9\_\.]+$', form):  # pragma: no cover
                # Invalid downloadType
                raise registry_exceptions.BadBulkActionModuleName("Bulk action isn't a valid Python module name.")

            module, form = form.rsplit('.', 1)
            exec('from %s import %s as f' % (module, form))

            # We need to make this a dictionary, not a class as otherwise
            # the template engire tries to instantiate it.
            frm = {'form': f}
            for prop in ['classes', 'can_use', 'text']:
                frm[prop] = getattr(f, prop, None)
            actions[action_name] = frm
        # Save to method to prevent having to reimport everytime
        get_bulk_actions.actions = actions
    return get_bulk_actions.actions
