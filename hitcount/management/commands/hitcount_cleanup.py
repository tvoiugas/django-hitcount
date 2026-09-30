from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from hitcount.models import Hit


class Command(BaseCommand):
    help = "Can be run as a cronjob or directly to clean out old Hits objects from the database."

    def handle(self, *args, **options):
        grace = getattr(settings, 'HITCOUNT_KEEP_HIT_IN_DATABASE', {'days': 30})
        period = timezone.now() - timedelta(**grace)
        qs = Hit.objects.filter(created__lt=period)
        number_removed = qs.count()
        qs.delete()
        self.stdout.write('Successfully removed %s Hits' % number_removed)
