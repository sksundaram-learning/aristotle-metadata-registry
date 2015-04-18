from django.conf.urls import patterns, include, url

# Below are the 'recommended' locations for the paths to aristotle extensions.
# At this point the 'glossary' extension *requires* being in the root at `/glossary/`.
urlpatterns = patterns('',
    url(r'^', include('aristotle_mdr.urls')),
#    url(r'^ddi/', include('aristotle_ddi_utils.urls',app_name="aristotle_ddi_utils",namespace="aristotle_ddi_utils")),
#    url(r'^dse/', include('aristotle_dse.urls',app_name="aristotle_dse",namespace="aristotle_dse")),
#    url(r'^glossary/', include('aristotle_glossary.urls',app_name="aristotle_glossary",namespace="glossary")),
    )