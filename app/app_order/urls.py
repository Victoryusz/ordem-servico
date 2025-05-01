from django.urls import path
from . import views

urlpatterns = [
    # Rota para exibir e enviar o formulário de solicitação
    path('solicitar-os/', views.solicitar_os, name='solicitar_os'),

    # Rota para exibir mensagem de sucesso após o envio
    path('solicitacao-enviada/', views.os_sucesso, name='os_sucesso'),
]
