from django.contrib import admin
from django.db.models import Count, F, Q
from django.utils import timezone
from .models import OrdemServico, Stage

# Filtro para OS com prazo inicial vencido
class OverdueFilter(admin.SimpleListFilter):
    title = 'Prazo Inicial'
    parameter_name = 'overdue'

    def lookups(self, request, model_admin):
        return [
            ('overdue', 'Vencidos'),
            ('ok', 'Dentro do prazo'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'overdue':
            return queryset.filter(prazo_inicial__lt=timezone.now(), status__in=['aguardando', 'em_andamento'])
        if self.value() == 'ok':
            return queryset.filter(Q(prazo_inicial__gte=timezone.now()) | Q(prazo_inicial__isnull=True))
        return queryset

# Filtro para OS que excederam repasses
class ExceededRepasseFilter(admin.SimpleListFilter):
    title = 'Limite de Repasses'
    parameter_name = 'excedeu'

    def lookups(self, request, model_admin):
        return [
            ('yes', 'Excedidos'),
            ('no', 'Restantes'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.annotate(count=Count('stages')).filter(count__gte=F('repass_limite'))
        if self.value() == 'no':
            return queryset.annotate(count=Count('stages')).filter(count__lt=F('repass_limite'))
        return queryset

# Inline para etapas dentro de cada OS
class StageInline(admin.TabularInline):
    model = Stage
    fields = ('ordem', 'tecnico', 'status', 'prazo_estipulado', 'criado_em')
    readonly_fields = ('criado_em',)
    extra = 0
    can_delete = False
    show_change_link = True

@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'nome_cliente', 'gmg', 'status', 'numero_os',
        'data_solicitacao', 'prazo_inicial', 'stage_count', 'repass_limite'
    )
    list_display_links = ('id', 'nome_cliente')
    list_editable = ('repass_limite',)
    list_filter = (
        'status', 'data_solicitacao', OverdueFilter, ExceededRepasseFilter
    )
    search_fields = ('nome_cliente', 'numero_os', 'gmg')
    date_hierarchy = 'data_solicitacao'
    ordering = ('-data_solicitacao',)
    list_per_page = 25
    fields = (
        'nome_cliente', 'gmg', 'descricao', 'status',
        'numero_os', 'prazo_inicial', 'repass_limite'
    )
    inlines = [StageInline]
    actions = ['liberar_repasses', 'marcar_concluida']

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(stage_count=Count('stages'))

    def stage_count(self, obj):
        return obj.stage_count
    stage_count.short_description = 'Etapas'

    # Ação para liberar +5 repasses
    def liberar_repasses(self, request, queryset):
        updated = queryset.update(repass_limite=F('repass_limite') + 5)
        self.message_user(request, f'{updated} OS receberam +5 repasses.')
    liberar_repasses.short_description = 'Liberar +5 repasses'

    # Ação para marcar a OS como concluída
    def marcar_concluida(self, request, queryset):
        updated = queryset.filter(~Q(status='concluida')).update(status='concluida')
        self.message_user(request, f'{updated} OS marcadas como concluídas.')
    marcar_concluida.short_description = 'Marcar como Concluída'

@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'order', 'ordem', 'tecnico', 'status', 'prazo_estipulado', 'criado_em'
    )
    list_filter = ('status', 'tecnico', 'ordem')
    search_fields = ('order__numero_os', 'tecnico__username')
    date_hierarchy = 'prazo_estipulado'
    list_editable = ('status',)
    readonly_fields = ('criado_em',)
    ordering = ('order', 'ordem')
