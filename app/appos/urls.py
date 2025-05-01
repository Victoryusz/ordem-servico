from django.contrib import admin
from django.urls import path, include  # include permite usar urls de outros apps
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls), # Inclui as rotas do app app_order
    path("", include("app_order.urls")),  # agora as URLs do app estarão ativas
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
