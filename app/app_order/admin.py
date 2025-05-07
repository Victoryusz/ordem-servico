from django.contrib import admin
from django.db.models import Count, F
from .models import OrdemServico, Stage


class ExceededRepasseFilter(admin.SimpleListFilter):
    title = 'Limite de Repasses'
    parameter_name = 'excedeu'

    def lookups(self, request, model_admin):
        return [('yes', 'Excedidos')]

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return (
                queryset
                .annotate(stage_count=Count('stages'))
                .filter(stage_count__gte=F('repass_limite'))
            )
        return queryset


@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    """
    Configurações do painel administrativo da Ordem de Serviço.
    """
    list_display = (
        'id',
        'nome_cliente',
        'status',
        'numero_os',
        'data_solicitacao',
        'stage_count',
        'repass_limite',
    )
    list_filter = (
        ExceededRepasseFilter,
        'status',
        'data_solicitacao',
    )
    search_fields = (
        'nome_cliente',
        'numero_os',
    )
    fields = (
        'nome_cliente',
        'gmg',
        'descricao',
        'status',
        'numero_os',
        'repass_limite',
    )
    actions = ['liberar_repasses']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(stage_count=Count('stages'))

    def stage_count(self, obj):
        return obj.stage_count
    stage_count.short_description = 'Etapas'

    def liberar_repasses(self, request, queryset):
        count = queryset.update(
            repass_limite=F('repass_limite') + 5
        )
        self.message_user(request, f'{count} OS receberam +5 repasses.')
    liberar_repasses.short_description = 'Liberar +5 repasses'
