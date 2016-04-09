from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView, TemplateView
from aristotle_mdr.utils import get_concepts_for_apps


class BrowseApps(TemplateView):
    template_name = "aristotle_mdr_browse/apps_list.html"

    def get_context_data(self, **kwargs):
        context = super(BrowseApps, self).get_context_data(**kwargs)

        aristotle_apps = getattr(settings, 'ARISTOTLE_SETTINGS', {}).get('CONTENT_EXTENSIONS', [])
        aristotle_apps += ["aristotle_mdr"]
        out = {}

        for m in get_concepts_for_apps(aristotle_apps):
            # Only output subclasses of 11179 concept
            app_models = out.get(m.app_label, {'app': None, 'models': []})
            if app_models['app'] is None:
                app_models['app'] = getattr(
                    apps.get_app_config(m.app_label),
                    'verbose_name',
                    _("No name")  # Where no name is configured in the app_config, set a dummy so we don't keep trying
                )

            app_models['models'].append((m, m.model_class()))
            out[m.app_label] = app_models
        context['apps'] = out
        return context


class AppBrowser(ListView):
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(AppBrowser, self).get_context_data(**kwargs)
        context['app_label'] = self.kwargs['app']
        context['app'] = apps.get_app_config(self.kwargs['app'])
        return context


class BrowseModels(AppBrowser):
    template_name = "aristotle_mdr_browse/model_list.html"
    context_object_name = "model_list"
    paginate_by = 25

    def get_queryset(self):
        app = self.kwargs['app']
        models = ContentType.objects.filter(app_label=app)
        models = get_concepts_for_apps([app])
        return models


class BrowseConcepts(AppBrowser):
    _model = None
    paginate_by = 25

    @property
    def model(self):
        if self._model is None:
            app = self.kwargs['app']
            model = self.kwargs['model']
            ct = ContentType.objects.filter(app_label=app, model=model)
            if not ct:
                raise Http404
            else:
                self._model = ct.first().model_class()
        return self._model

    def get_queryset(self, *args, **kwargs):
        queryset = super(BrowseConcepts, self).get_queryset(*args, **kwargs)
        return queryset.visible(self.request.user)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(BrowseConcepts, self).get_context_data(**kwargs)
        context['model'] = self.model
        context['model_name'] = self.model._meta.model_name
        return context

    def get_template_names(self):
        names = super(BrowseConcepts, self).get_template_names()
        names.append('aristotle_mdr_browse/list.html')
        return names

    def get_ordering(self):
        _order_map = {
            'name': 'name',
            'wg': 'workgroup__name',
            'mod': 'modified',
        }
        order_map = {}
        order_map.update([(k + '_asc', v) for k, v in _order_map.items()])
        order_map.update([(k + '_desc', "-" + v) for k, v in _order_map.items()])

        order = self.request.GET.get('order', 'name')
        return order_map.get(order)
