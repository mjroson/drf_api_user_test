from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from .urls_api import urlpatterns as api_urlpatterns

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include((api_urlpatterns, "api"))),
]


# Add debug toolbar
if settings.DEBUG and "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
