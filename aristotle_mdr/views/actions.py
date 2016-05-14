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
from django.utils.decorators import method_decorator
import datetime

import reversion
from reversion.revisions import default_revision_manager

from aristotle_mdr.perms import user_can_view, user_can_edit, user_can_change_status
from aristotle_mdr.utils import cache_per_item_user, concept_to_dict, construct_change_message, url_slugify_concept
from aristotle_mdr import forms as MDRForms
from aristotle_mdr import exceptions as registry_exceptions
from aristotle_mdr import models as MDR
from aristotle_mdr.forms import actions

class ItemSubpageFormView(FormView):
    def get_context_data(self, **kwargs):
        kwargs = super(ItemSubpageFormView, self).get_context_data(**kwargs)
        kwargs['item'] = self.get_item()
        return kwargs

    def get_item(self):
        self.item = get_object_or_404(MDR._concept, pk=self.kwargs['iid']).item
        if not self.item.can_view(self.request.user):
            raise PermissionDenied
        return self.item

    def dispatch(self, *args, **kwargs):
        self.item = self.get_item()
        return super(ItemSubpageFormView, self).dispatch(*args, **kwargs)

class SubmitForReviewView(ItemSubpageFormView):
    form_class = actions.RequestReviewForm
    template_name = "aristotle_mdr/actions/request_review.html"

    def get_context_data(self, **kwargs):
        kwargs = super(SubmitForReviewView, self).get_context_data(**kwargs)
        kwargs['reviews'] = self.get_item().review_requests.filter(status=MDR.REVIEW_STATES.submitted).all()
        return kwargs

    def get_form_kwargs(self):
        kwargs = super(SubmitForReviewView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
        
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        item = self.get_item()

        if form.is_valid():
            review = form.save(commit=False)
            review.requester = request.user
            review.save()
            review.concepts.add(item)
            message = _("Review submitted")
            messages.add_message(request, messages.INFO, message)
            return HttpResponseRedirect(item.get_absolute_url())
        else:
            return self.form_invalid(form)
