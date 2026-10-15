"""
Full request/response cycle through the example project, with CSRF checks on.
"""
import re

from django.test import Client, TestCase
from django.urls import reverse

from blog.models import Post


class InsertHitCountJSIntegrationTests(TestCase):

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.post = Post.objects.create(title='integration', content='post')

    def post_hit(self, url, pk, token=None):
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        if token:
            headers['X-CSRFToken'] = token
        return self.client.post(url, {'hitcountPK': pk}, headers=headers)

    def test_rendered_script_can_count_a_hit(self):
        page = self.client.get(reverse('ajax-template-tag', args=[self.post.pk]))
        self.assertEqual(page.status_code, 200)
        html = page.content.decode()

        token = re.search(r'var csrfToken = "([^"]+)";', html).group(1)
        url = re.search(r'fetch\("([^"]+)"', html).group(1)
        pk = re.search(r'encodeURIComponent\("(\d+)"\)', html).group(1)

        response = self.post_hit(url, pk, token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'hit_counted': True,
                                           'hit_message': 'Hit counted: session key'})
        self.assertEqual(self.post.hit_count.hits, 1)

        # the same session is not counted twice
        response = self.post_hit(url, pk, token)
        self.assertFalse(response.json()['hit_counted'])
        self.assertEqual(self.post.hit_count.hits, 1)

    def test_post_without_csrf_token_is_rejected(self):
        self.client.get(reverse('ajax-template-tag', args=[self.post.pk]))
        response = self.post_hit(reverse('hitcount:hit_ajax'), self.post.hit_count.pk)
        self.assertEqual(response.status_code, 403)

    def test_example_pages_render(self):
        self.assertEqual(self.client.get(reverse('index')).status_code, 200)
        for name in ('ajax', 'ajax-template-tag', 'detail', 'detail-with-count'):
            with self.subTest(name=name):
                response = self.client.get(reverse(name, args=[self.post.pk]))
                self.assertEqual(response.status_code, 200)
