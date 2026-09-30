import unittest
from datetime import timedelta
from unittest import mock

import django
from django.template import Context, RequestContext, Template, TemplateSyntaxError
from django.test import RequestFactory, TestCase
from django.utils import timezone

from hitcount.models import Hit
from hitcount.utils import get_hitcount_model

from blog.models import Post

HitCount = get_hitcount_model()


class TemplateTagGetHitCountTests(TestCase):
    fixtures = ['initial_data.json']

    def setUp(self):
        self.post = Post.objects.get(pk=1)
        hit_count = HitCount.objects.create(content_object=self.post)

        for x in range(10):
            created = timezone.now() - timedelta(minutes=x * 15)
            with mock.patch('django.utils.timezone.now') as mock_now:
                mock_now.return_value = created

                Hit.objects.create(hitcount=hit_count)

    def test_returns_0(self):
        """
        {% get_hit_count for post%}

        If no HitCount object exists, the template tag should return zero
        and have created an object for the next time.
        """
        # no HitCounts to start
        self.assertEqual(len(HitCount.objects.all()), 1)
        post2 = Post.objects.create(title='second', content='post!')

        out = Template(
            "{% load hitcount_tags %}"
            "{% get_hit_count for post %}"
        ).render(Context({
            "post": post2
        }))

        # zero hits, but now one object
        self.assertEqual(str(0), out)
        self.assertEqual(len(HitCount.objects.all()), 2)

    def test_returns_10(self):
        """
        {% get_hit_count for post%}

        Test tag with multiple hits.
        """
        out = Template(
            "{% load hitcount_tags %}"
            "{% get_hit_count for post %}"
        ).render(Context({
            "post": self.post
        }))

        self.assertEqual(str(10), out)

    def test_as_variable(self):
        """
        {% get_hit_count for post as hits %}

        Test tag with output as variable.
        """
        out = Template(
            "{% load hitcount_tags %}"
            "{% get_hit_count for post as hits %}"
            "Total Hits: {{ hits }}"
        ).render(Context({
            "post": self.post
        }))

        self.assertEqual("Total Hits: 10", out)

    def test_within(self):
        """
        {% get_hit_count for [object] within [ex: "hours=1"] %}

        Test tag with multiple hits.
        """
        out = Template(
            "{% load hitcount_tags %}"
            '{% get_hit_count for post within "hours=1" %}'
        ).render(Context({
            "post": self.post
        }))

        self.assertEqual(str(4), out)

    def test_within_multiple_time_args(self):
        """
        {% get_hit_count for [object] within [ex: "hours=1,minutes=30"] %}

        Test tag with multiple hits and multiple time args.
        """
        out = Template(
            "{% load hitcount_tags %}"
            '{% get_hit_count for post within "hours=1,minutes=30" %}'
        ).render(Context({
            "post": self.post
        }))

        self.assertEqual(str(6), out)

    def test_within_multiple_time_args_without_quotes(self):
        """
        {% get_hit_count for [object] within [ex: hours=1,minutes=30] %}

        Test tag with multiple hits and multiple time args without quotes.
        """
        out = Template(
            "{% load hitcount_tags %}"
            '{% get_hit_count for post within hours=1,minutes=30 %}'
        ).render(Context({
            "post": self.post
        }))

        self.assertEqual(str(6), out)

    def test_within_as_var(self):
        """
        {% get_hit_count for [object] within [ex: "hours=1"] as [var] %}

        Test tag with multiple hits, get as a variable.
        """
        out = Template(
            '{% load hitcount_tags %}'
            '{% get_hit_count for post within "hours=1" as hits %}'
            'Total Hits in last hour: {{ hits }}'
        ).render(Context({
            "post": self.post
        }))

        self.assertEqual('Total Hits in last hour: 4', out)

    def test_within_multiple_time_args_as_var(self):
        """
        {% get_hit_count for [object] within [ex: "hours=1,minutes=30"] as [var] %}

        Test tag with multiple hits and multiple time args as a variable.
        """
        out = Template(
            "{% load hitcount_tags %}"
            '{% get_hit_count for post within "hours=1,minutes=30" as hits %}'
            'Total Hits in last 1h 15m: {{ hits }}'
        ).render(Context({
            "post": self.post
        }))

        self.assertEqual("Total Hits in last 1h 15m: 6", out)

    def test_get_js_variables(self):
        """
        {% get_hit_count_js_variables for [object] as [var_name] %}

        Test retrieval of javascript variables.
        """
        out = Template(
            "{% load hitcount_tags %}"
            '{% get_hit_count_js_variables for post as hit_count_js %}'
            'pk: {{ hit_count_js.pk }} || '
            'url: {{ hit_count_js.ajax_url }} || '
            'hits: {{ hit_count_js.hits }}'
        ).render(Context({
            "post": self.post
        }))

        pk = self.post.hit_count.pk
        self.assertEqual('pk: %s || url: /hitcount/hit/ajax/ || hits: 10' % pk, out)

    def test_insert_js_variables(self):
        """
        {% insert_hit_count_js_variables for [object] %}

        Test for writing of js variables directly onto the template.
        """
        out = Template(
            "{% load hitcount_tags %}"
            '{% insert_hit_count_js_variables for post %}'
        ).render(Context({
            "post": self.post
        }))

        pk = self.post.hit_count.pk
        self.assertEqual(
            '<script type="text/javascript">\n'
            'var hitcountJS = {hitcountPK : \'%s\',hitcountURL :'
            ' \'/hitcount/hit/ajax/\'};\n</script>' % pk, out)

    def test_parsing_errors(self):
        render = lambda t, c: Template(t).render(Context(c))

        # invalid date/time
        self.assertRaises(
            TemplateSyntaxError, render,
            '{% load hitcount_tags %}{% get_hit_count for post within "foo=1,bar=30" %}',
            {"post": self.post})

        # non-existent context variable
        self.assertRaises(
            TemplateSyntaxError, render,
            "{% load hitcount_tags %}{% get_hit_count for post %}",
            {"post_doesnt_context": self.post})

        # wrong number of args
        self.assertRaises(
            TemplateSyntaxError, render,
            '{% load hitcount_tags %}{% get_hit_count post %}',
            {"post": self.post})

        # not passed valid object
        self.assertRaises(
            TemplateSyntaxError, render,
            '{% load hitcount_tags %}{% get_hit_count post %}',
            {"post": 'bob the baker'})

    def test_parsing_errors_get_js_variables(self):
        render = lambda t, c: Template(t).render(Context(c))

        # wrong number of variables
        self.assertRaises(
            TemplateSyntaxError, render,
            "{% load hitcount_tags %}{% get_hit_count_js_variables as hit_count_js %}",
            {"post_variable_wrong": self.post})

        # wrong number of variables
        self.assertRaises(
            TemplateSyntaxError, render,
            "{% load hitcount_tags %}{% get_hit_count_js_variables as hit_count_js %}",
            {"post": self.post})

        # a string not an object
        self.assertRaises(
            TemplateSyntaxError, render,
            "{% load hitcount_tags %}{% get_hit_count_js_variables for post as hit_count_js %}",
            {"post": 'bob the baker'})

    def test_parsing_errors_insert_js_variables(self):
        render = lambda t, c: Template(t).render(Context(c))

        # wrong number of variables
        self.assertRaises(
            TemplateSyntaxError, render,
            "{% load hitcount_tags %}{% insert_hit_count_js_variables post %}",
            {"post": self.post})

        # non-existent context variable
        self.assertRaises(
            TemplateSyntaxError, render,
            "{% load hitcount_tags %}{% insert_hit_count_js_variables for post %}",
            {"post_doesnt_context": self.post})

        # a string not an object
        self.assertRaises(
            TemplateSyntaxError, render,
            "{% load hitcount_tags %}{% insert_hit_count_js_variables for post %}",
            {"post": 'bob the baker'})


class TemplateTagInsertHitCountJSTests(TestCase):

    def setUp(self):
        self.post = Post.objects.create(title='js', content='post')

    def render(self, template, context):
        return Template('{% load hitcount_tags %}' + template).render(Context(context))

    def test_insert_js(self):
        out = self.render('{% insert_hit_count_js for post %}', {'post': self.post})
        pk = self.post.hit_count.pk

        self.assertIn('fetch("/hitcount/hit/ajax/"', out)
        self.assertIn('encodeURIComponent("%s")' % pk, out)
        self.assertIn('"X-Requested-With": "XMLHttpRequest"', out)
        self.assertIn('hitcount:counted', out)
        self.assertNotIn('jQuery', out)
        self.assertNotIn('console.log', out)

    def test_insert_js_debug(self):
        out = self.render('{% insert_hit_count_js for post debug %}', {'post': self.post})
        self.assertIn('console.log("django-hitcount: AJAX POST succeeded.", data);', out)
        self.assertIn('console.log("django-hitcount: AJAX POST failed.", error);', out)

    def test_insert_js_uses_context_csrf_token(self):
        out = self.render('{% insert_hit_count_js for post %}',
                          {'post': self.post, 'csrf_token': 'abc123'})
        self.assertIn('var csrfToken = "abc123";', out)

    def test_insert_js_ignores_missing_csrf_token(self):
        out = self.render('{% insert_hit_count_js for post %}',
                          {'post': self.post, 'csrf_token': 'NOTPROVIDED'})
        self.assertIn('var csrfToken = "";', out)

    def test_insert_js_escapes_csrf_token(self):
        out = self.render('{% insert_hit_count_js for post %}',
                          {'post': self.post, 'csrf_token': '"</script>'})
        self.assertIn('var csrfToken = "\\u0022\\u003C/script\\u003E";', out)

    def test_parsing_errors(self):
        with self.assertRaises(TemplateSyntaxError):
            self.render('{% insert_hit_count_js post %}', {'post': self.post})
        with self.assertRaises(TemplateSyntaxError):
            self.render('{% insert_hit_count_js for post verbose %}', {'post': self.post})
        with self.assertRaises(TemplateSyntaxError):
            self.render('{% insert_hit_count_js for post %}', {'post': 'bob the baker'})


@unittest.skipIf(django.VERSION < (6, 0), 'Django 6.0 added built-in CSP support')
class TemplateTagCSPNonceTests(TestCase):

    def setUp(self):
        from django.utils.csp import LazyNonce

        self.post = Post.objects.create(title='csp', content='post')
        self.request = RequestFactory().get('/')
        self.request._csp_nonce = LazyNonce()  # what ContentSecurityPolicyMiddleware does

    def render(self, template, request):
        context = RequestContext(request, {'post': self.post})
        return Template('{% load hitcount_tags %}' + template).render(context)

    def test_insert_js_uses_nonce(self):
        out = self.render('{% insert_hit_count_js for post %}', self.request)
        self.assertIn('<script nonce="%s">' % self.request._csp_nonce, out)

    def test_insert_js_variables_uses_nonce(self):
        out = self.render('{% insert_hit_count_js_variables for post %}', self.request)
        self.assertIn('<script type="text/javascript" nonce="%s">' % self.request._csp_nonce, out)

    def test_no_nonce_without_csp_middleware(self):
        out = self.render('{% insert_hit_count_js for post %}', RequestFactory().get('/'))
        self.assertIn('<script>', out)
        self.assertNotIn('nonce', out)
