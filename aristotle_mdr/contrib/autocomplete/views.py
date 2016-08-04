from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from aristotle_mdr import models
from dal import autocomplete
from django.template.loader import get_template
from django.template import Context


class GenericAutocomplete(autocomplete.Select2QuerySetView):
    model = None
    template_name = "autocomplete_light/item.html"

    def dispatch(self, request, *args, **kwargs):
        if kwargs.get('app_name', None) and kwargs.get('model_name', None):
            self.model = get_object_or_404(
                ContentType, app_label=kwargs['app_name'], model=kwargs['model_name']
            ).model_class()
        return super(GenericAutocomplete, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return self.model.objects.none()

        qs = self.model.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs

    def get_result_label(self, result):
        """Return the label of a result."""

        template = get_template(self.template_name)
        context = Context({"result": result})
        return template.render(context)


class GenericConceptAutocomplete(GenericAutocomplete):
    model = models._concept
    template_name = "autocomplete_light/concept.html"

    def get_queryset(self):
        if not self.request.user.is_authenticated():
            qs = self.model.objects.public()
        else:
            qs = self.model.objects.visible(self.request.user)

        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs
