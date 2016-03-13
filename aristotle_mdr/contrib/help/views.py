from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView, TemplateView, DetailView
from aristotle_mdr.utils import get_concepts_for_apps

from aristotle_mdr.contrib.help.models import ConceptHelp

class ConceptHelpView(DetailView):
    template_name = "aristotle_mdr_help/concept_help.html"

    def get_object(self, queryset=None):
        app = self.kwargs['app']
        model = self.kwargs['model']
        return get_object_or_404(ConceptHelp,app_label=app,concept_type=model)

    def get_context_data(self, **kwargs):
        context = super(ConceptHelpView, self).get_context_data(**kwargs)
        
        app = self.kwargs['app']
        model = self.kwargs['model']

        ct = ContentType.objects.get(app_label=app,model=model)
        context['model'] = ct.model_class()
        context['app'] = apps.get_app_config(app)
        return context

#class AppHelpView(TemplateView):
#    template_name = "aristotle_mdr_help/app_help.html"
