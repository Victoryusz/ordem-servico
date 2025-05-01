from django.contrib import admin
from django.urls import path, include  # include permite usar urls de outros apps

urlpatterns = [
    path("admin/", admin.site.urls),
    # Inclui as rotas do app app_order
    path("", include("app_order.urls")),  # agora as URLs do app estarão ativas
]
