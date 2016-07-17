from django.apps import apps
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from model_utils import Choices
from model_utils.models import TimeStampedModel

from aristotle_mdr import models as MDR


class PublicationRecord(TimeStampedModel):
    VISIBILITY = Choices(
        (0, 'public', _('Public')),
        (1, 'active', _('Logged in users only')),
    )
    visibility = models.IntegerField(
        choices=VISIBILITY,
        default=VISIBILITY.public,
        help_text=_('Status of a review')
    )
    user = models.ForeignKey(User)
    concept = models.OneToOneField(MDR._concept, related_name='publicationrecord')
    publication_date = models.DateField(default=now, blank=True)
    note = models.TextField(null=True, blank=True)


def concept_visibility_query(user):
    q = Q(
        publicationrecord__visibility=PublicationRecord.VISIBILITY.public,
        publication_date__gte=now()
    )
    if user.is_active:
        q |= Q(
            publicationrecord__visibility=PublicationRecord.VISIBILITY.active,
            publication_date__gte=now()
        )
    return q


def concept_public_query():
    return Q(publicationrecord__visibility=PublicationRecord.VISIBILITY.public)


post_save.connect(MDR.recache_concept_states, sender=PublicationRecord)
post_delete.connect(MDR.recache_concept_states, sender=PublicationRecord)
