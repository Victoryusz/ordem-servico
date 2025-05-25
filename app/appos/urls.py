from django.urls import path
from django.conf import settings
from . import views

# Rotas principais da aplicação Juma OS
urlpatterns = [
    # Solicitação de Ordem de Serviço
    path('solicitar-os/', views.solicitar_os, name='solicitar_os'),
    path('solicitacao-enviada/', views.os_sucesso, name='os_sucesso'),

    # Autenticação de usuário
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # Painéis de controle
    path('painel-funcionario/', views.painel_funcionario, name='painel_funcionario'),
    path('painel-admin/', views.painel_admin, name='painel_admin'),

    # Funcionário: Minhas etapas e histórico
    path('painel-funcionario/ordens/', views.listar_os_funcionario, name='listar_os_funcionario'),
    path('painel-funcionario/acao-stage/<int:stage_id>/', views.acao_stage, name='acao_stage'),

    # Endpoints AJAX/API
    path('api/verificar-numero-os/<int:pk>/', views.verificar_numero_os, name='verificar_numero_os'),
    path('api/os-funcionario/', views.api_os_funcionario, name='api_os_funcionario'),
    path('detalhes-os/<int:os_id>/', views.detalhes_os, name='detalhes_os'),
    path('api/notificacoes-os/', views.notificacoes_os, name='notificacoes_os'),

    # Admin AJAX: Atribuir número e liberar repasses
    path('painel-admin/atribuir-numero/<int:os_id>/', views.atribuir_numero_os, name='atribuir_numero_os'),
    path('painel-admin/liberar-repasses/<int:os_id>/', views.liberar_repasses_os, name='liberar_repasses_os'),

    # Gerenciamento de usuários (admin)
    path('painel-admin/usuarios/', views.user_list, name='admin_user_list'),
    path('painel-admin/usuarios/<int:user_id>/toggle-active/', views.toggle_user_active, name='toggle_user_active'),
    path('painel-admin/usuarios/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('painel-admin/usuarios/<int:user_id>/update/', views.user_update, name='user_update'),
    path('painel-admin/usuarios/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('painel-admin/usuarios/<int:user_id>/reset-password/', views.user_reset_password, name='user_reset_password'),

    # Páginas legais
    path('termos/', views.termos, name='termos'),
    path('privacidade/', views.privacy, name='privacy'),
]

# Exibir rotas para depuração em ambiente de desenvolvimento
if settings.DEBUG:
    def debug_urls():
        from django.urls import get_resolver
        for pattern in get_resolver().url_patterns:
            print(f"[URL DEBUG] {pattern}")
    # debug_urls()