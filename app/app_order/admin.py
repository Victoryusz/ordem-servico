from django.contrib import admin
from django.db.models import Count, F
from .models import OrdemServico, Stage


class ExceededRepasseFilter(admin.SimpleListFilter):
    title = "Limite de Repasses"
    parameter_name = "excedeu"

    def lookups(self, request, model_admin):
        return [("yes", "Excedidos")]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.annotate(stage_count=Count("stages")).filter(
                stage_count__gte=F("repass_limite")
            )
        return queryset


# Inline para mostrar as etapas diretamente na OS
class StageInline(admin.TabularInline):
    model = Stage
    fields = ("ordem", "tecnico", "status", "prazo_estipulado", "criado_em")
    readonly_fields = ("criado_em",)
    extra = 0
    can_delete = False
    show_change_link = True


@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nome_cliente",
        "status",
        "numero_os",
        "data_solicitacao",
        "prazo_inicial",
        "stage_count",
        "repass_limite",
    )
    list_filter = (
        ExceededRepasseFilter,
        "status",
        "data_solicitacao",
    )
    search_fields = ("nome_cliente", "numero_os",)
    fields = (
        "nome_cliente",
        "gmg",
        "descricao",
        "status",
        "numero_os",
        "prazo_inicial",
        "repass_limite",
    )
    inlines = [StageInline]
    actions = ["liberar_repasses"]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(stage_count=Count("stages"))

    def stage_count(self, obj):
        return obj.stage_count
    stage_count.short_description = "Etapas"

    def liberar_repasses(self, request, queryset):
        count = queryset.update(repass_limite=F("repass_limite") + 5)
        self.message_user(request, f"{count} OS receberam +5 repasses.")
    liberar_repasses.short_description = "Liberar +5 repasses"


# Registrar também um admin para Stage, se quiser
@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "ordem",
        "tecnico",
        "status",
        "prazo_estipulado",
        "criado_em",
    )
    list_filter = ("status", "order__status", "tecnico",)
    search_fields = ("order__numero_os", "tecnico__username",)
    readonly_fields = ("criado_em",)