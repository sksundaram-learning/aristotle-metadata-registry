from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.template import RequestContext, TemplateDoesNotExist
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView
from django.utils.decorators import method_decorator
import datetime

import reversion
from reversion.revisions import default_revision_manager

from aristotle_mdr import perms
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


class ReviewActionMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        review = self.get_review()
        if not perms.user_can_view_review(self.request.user,review):
            raise PermissionDenied
        return super(ReviewActionMixin, self).dispatch(*args, **kwargs)

    def get_review(self):
        self.review = get_object_or_404(MDR.ReviewRequest, pk=self.kwargs['review_id'])
        return self.review

    def get_context_data(self, **kwargs):
        kwargs = super(ReviewActionMixin, self).get_context_data(**kwargs)
        kwargs['review'] = self.get_review()
        return kwargs

    def get_form_kwargs(self):
        kwargs = super(ReviewActionMixin, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class ReviewRejectView(ReviewActionMixin, FormView):
    form_class = actions.RequestReviewRejectForm
    template_name = "aristotle_mdr/user/user_request_reject.html"

    def get_form_kwargs(self):
        kwargs = super(ReviewRejectView, self).get_form_kwargs()
        kwargs['instance'] = self.get_review()
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = request.user
            review.status = MDR.REVIEW_STATES.rejected
            review.save()
            message = _("Review successfully rejected")
            messages.add_message(request, messages.INFO, message)
            return HttpResponseRedirect(reverse('aristotle_mdr:userReadyForReview'))
        else:
            return self.form_invalid(form)


class ReviewAcceptView(ReviewActionMixin, FormView):
    form_class = actions.RequestReviewAcceptForm
    template_name = "aristotle_mdr/user/user_request_accept.html"

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        review = self.get_review()

        if form.is_valid():
            review.reviewer = request.user
            review.response = form.cleaned_data['response']
            review.status = MDR.REVIEW_STATES.accepted
            review.save()
            message = form.make_changes(items=review.concepts.all())
            # message = _("Review accepted")
            messages.add_message(request, messages.INFO, message)
            return HttpResponseRedirect(reverse('aristotle_mdr:userReadyForReview'))
        else:
            return self.form_invalid(form)
