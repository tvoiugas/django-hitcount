from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext

from .models import BlacklistIP, BlacklistUserAgent, Hit
from .utils import get_hitcount_model


@admin.register(Hit)
class HitAdmin(admin.ModelAdmin):
    list_display = ('created', 'user', 'ip', 'user_agent', 'hitcount')
    list_display_links = None
    search_fields = ('ip', 'user_agent')
    date_hierarchy = 'created'
    actions = ['blacklist_ips',
               'blacklist_user_agents',
               'blacklist_delete_ips',
               'blacklist_delete_user_agents',
               'delete_queryset',
               ]

    def has_add_permission(self, request):
        return False

    def get_actions(self, request, action_location=None):
        # Django >= 6.1 passes `action_location`; older versions don't know it
        if action_location is None:
            actions = super().get_actions(request)
        else:
            actions = super().get_actions(request, action_location=action_location)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    @admin.action(description=_("Blacklist selected IP addresses"))
    def blacklist_ips(self, request, queryset):
        for obj in queryset:
            BlacklistIP.objects.get_or_create(ip=obj.ip)
        msg = _("Successfully blacklisted %d IPs") % queryset.count()
        self.message_user(request, msg)

    @admin.action(description=_("Blacklist selected User Agents"))
    def blacklist_user_agents(self, request, queryset):
        for obj in queryset:
            BlacklistUserAgent.objects.get_or_create(user_agent=obj.user_agent)
        msg = _("Successfully blacklisted %d User Agents") % queryset.count()
        self.message_user(request, msg)

    @admin.action(description=_("Delete selected hits and blacklist related IP addresses"))
    def blacklist_delete_ips(self, request, queryset):
        self.blacklist_ips(request, queryset)
        self.delete_queryset(request, queryset)

    @admin.action(description=_("Delete selected hits and blacklist related User Agents"))
    def blacklist_delete_user_agents(self, request, queryset):
        self.blacklist_user_agents(request, queryset)
        self.delete_queryset(request, queryset)

    @admin.action(description=_("Delete selected hits"))
    def delete_queryset(self, request, queryset):
        if not self.has_delete_permission(request):
            raise PermissionDenied

        count = queryset.count()
        for obj in queryset.iterator():
            obj.delete()  # calling it this way to get custom delete() method

        msg = ngettext("%d hit was successfully deleted.",
                       "%d hits were successfully deleted.", count) % count
        self.message_user(request, msg)


@admin.register(get_hitcount_model())
class HitCountAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'hits', 'modified')
    fields = ('hits',)

    def has_add_permission(self, request):
        return False


@admin.register(BlacklistIP)
class BlacklistIPAdmin(admin.ModelAdmin):
    pass


@admin.register(BlacklistUserAgent)
class BlacklistUserAgentAdmin(admin.ModelAdmin):
    pass
