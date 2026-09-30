from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import DetailView, TemplateView

from hitcount.views import HitCountDetailView

from blog.models import Post


class PostMixinDetailView:
    """
    Mixin to save us some typing.  Adds context for us!
    """
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_list'] = Post.objects.all()[:5]
        context['post_views'] = ["ajax", "ajax-template-tag", "detail", "detail-with-count"]
        return context


class IndexView(PostMixinDetailView, TemplateView):
    template_name = 'blog/index.html'


@method_decorator(ensure_csrf_cookie, name='dispatch')
class PostDetailJSONView(PostMixinDetailView, DetailView):
    """
    Counts the hit with the bundled jQuery plugin (``jquery.postcsrf.js``),
    which reads the CSRF token from the cookie.
    """
    template_name = 'blog/post_ajax.html'


class PostDetailTemplateTagView(PostMixinDetailView, DetailView):
    """
    Counts the hit with ``{% insert_hit_count_js %}``: no jQuery required.
    """
    template_name = 'blog/post_ajax_template_tag.html'


class PostDetailView(PostMixinDetailView, HitCountDetailView):
    """
    Generic hitcount class based view.
    """


class PostCountHitDetailView(PostMixinDetailView, HitCountDetailView):
    """
    Generic hitcount class based view that will also perform the hitcount logic.
    """
    count_hit = True
