from inplaceeditform_extra_fields.fields import AdaptorTinyMCEField
from inplaceeditform_extra_fields.widgets import TinyMCE
from inplaceeditform.fields import AdaptorChoicesField
from inplaceeditform.commons import apply_filters

from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.forms.extras import widgets

conf = dict(
    toolbar1=(" | undo redo | bold italic | "
             "subscript superscript | " #spellchecker | "
             "bullist numlist | link image glossary"),
    toolbar2=("save cancel | code |  "),
    #plugins= "spellchecker",
    plugins= "code link image",
    #link_list='/glossary/ajaxlist',
    menubar=False)

class AristotleRichTextField(AdaptorTinyMCEField):
    @property
    def name(self):
        return 'aristotlerichtextfield'

    @property
    def TinyMCE(self):
        return AristotleTinyMCE

class AristotleTinyMCE(TinyMCE):
    def __init__(self, extra_mce_settings=None,
                 config=None, width=None, *args, **kwargs):
        super(AristotleTinyMCE, self).__init__(extra_mce_settings=conf,*args, **kwargs)
        self.mce_settings['setup'] = ''.join(render_to_string('aristotle_mdr/tinymce/setup.js', config).splitlines())
