"""
End-to-end browser tests.

These are opt-in because they need a real browser::

    HITCOUNT_SELENIUM=1 pytest -m selenium

Use ``HITCOUNT_SELENIUM_BROWSER`` to pick ``chrome`` (default), ``firefox`` or
``edge``. Selenium Manager downloads a matching driver automatically.
"""
import os

import pytest
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse

from blog.models import Post

pytestmark = [
    pytest.mark.selenium,
    pytest.mark.skipif(not os.environ.get('HITCOUNT_SELENIUM'),
                       reason='set HITCOUNT_SELENIUM=1 to run browser tests'),
]


def make_driver():
    webdriver = pytest.importorskip('selenium.webdriver')
    browser = os.environ.get('HITCOUNT_SELENIUM_BROWSER', 'chrome').lower()

    if browser == 'firefox':
        options = webdriver.FirefoxOptions()
        options.add_argument('-headless')
        return webdriver.Firefox(options=options)
    if browser == 'edge':
        options = webdriver.EdgeOptions()
        options.add_argument('--headless=new')
        return webdriver.Edge(options=options)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    return webdriver.Chrome(options=options)


class UpdateHitCountSelenium(StaticLiveServerTestCase):
    delay = 10

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = make_driver()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        self.post = Post.objects.create(title='selenium', content='post')

    def assert_hit_counted(self, url_name):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait

        self.selenium.delete_all_cookies()
        url = reverse(url_name, args=[self.post.pk])
        self.selenium.get('%s%s' % (self.live_server_url, url))
        wait = WebDriverWait(self.selenium, self.delay)
        self.assertTrue(wait.until(EC.text_to_be_present_in_element(
            (By.ID, 'hit-counted-value'), 'true')))
        self.assertEqual(self.post.hit_count.hits, 1)

    def test_ajax_hit(self):
        self.assert_hit_counted('ajax')

    def test_insert_hit_count_js(self):
        self.assert_hit_counted('ajax-template-tag')
