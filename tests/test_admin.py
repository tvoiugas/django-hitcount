from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory, TestCase
from django.urls import reverse

from hitcount.admin import HitAdmin, HitCountAdmin
from hitcount.models import BlacklistIP, BlacklistUserAgent, Hit
from hitcount.utils import get_hitcount_model

from blog.models import Post

HitCount = get_hitcount_model()


class HitCountAdminTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.admin = HitCountAdmin(HitCount, AdminSite())

    def test_has_add_permission(self):
        """
        Should return False always.
        """
        self.assertFalse(self.admin.has_add_permission(self.factory))


class HitAdminTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.admin = HitAdmin(Hit, AdminSite())
        self.request = self.factory.get(reverse('admin:hitcount_hit_changelist'))

        # https://code.djangoproject.com/ticket/17971
        self.request.session = 'session'
        messages = FallbackStorage(self.request)
        self.request._messages = messages
        self.request.user = AnonymousUser()

        post = Post.objects.create(title='my title', content='my text')
        hit_count = HitCount.objects.create(content_object=post)

        for x in range(10):
            Hit.objects.create(hitcount=hit_count, ip="127.0.0.%s" % x, user_agent="agent_%s" % x)

    def test_has_add_permission(self):
        """
        Should return False always.
        """
        self.assertFalse(self.admin.has_add_permission(self.factory))

    def test_get_actions(self):
        """
        Actions should be: ['blacklist_ips',
               'blacklist_user_agents',
               'blacklist_delete_ips',
               'blacklist_delete_user_agents',
               'delete_queryset',
               ]
        """
        actions = ['blacklist_ips',
                   'blacklist_user_agents',
                   'blacklist_delete_ips',
                   'blacklist_delete_user_agents',
                   'delete_queryset',
                   ]
        self.assertEqual(actions, list(self.admin.get_actions(self.request).keys()))

    def test_blacklist_ips_single(self):
        """
        Test adding `blacklist_ips` via Admin action.
        """
        # add by hit object, should
        qs = Hit.objects.filter(ip="127.0.0.5")
        self.admin.blacklist_ips(self.request, qs)
        ip = BlacklistIP.objects.get(pk=1)
        self.assertEqual(ip.ip, "127.0.0.5")
        self.assertEqual(len(BlacklistIP.objects.all()), 1)

    def test_blacklist_ips_multiple(self):
        """
        Test adding `blacklist_ips` via Admin action with multiple items.
        """
        qs = Hit.objects.all()[:5]
        self.admin.blacklist_ips(self.request, qs)
        ips = BlacklistIP.objects.values_list('ip', flat=True)
        self.assertEqual(ips[4], '127.0.0.5')
        self.assertEqual(len(BlacklistIP.objects.all()), 5)

    def test_blacklist_ips_add_only_once(self):
        """
        Test adding `blacklist_ips` to ensure adding the same IP address more
        than once does not duplicate a record in the BlacklistIP table.
        """
        qs = Hit.objects.filter(ip="127.0.0.5")
        self.admin.blacklist_ips(self.request, qs)
        self.assertEqual(len(BlacklistIP.objects.all()), 1)

        # adding a second time should not increase the list
        qs = Hit.objects.filter(ip="127.0.0.5")
        self.admin.blacklist_ips(self.request, qs)
        self.assertEqual(len(BlacklistIP.objects.all()), 1)

    def test_blacklist_user_agents_single(self):
        """
        Test adding `blacklist_user_agent` via Admin action.
        """
        qs = Hit.objects.filter(ip="127.0.0.5")
        self.admin.blacklist_user_agents(self.request, qs)
        ua = BlacklistUserAgent.objects.get(pk=1)
        self.assertEqual(ua.user_agent, 'agent_5')
        self.assertEqual(len(BlacklistUserAgent.objects.all()), 1)

    def test_blacklist_user_agents_multiple(self):
        """
        Test adding `blacklist_ips` via Admin action with multiple items.
        """
        qs = Hit.objects.all()[:5]
        self.admin.blacklist_user_agents(self.request, qs)
        uas = BlacklistUserAgent.objects.values_list('user_agent', flat=True)
        self.assertEqual(uas[2], 'agent_7')
        self.assertEqual(len(BlacklistUserAgent.objects.all()), 5)

    def test_blacklist_user_agents_add_only_once(self):
        """
        Test adding `blacklist_ips` to ensure adding the same user agent more
        than once does not duplicate a record in the BlacklistUserAgent table.
        """
        qs = Hit.objects.filter(ip="127.0.0.5")
        self.admin.blacklist_user_agents(self.request, qs)
        self.assertEqual(len(BlacklistUserAgent.objects.all()), 1)

        # adding a second time should not increase the list
        qs = Hit.objects.filter(ip="127.0.0.5")
        self.admin.blacklist_user_agents(self.request, qs)
        self.assertEqual(len(BlacklistUserAgent.objects.all()), 1)

    def test_delete_queryset(self):
        """
        Test the `delete_queryset` action.
        """
        my_admin = User.objects.create_superuser('myuser', 'myemail@example.com', '1234')
        self.request.user = my_admin

        qs = Hit.objects.all()[:5]
        self.admin.delete_queryset(self.request, qs)
        hit_count = HitCount.objects.get(pk=1)

        self.assertEqual(len(Hit.objects.all()), 5)
        self.assertEqual(hit_count.hits, 5)

    def test_delete_queryset_single_item(self):
        """
        Test the `delete_queryset` action against a single item.
        """
        my_admin = User.objects.create_superuser('myuser', 'myemail@example.com', '1234')
        self.request.user = my_admin

        qs = Hit.objects.filter(ip="127.0.0.5")
        self.admin.delete_queryset(self.request, qs)
        hit_count = HitCount.objects.get(pk=1)

        self.assertEqual(len(Hit.objects.all()), 9)
        self.assertEqual(hit_count.hits, 9)

    def test_delete_queryset_permission_denied(self):
        """
        Test the `delete_queryset` action against an unauthorized user.
        """
        my_admin = User.objects.create_user('myuser', 'myemail@example.com', '1234')
        self.request.user = my_admin

        qs = Hit.objects.all()[:5]
        with self.assertRaises(PermissionDenied):
            self.admin.delete_queryset(self.request, qs)

    def test_blacklist_and_delete_ips(self):
        """
        Test the `blacklist_delete_ips` action.
        """
        my_admin = User.objects.create_superuser('myuser', 'myemail@example.com', '1234')
        self.request.user = my_admin

        qs = Hit.objects.all()[:5]
        self.admin.blacklist_delete_ips(self.request, qs)
        hit_count = HitCount.objects.get(pk=1)

        self.assertEqual(len(Hit.objects.all()), 5)
        self.assertEqual(hit_count.hits, 5)
        self.assertEqual(len(BlacklistIP.objects.all()), 5)

    def test_blacklist_and_delete_user_agents(self):
        """
        Test the `blacklist_delete_user_agents` action.
        """
        my_admin = User.objects.create_superuser('myuser', 'myemail@example.com', '1234')
        self.request.user = my_admin

        qs = Hit.objects.all()[:5]
        self.admin.blacklist_delete_user_agents(self.request, qs)
        hit_count = HitCount.objects.get(pk=1)

        self.assertEqual(len(Hit.objects.all()), 5)
        self.assertEqual(hit_count.hits, 5)
        self.assertEqual(len(BlacklistUserAgent.objects.all()), 5)


class AdminPagesTest(TestCase):
    """Render the real admin pages, so Django calls our overrides itself."""

    def setUp(self):
        user = User.objects.create_superuser('admin', 'admin@example.com', 'pw-for-tests-only')
        self.client.force_login(user)
        post = Post.objects.create(title='my title', content='my text')
        hit_count = HitCount.objects.create(content_object=post)
        Hit.objects.create(hitcount=hit_count, ip='127.0.0.1', user_agent='agent')

    def test_changelists_render(self):
        for name in ('hit', 'hitcount', 'blacklistip', 'blacklistuseragent'):
            with self.subTest(name=name):
                response = self.client.get(reverse('admin:hitcount_%s_changelist' % name))
                self.assertEqual(response.status_code, 200)

    def test_hit_changelist_actions(self):
        response = self.client.get(reverse('admin:hitcount_hit_changelist'))
        actions = [value for value, _label in response.context['action_form'].fields['action'].choices]
        self.assertNotIn('delete_selected', actions)
        self.assertIn('blacklist_ips', actions)
