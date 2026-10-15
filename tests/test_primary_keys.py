"""HitCount works for any primary key type, not just integers."""
import uuid
from importlib import import_module

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.db import connection
from django.template import Context, Template
from django.test import RequestFactory, TestCase

from hitcount.models import Hit
from hitcount.utils import get_hitcount_model
from hitcount.views import HitCountMixin

from blog.models import Post
from tests.models import SlugArticle, UUIDArticle

HitCount = get_hitcount_model()


class PrimaryKeyTypesTests(TestCase):

    def count_hit(self, obj):
        request = RequestFactory().get('/', REMOTE_ADDR='127.0.0.1')
        request.session = import_module(settings.SESSION_ENGINE).SessionStore()
        request.user = AnonymousUser()
        return HitCountMixin.hit_count(request, HitCount.objects.get_for_object(obj))

    def objects(self):
        return [
            Post.objects.create(title='int pk', content=''),
            UUIDArticle.objects.create(),
            SlugArticle.objects.create(slug='a-string-pk'),
        ]

    def test_counting(self):
        for obj in self.objects():
            with self.subTest(model=type(obj).__name__):
                self.assertTrue(self.count_hit(obj).hit_counted)
                self.assertEqual(obj.hit_count.hits, 1)
                self.assertEqual(obj.hit_count.hits_in_last(days=1), 1)
                self.assertEqual(HitCount.objects.get_for_object(obj).content_object, obj)

    def test_objects_do_not_share_hitcounts(self):
        objs = self.objects()
        for obj in objs:
            self.count_hit(obj)
        self.assertEqual(HitCount.objects.count(), 3)
        self.assertEqual(Hit.objects.count(), 3)

    def test_template_tag(self):
        for obj in self.objects():
            with self.subTest(model=type(obj).__name__):
                self.count_hit(obj)
                out = Template('{% load hitcount_tags %}{% get_hit_count for obj %}').render(
                    Context({'obj': obj}))
                self.assertEqual(out, '1')

    def test_order_and_filter_by_hits(self):
        """Joins through the GenericRelation (was broken on PostgreSQL with text keys)."""
        for model, make in ((Post, lambda: Post.objects.create(title='t', content='')),
                            (SlugArticle, lambda: SlugArticle.objects.create(slug=str(uuid.uuid4()))),
                            (UUIDArticle, UUIDArticle.objects.create)):
            with self.subTest(model=model.__name__):
                if model is UUIDArticle and not connection.features.has_native_uuid_field:
                    # SQLite / MySQL store UUIDs as 32 hex chars, while generic
                    # relations use the dashed form: DB-side joins can't match.
                    continue
                busy, quiet, never = make(), make(), make()
                self.count_hit(busy)
                self.count_hit(busy)
                self.count_hit(quiet)

                ordered = list(model.objects.filter(hit_count_generic__hits__gt=0)
                               .order_by('-hit_count_generic__hits'))
                self.assertEqual(ordered, [busy, quiet])
                self.assertNotIn(never, ordered)

    def test_generic_relation_reverse_lookup(self):
        """obj.hit_count_generic works for every key type on every database."""
        for obj in self.objects():
            with self.subTest(model=type(obj).__name__):
                self.count_hit(obj)
                self.assertEqual(obj.hit_count_generic.get().hits, 1)
                prefetched = type(obj).objects.prefetch_related('hit_count_generic').get(pk=obj.pk)
                self.assertEqual([hc.hits for hc in prefetched.hit_count_generic.all()], [1])
