from django.contrib import admin
from django.urls import include, path

from blog import views

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),

    path('generic-detail-view-ajax/<int:pk>/',
         views.PostDetailJSONView.as_view(),
         name="ajax"),
    path('generic-detail-view-ajax-template-tag/<int:pk>/',
         views.PostDetailTemplateTagView.as_view(),
         name="ajax-template-tag"),
    path('hitcount-detail-view/<int:pk>/',
         views.PostDetailView.as_view(),
         name="detail"),
    path('hitcount-detail-view-count-hit/<int:pk>/',
         views.PostCountHitDetailView.as_view(),
         name="detail-with-count"),

    # for our built-in ajax post view
    path('hitcount/', include('hitcount.urls', namespace='hitcount')),

    path('admin/', admin.site.urls),
]
