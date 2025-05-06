from django.urls import path
from . import views
from .views import api_os_funcionario
print("[DEBUG] URLs carregadas com sucesso.")

urlpatterns = [
    path("solicitar-os/", views.solicitar_os, name="solicitar_os"),
    path("solicitacao-enviada/", views.os_sucesso, name="os_sucesso"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    path("painel-funcionario/", views.painel_funcionario, name="painel_funcionario"),
    path("painel-admin/", views.painel_admin, name="painel_admin"),
    path("painel-funcionario/ordens/",views.listar_os_funcionario, name="listar_os_funcionario"),
    path('painel-funcionario/concluir/<str:numero_os>/', views.concluir_os, name='concluir_os'),
    path('api/verificar-numero-os/<int:pk>/', views.verificar_numero_os, name='verificar_numero_os'),
    path('api/os-funcionario/', api_os_funcionario, name='api_os_funcionario'),
]

# ✅ Código de debug seguro
def debug_urls():
    from django.urls import get_resolver
    for pattern in get_resolver().url_patterns:
        print(f"[URL DEBUG] {pattern}")

# ❌ NÃO chame a função aqui!
# debug_urls()  <- ISSO causará erro se ativado aqui
