from aristotle_mdr.views import render_if_user_can_view
from django.views.generic import TemplateView
import extension_test

class DynamicTemplateView(TemplateView):
    def get_template_names(self):
        return ['extension_test/static/%s.html' % self.kwargs['template']]
