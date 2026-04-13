from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from config.metrics import metrics_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("api.v1.urls")),
    path("health/", include("api.v1.health_urls")),
    path("metrics", metrics_view, name="prometheus-metrics"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
