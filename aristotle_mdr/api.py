from aristotle_mdr import models
from aristotle_mdr.utils import url_slugify_concept
from tastypie import fields
from tastypie.authorization import DjangoAuthorization, ReadOnlyAuthorization
from tastypie.authentication import MultiAuthentication, BasicAuthentication, SessionAuthentication
from tastypie.resources import ModelResource


class GlossaryListResource(ModelResource):
    url = fields.CharField(readonly=True)
    class Meta:
        queryset = models.GlossaryItem.objects.all()
        resource_name = 'glossarylist'
        fields = ['id','name','description','url']
        authorization = ReadOnlyAuthorization()
        authentication = MultiAuthentication(BasicAuthentication(), SessionAuthentication())
        filtering = {
            'name': ('exact', 'startswith', 'contains',),
            'id': ('exact','in'),
        }

    def dehydrate_url(self,bundle):
        return url_slugify_concept(bundle.obj)

    def get_object_list(self, request):
        print request.user
        return super(GlossaryListResource, self).get_object_list(request).visible(request.user)
