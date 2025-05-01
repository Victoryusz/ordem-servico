from django.contrib import admin
from .models import OrdemServico


@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    """
    Configurações do painel administrativo da Ordem de Serviço.
    """

    # Campos que aparecem na lista (tabela principal)
    list_display = (
        "id",
        "nome_cliente",
        "email_cliente",
        "status",
        "numero_os",
        "data_solicitacao",
    )

    # Campos pelos quais o admin pode filtrar lateralmente
    list_filter = ("status", "data_solicitacao")

    # Campos pesquisáveis no topo
    search_fields = ("nome_cliente", "email_cliente", "numero_os")

    # Campos que serão exibidos no formulário de edição da OS
    fields = (
        "nome_cliente",
        "email_cliente",
        "gmg",
        "descricao",
        "status",
        "numero_os",  # ✅ agora aparecerá para edição
    )
