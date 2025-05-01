from django.urls import path
from . import views

urlpatterns = [
    path('solicitar-os/', views.solicitar_os, name='solicitar_os'),
    path('solicitacao-enviada/', views.os_sucesso, name='os_sucesso'),

    # Login e Logout
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
