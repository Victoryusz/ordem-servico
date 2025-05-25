from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # Autenticação de usuários
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # Fluxo de Solicitação de Ordem de Serviço
    path('solicitar-os/', views.solicitar_os, name='solicitar_os'),
    path('solicitacao-enviada/', views.os_sucesso, name='os_sucesso'),

    # Painel do Funcionário e suas ações
    path('painel-funcionario/', views.painel_funcionario, name='painel_funcionario'),
    path('painel-funcionario/ordens/', views.listar_os_funcionario, name='listar_os_funcionario'),
    path('painel-funcionario/acao-stage/<int:stage_id>/', views.acao_stage, name='acao_stage'),

    # Painel do Administrador e ações AJAX
    path('painel-admin/', views.painel_admin, name='painel_admin'),
    path('painel-admin/atribuir-numero/<int:os_id>/', views.atribuir_numero_os, name='atribuir_numero_os'),
    path('painel-admin/liberar-repasses/<int:os_id>/', views.liberar_repasses_os, name='liberar_repasses_os'),

    # Gerenciamento de usuários (Admin)
    path('painel-admin/usuarios/', views.user_list, name='admin_user_list'),
    path('painel-admin/usuarios/<int:user_id>/toggle-active/', views.toggle_user_active, name='toggle_user_active'),
    path('painel-admin/usuarios/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('painel-admin/usuarios/<int:user_id>/update/', views.user_update, name='user_update'),
    path('painel-admin/usuarios/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('painel-admin/usuarios/<int:user_id>/reset-password/', views.user_reset_password, name='user_reset_password'),

    # Endpoints de API e AJAX para funcionalidades adicionais
    path('api/os-funcionario/', views.api_os_funcionario, name='api_os_funcionario'),
    path('api/verificar-numero-os/<int:pk>/', views.verificar_numero_os, name='verificar_numero_os'),
    path('api/notificacoes-os/', views.notificacoes_os, name='notificacoes_os'),
    path('detalhes-os/<int:os_id>/', views.detalhes_os, name='detalhes_os'),

    # Páginas Legais
    path('termos/', views.termos, name='termos'),
    path('privacidade/', views.privacy, name='privacy'),
]

# Servir mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)