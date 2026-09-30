from django.core.exceptions import ImproperlyConfigured
from django.test import RequestFactory, SimpleTestCase

from hitcount import settings as hitcount_settings
from hitcount.models import HitCount
from hitcount.utils import get_hitcount_model, get_ip


class GetIPTests(SimpleTestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_remote_addr(self):
        request = self.factory.get('/', REMOTE_ADDR='192.168.1.10')
        self.assertEqual(get_ip(request), '192.168.1.10')

    def test_x_forwarded_for_single(self):
        request = self.factory.get('/', REMOTE_ADDR='10.1.1.1',
                                   HTTP_X_FORWARDED_FOR='203.0.113.7')
        self.assertEqual(get_ip(request), '203.0.113.7')

    def test_x_forwarded_for_list_uses_first_ip(self):
        request = self.factory.get('/', REMOTE_ADDR='10.1.1.1',
                                   HTTP_X_FORWARDED_FOR='203.0.113.7, 198.51.100.2, 10.1.1.1')
        self.assertEqual(get_ip(request), '203.0.113.7')

    def test_ipv6(self):
        request = self.factory.get('/', REMOTE_ADDR='2001:db8::1')
        self.assertEqual(get_ip(request), '2001:db8::1')

    def test_invalid_ip(self):
        request = self.factory.get('/', HTTP_X_FORWARDED_FOR='unknown')
        self.assertEqual(get_ip(request), '10.0.0.1')


class GetHitCountModelTests(SimpleTestCase):

    def test_default_model(self):
        self.assertIs(get_hitcount_model(), HitCount)

    def test_malformed_setting(self):
        original = hitcount_settings.MODEL_HITCOUNT
        hitcount_settings.MODEL_HITCOUNT = 'hitcount'
        try:
            with self.assertRaises(ImproperlyConfigured):
                get_hitcount_model()
        finally:
            hitcount_settings.MODEL_HITCOUNT = original

    def test_missing_model(self):
        original = hitcount_settings.MODEL_HITCOUNT
        hitcount_settings.MODEL_HITCOUNT = 'hitcount.DoesNotExist'
        try:
            with self.assertRaises(ImproperlyConfigured):
                get_hitcount_model()
        finally:
            hitcount_settings.MODEL_HITCOUNT = original
