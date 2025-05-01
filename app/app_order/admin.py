# Importa o módulo de administração do Django
from django.contrib import admin

# Importa o modelo que criamos no models.py
from .models import OrdemServico

# Registra o modelo na interface administrativa do Django
@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    """
    Configuração da interface de administração para o modelo OrdemServico.
    Isso personaliza como os dados aparecem no painel /admin.
    """

    # Define quais colunas aparecerão na lista de OSs no admin
    list_display = (
        'id',               # ID automático da OS
        'nome_cliente',     # Nome do cliente
        'email_cliente',    # E-mail do cliente
        'status',           # Status da OS (aguardando, em andamento, concluída)
        'numero_os',        # Número manual da OS inserido pelo admin
        'data_solicitacao'  # Data em que a OS foi criada
    )

    # Adiciona filtros laterais no admin para facilitar a navegação
    list_filter = (
        'status',            # Permite filtrar por status
        'data_solicitacao',  # Permite filtrar por data
    )

    # Permite pesquisar OSs por nome, e-mail ou número da OS
    search_fields = (
        'nome_cliente',
        'email_cliente',
        'numero_os',
    )
