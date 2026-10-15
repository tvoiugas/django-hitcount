from collections import namedtuple

from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponseBadRequest, JsonResponse
from django.views.generic import DetailView, View

from hitcount.models import BlacklistIP, BlacklistUserAgent, Hit
from hitcount.utils import get_hitcount_model, get_ip

UpdateHitCountResponse = namedtuple(
    'UpdateHitCountResponse', 'hit_counted hit_message')


class HitCountMixin:
    """
    Mixin to evaluate a HttpRequest and a HitCount and determine whether or not
    the HitCount should be incremented and the Hit recorded.
    """

    @classmethod
    def hit_count(cls, request, hitcount):
        """
        Called with a HttpRequest and HitCount object it will return a
        namedtuple:

        UpdateHitCountResponse(hit_counted=Boolean, hit_message='Message').

        `hit_counted` will be True if the hit was counted and False if it was
        not.  `'hit_message` will indicate by what means the Hit was either
        counted or ignored.
        """
        # as of Django 1.8.4 empty sessions are not being saved
        # https://code.djangoproject.com/ticket/25489
        if request.session.session_key is None:
            request.session.save()

        user = request.user
        is_authenticated_user = user.is_authenticated
        session_key = request.session.session_key
        ip = get_ip(request)
        user_agent = request.headers.get('User-Agent', '')[:255]
        hits_per_ip_limit = getattr(settings, 'HITCOUNT_HITS_PER_IP_LIMIT', 0)
        exclude_user_group = getattr(settings, 'HITCOUNT_EXCLUDE_USER_GROUP', None)

        # first, check our request against the IP blacklist
        if BlacklistIP.objects.filter(ip__exact=ip).exists():
            return UpdateHitCountResponse(
                False, 'Not counted: user IP has been blacklisted')

        # second, check our request against the user agent blacklist
        if BlacklistUserAgent.objects.filter(user_agent__exact=user_agent).exists():
            return UpdateHitCountResponse(
                False, 'Not counted: user agent has been blacklisted')

        # third, see if we are excluding a specific user group or not
        if exclude_user_group and is_authenticated_user:
            if user.groups.filter(name__in=exclude_user_group).exists():
                return UpdateHitCountResponse(
                    False, 'Not counted: user excluded by group')

        # eliminated first three possible exclusions, now on to checking our database of
        # active hits to see if we should count another one

        # start with a fresh active query set (HITCOUNT_KEEP_HIT_ACTIVE)
        qs = Hit.objects.filter_active()

        # check limit on hits from a unique ip address (HITCOUNT_HITS_PER_IP_LIMIT)
        if hits_per_ip_limit:
            if qs.filter(ip__exact=ip).count() >= hits_per_ip_limit:
                return UpdateHitCountResponse(
                    False, 'Not counted: hits per IP address limit reached')

        # create a generic Hit object with request data
        hit = Hit(session=session_key, hitcount=hitcount, ip=ip, user_agent=user_agent)

        # first, use a user's authentication to see if they made an earlier hit
        if is_authenticated_user:
            if not qs.filter(user=user, hitcount=hitcount).exists():
                hit.user = user  # associate this hit with a user
                hit.save()

                response = UpdateHitCountResponse(
                    True, 'Hit counted: user authentication')
            else:
                response = UpdateHitCountResponse(
                    False, 'Not counted: authenticated user has active hit')

        # if not authenticated, see if we have a repeat session
        else:
            if not qs.filter(session=session_key, hitcount=hitcount).exists():
                hit.save()
                response = UpdateHitCountResponse(
                    True, 'Hit counted: session key')
            else:
                response = UpdateHitCountResponse(
                    False, 'Not counted: session key has active hit')

        return response


class HitCountJSONView(HitCountMixin, View):
    """
    JSON response view to handle HitCount POST.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        msg = "Hits counted via POST only."
        return JsonResponse({'success': False, 'error_message': msg})

    def post(self, request, *args, **kwargs):
        hitcount_pk = request.POST.get('hitcountPK')

        HitCount = get_hitcount_model()
        try:
            hitcount = HitCount.objects.get(pk=hitcount_pk)
        except (HitCount.DoesNotExist, ValueError, TypeError, ValidationError):
            return HttpResponseBadRequest("HitCount object_pk not working")

        hit_count_response = self.hit_count(request, hitcount)
        return JsonResponse(hit_count_response._asdict())


class HitCountDetailView(HitCountMixin, DetailView):
    """
    HitCountDetailView provides an inherited DetailView that will inject the
    template context with a `hitcount` variable giving you the number of
    Hits for an object without using a template tag.

    Optionally, by setting `count_hit = True` you can also do the business of
    counting the Hit for this object (in lieu of using JavaScript).  It will
    then further inject the response from the attempt to count the Hit into
    the template context.
    """
    count_hit = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object:
            hit_count = get_hitcount_model().objects.get_for_object(self.object)
            hits = hit_count.hits
            context['hitcount'] = {'pk': hit_count.pk}

            if self.count_hit:
                hit_count_response = self.hit_count(self.request, hit_count)
                if hit_count_response.hit_counted:
                    hits = hits + 1
                context['hitcount']['hit_counted'] = hit_count_response.hit_counted
                context['hitcount']['hit_message'] = hit_count_response.hit_message

            context['hitcount']['total_hits'] = hits

        return context

