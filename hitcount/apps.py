from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class HitCountConfig(AppConfig):
    name = 'hitcount'
    verbose_name = _('Hit Count')
    default_auto_field = 'django.db.models.BigAutoField'
