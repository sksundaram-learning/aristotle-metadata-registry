from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

class GenericAutocomplete(autocomplete.Select2QuerySetView):
    model = None
    
    def dispatch(self, request, *args, **kwargs):
        print args, kwargs
        if 'app_name' in kwargs.keys() and 'model_name' in kwargs.keys():
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

        template = get_template("autocomplete_light/item.html")
        context = Context({"item": result})
        return template.render(context)
