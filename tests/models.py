import uuid

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from hitcount.models import HitCountMixin
from hitcount.settings import MODEL_HITCOUNT


class UUIDArticle(HitCountMixin, models.Model):
    """A model with a UUID primary key."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    hit_count_generic = GenericRelation(
        MODEL_HITCOUNT, object_id_field='object_pk',
        related_query_name='hit_count_generic_relation')

    def __str__(self):
        return str(self.pk)


class SlugArticle(HitCountMixin, models.Model):
    """A model with a string primary key."""
    slug = models.CharField(max_length=100, primary_key=True)
    hit_count_generic = GenericRelation(
        MODEL_HITCOUNT, object_id_field='object_pk',
        related_query_name='hit_count_generic_relation')

    def __str__(self):
        return self.slug
