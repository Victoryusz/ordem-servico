from functools import wraps
import json
import datetime

from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Count, F, Avg, ExpressionWrapper, DurationField
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import make_password

from .models import OrdemServico, Stage
from .forms import OrdemServicoForm, RegistroUsuarioForm, StageActionForm

User = get_user_model()


def debug_view(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        print(f"[DEBUG] View chamada: {func.__name__}")
        return func(request, *args, **kwargs)
    return wrapper


MAX_ETAPAS_EM_ANDAMENTO = 2


@login_required(login_url="login")
def solicitar_os(request):
    os_pendentes = OrdemServico.objects.filter(usuario=request.user, status="aguardando").count()
    etapas_ativas = Stage.objects.filter(
        tecnico=request.user,
        status="em_execucao",
        order__status="em_andamento"
    ).count()
    form = OrdemServicoForm(request.POST or None)
    if request.method == "POST":
        if os_pendentes or etapas_ativas >= MAX_ETAPAS_EM_ANDAMENTO:
            return render(request, "app_order/solicitar_os.html", {
                "form": form,
                "os_pendentes": os_pendentes,
                "etapas_ativas": etapas_ativas
            })
        if form.is_valid():
            nova_os = form.save(commit=False)
            nova_os.usuario = request.user
            prazo = form.cleaned_data.get("prazo_inicial")
            if prazo:
                dt = datetime.datetime.combine(prazo, datetime.time.min)
                nova_os.prazo_inicial = timezone.make_aware(dt)
            nova_os.save()
            Stage.objects.create(order=nova_os, tecnico=request.user, ordem=1)
            return redirect("os_sucesso")
    return render(request, "app_order/solicitar_os.html", {
        "form": form,
        "os_pendentes": os_pendentes,
        "etapas_ativas": etapas_ativas
    })


@login_required(login_url="login")
def os_sucesso(request):
    ultima_ordem = OrdemServico.objects.filter(usuario=request.user).last()
    return render(request, "app_order/os_sucesso.html", {
        "ordem_servico": ultima_ordem
    })


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        remember = request.POST.get("remember")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            request.session.set_expiry(1209600 if remember == "on" else 0)
            if user.is_superuser or user.is_staff:
                return redirect(reverse("painel_admin"))
            next_url = request.POST.get("next")
            return redirect(next_url or reverse("painel_funcionario"))
        messages.error(request, "Usuário ou senha inválidos.")
    return render(request, "app_order/login.html", {
        "next": request.GET.get("next", "")
    })


def register_view(request):
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("solicitar_os")
    else:
        form = RegistroUsuarioForm()
    return render(request, "app_order/register.html", {
        "form": form
    })


def termos(request):
    return render(request, "app_order/terms.html")


def privacy(request):
    return render(request, "app_order/privacy.html")


def logout_view(request):
    list(messages.get_messages(request))
    logout(request)
    return redirect("login")


def is_funcionario(user):
    return user.groups.filter(name="Funcionario").exists()


def is_admin(user):
    return user.is_superuser or user.groups.filter(name="Administrador").exists()


@login_required(login_url="login")
@user_passes_test(is_funcionario, login_url="login")
@debug_view
def painel_funcionario(request):
    return render(request, "app_order/painel_funcionario.html")


@login_required(login_url="login")
@user_passes_test(is_admin, login_url="login")
@debug_view
def painel_admin(request):
    ordens = OrdemServico.objects.annotate(stage_count=Count("stages")).order_by("-data_solicitacao")
    context = {
        "ordens": ordens,
        "total_andamento": ordens.filter(status="em_andamento").count(),
        "novas_os": ordens.filter(status="aguardando").count(),
        "novas_24h": OrdemServico.objects.filter(
            data_solicitacao__gte=timezone.now() - datetime.timedelta(hours=24)
        ).count(),
        "concluidas": ordens.filter(status="concluida").count(),
    }
    return render(request, "app_order/painel_admin.html", context)


@login_required(login_url="login")
@user_passes_test(is_admin, login_url="login")
@debug_view
def user_list(request):
    users = User.objects.all().order_by("username")
    return render(request, "app_order/admin_user_list.html", {
        "users": users
    })


@login_required(login_url="login")
@user_passes_test(is_admin, login_url="login")
@require_POST
def toggle_user_active(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if user == request.user:
        return JsonResponse({"error": "Não é possível alterar seu próprio status."}, status=400)
    user.is_active = not user.is_active
    user.save()
    return JsonResponse({"success": True, "is_active": user.is_active})


@login_required(login_url="login")
@user_passes_test(is_admin, login_url="login")
@require_GET
def notificacoes_os(request):
    return JsonResponse({
        "count": OrdemServico.objects.filter(status="aguardando").count()
    })


@login_required(login_url="login")
@user_passes_test(is_admin, login_url="login")
@require_POST
def atribuir_numero_os(request, os_id):
    ordem = get_object_or_404(OrdemServico, pk=os_id)
    num = request.POST.get("numero_os", "").strip()
    if not num:
        return JsonResponse({"error": "Número obrigatório."}, status=400)
    ordem.numero_os = num
    if ordem.status == "aguardando":
        ordem.status = "em_andamento"
    ordem.save()
    return JsonResponse({"success": True, "numero_os": ordem.numero_os})


@login_required(login_url="login")
@user_passes_test(is_admin, login_url="login")
@require_POST
def liberar_repasses_os(request, os_id):
    ordem = get_object_or_404(OrdemServico, pk=os_id)
    ordem.repass_limite = F("repass_limite") + 5
    ordem.save()
    ordem.refresh_from_db()
    return JsonResponse({"success": True, "repass_limite": ordem.repass_limite})


@login_required(login_url="login")
@user_passes_test(is_admin, login_url="login")
def user_edit(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    groups = list(Group.objects.values("id", "name"))
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "groups": list(user.groups.values_list("id", flat=True))
    }
    return JsonResponse({"user": user_data, "all_groups": groups})


@login_required(login_url="login")
@user_passes_test(is_admin, login_url="login")
@require_POST
def user_update(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    data = request.POST
    user.username = data.get("username", user.username)
    user.email = data.get("email", user.email)
    user.is_active = data.get("is_active") == "on"
    group_ids = data.getlist("groups")
    user.groups.set(Group.objects.filter(id__in=group_ids))
    user.save()
    return JsonResponse({"success": True})


@login_required(login_url="login")
@user_passes_test(is_admin, login_url="login")
@require_POST
def user_delete(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if user == request.user:
        return JsonResponse({"error": "Não é possível excluir você mesmo."}, status=400)
    user.delete()
    return JsonResponse({"success": True})


@login_required(login_url="login")
@user_passes_test(is_admin, login_url="login")
@require_POST
def user_reset_password(request, user_id):
    import secrets
    user = get_object_or_404(User, pk=user_id)
    new_pw = secrets.token_urlsafe(8)
    user.password = make_password(new_pw)
    user.save()
    return JsonResponse({"success": True, "new_password": new_pw})


@login_required(login_url="login")
@user_passes_test(is_funcionario, login_url="login")
@debug_view
def listar_os_funcionario(request):
    etapas = Stage.objects.filter(
        tecnico=request.user,
        status="em_execucao",
        order__status="em_andamento"
    )
    criadas = OrdemServico.objects.filter(usuario=request.user).order_by("-data_solicitacao")
    contribui = OrdemServico.objects \
        .filter(stages__tecnico=request.user) \
        .exclude(usuario=request.user) \
        .distinct() \
        .order_by("-data_solicitacao")
    form = StageActionForm(user=request.user)
    now = timezone.localtime()
    return render(request, "app_order/listar_os_funcionario.html", {
        "etapas": etapas,
        "criadas": criadas,
        "contribui": contribui,
        "form": form,
        "now": now
    })


@login_required(login_url="login")
@user_passes_test(is_funcionario, login_url="login")
@debug_view
def acao_stage(request, stage_id):
    stage = get_object_or_404(Stage, pk=stage_id, tecnico=request.user, status="em_execucao")
    form = StageActionForm(request.POST or None, request.FILES or None, user=request.user)
    if form.is_valid():
        pd = form.cleaned_data
        if pd.get("ajustar_prazo") and pd.get("prazo_estipulado"):
            dt = datetime.datetime.combine(pd["prazo_estipulado"], datetime.time.min)
            stage.prazo_estipulado = timezone.make_aware(dt)
            stage.save()
            messages.success(request, "Prazo da etapa atualizado com sucesso.")
            return redirect("listar_os_funcionario")
        ordem = stage.order
        total = Stage.objects.filter(order=ordem).count()
        with transaction.atomic():
            stage.status = "concluida"
            stage.comentario = pd.get("comentario")
            stage.foto = pd.get("foto") or stage.foto
            stage.save()
            if pd.get("repassar_para"):
                if total < ordem.repass_limite:
                    Stage.objects.create(
                        order=ordem,
                        tecnico=pd["repassar_para"],
                        ordem=total + 1
                    )
                    messages.success(
                        request,
                        f"Ordem repassada para {pd['repassar_para'].username} com sucesso."
                    )
                else:
                    messages.warning(request, "Limite de repasses atingido. Entre em contato com o administrador.")
            elif pd.get("finalizar_os"):
                ordem.status = "concluida"
                ordem.save()
                messages.success(request, "OS finalizada com sucesso!")
        return redirect("listar_os_funcionario")
    return render(request, "app_order/acao_stage.html", {
        "form": form,
        "stage": stage
    })


@login_required(login_url="login")
@require_GET
def verificar_numero_os(request, pk):
    ordem = get_object_or_404(OrdemServico, pk=pk, usuario=request.user)
    return JsonResponse({
        "numero_os": ordem.numero_os or None,
        "status": ordem.status
    })


@login_required(login_url="login")
@require_GET
def api_os_funcionario(request):
    ordens = OrdemServico.objects.filter(usuario=request.user)
    dados = list(ordens.values("id", "numero_os", "nome_cliente", "descricao", "status"))
    return JsonResponse(dados, safe=False)


@login_required(login_url="login")
def detalhes_os(request, os_id):
    """
    Admin vê qualquer OS; técnicos veem só as que criaram ou participam.
    """
    is_admin_user = request.user.is_superuser or request.user.groups.filter(name="Administrador").exists()
    if is_admin_user:
        ordem = get_object_or_404(OrdemServico, pk=os_id)
    else:
        qs = OrdemServico.objects.filter(
            Q(usuario=request.user) | Q(stages__tecnico=request.user)
        ).distinct()
        ordem = get_object_or_404(qs, pk=os_id)

    etapas = ordem.stages.all().order_by("ordem", "criado_em")
    now = timezone.localtime()
    return render(request, "app_order/partials/timeline.html", {
        "etapas": etapas,
        "now": now
    })


@login_required(login_url="login")
@user_passes_test(is_admin, login_url="login")
def resumo_os(request):
    # KPIs gerais
    kp = OrdemServico.objects.aggregate(
        total=Count('id'),
        aguardando=Count('id', filter=Q(status='aguardando')),
        andamento=Count('id', filter=Q(status='em_andamento')),
        concluida=Count('id', filter=Q(status='concluida')),
        avg_tempo=Avg(
            ExpressionWrapper(
                F('data_conclusao') - F('data_solicitacao'),
                output_field=DurationField()
            ),
            filter=Q(status='concluida')
        )
    )

    # Evolução diária (últimos 30 dias)
    series = (
        OrdemServico.objects
        .filter(data_solicitacao__gte=timezone.now() - datetime.timedelta(days=30))
        .annotate(dia=TruncDate('data_solicitacao'))
        .values('dia')
        .annotate(qty=Count('id'))
        .order_by('dia')
    )
    series_json = json.dumps([
        {'dia': x['dia'].strftime('%Y-%m-%d'), 'qty': x['qty']}
        for x in series
    ])

    # Top 5 técnicos por etapas
    top_tech = (
        Stage.objects
        .values(name=F('tecnico__username'))
        .annotate(etapas=Count('id'))
        .order_by('-etapas')[:5]
    )

    # OS próximas do prazo
    proximas = (
        OrdemServico.objects
        .filter(prazo_inicial__date__in=[
            timezone.localdate(),
            timezone.localdate() + datetime.timedelta(days=1)
        ])
        .order_by('prazo_inicial')[:5]
    )

    return render(request, "app_order/resumo_os.html", {
        'kp': kp,
        'series_json': series_json,
        'top_tech': top_tech,
        'proximas': proximas,
    })
