from functools import wraps
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse, Http404
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils import timezone
import datetime
from django.contrib.auth import get_user_model
from .models import OrdemServico, Stage
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import make_password
from django.urls import reverse

from .forms import (
    OrdemServicoForm,
    RegistroUsuarioForm,
    StageActionForm,
)


User = get_user_model()


# ——————————————————————————————————————
# Decorator de debug: loga o nome da view ao ser chamada
# ——————————————————————————————————————
def debug_view(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        print(f"[DEBUG] View chamada: {func.__name__}")
        return func(request, *args, **kwargs)

    return wrapper


# ##########################################################
#           SOLICITAÇÃO DE ORDEM DE SERVIÇO
# ##########################################################

# Limite máximo de tarefas simultâneas em execução para cada usuário
MAX_ETAPAS_EM_ANDAMENTO = 2

@login_required(login_url="login")
@debug_view
def solicitar_os(request):
    """
    Exibe e processa o formulário de nova OS.
    - Bloqueia se houver 1 OS pendente de aprovação
      ou 2 etapas ativas (tarefas) em execução.
    """
    # 1) OS pendentes de aprovação criadas por este usuário
    os_pendentes = OrdemServico.objects.filter(
        usuario=request.user,
        status="aguardando"
    ).count()

    # 2) Etapas ativas (tarefas) atribuídas a este usuário
    etapas_ativas = (
        Stage.objects
        .filter(
            tecnico=request.user,
            status="em_execucao",
            order__status="em_andamento"
        )
        .values("order")
        .distinct()
        .count()
    )

    form = OrdemServicoForm(request.POST or None)
    if request.method == "POST":
        # Se tiver pendente ou já 2+ tarefas, renderiza sem processar
        if os_pendentes or etapas_ativas >= MAX_ETAPAS_EM_ANDAMENTO:
            return render(request, "app_order/solicitar_os.html", {
                "form": form,
                "os_pendentes": os_pendentes,
                "etapas_ativas": etapas_ativas,
            })

        # Caso contrário, salva nova OS e cria etapa inicial
        if form.is_valid():
            ordem = form.save(commit=False)
            ordem.usuario = request.user
            ordem.save()
            Stage.objects.create(order=ordem, tecnico=request.user, ordem=1)
            return redirect("os_sucesso")

    # GET ou casos de bloqueio: exibe formulário com flags
    return render(request, "app_order/solicitar_os.html", {
        "form": form,
        "os_pendentes": os_pendentes,
        "etapas_ativas": etapas_ativas,
    })


@login_required(login_url="login")
@debug_view
def os_sucesso(request):
    """Confirmação de envio de OS."""
    ultima_ordem = OrdemServico.objects.last()
    return render(request, "app_order/os_sucesso.html", {"ordem_servico": ultima_ordem})


# ##########################################################
#                AUTENTICAÇÃO DE USUÁRIO
# ##########################################################


def login_view(request):
    """Faz login e redireciona de acordo com perfil ou next_url seguro."""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        next_url = request.POST.get("next", "")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            host = request.get_host()
            # redireciona se next_url for interna e segura
            if next_url and url_has_allowed_host_and_scheme(next_url, {host}):
                return redirect(next_url)
            # caso contrário, vai para o painel padrão
            if is_admin(user):
                return redirect("painel_admin")
            if is_funcionario(user):
                return redirect("listar_os_funcionario")
            return redirect("solicitar_os")
        messages.error(request, "Usuário ou senha inválidos.")
    else:
        next_url = request.GET.get("next", "")
    return render(request, "app_order/login.html", {"next": next_url})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username") # nome de usuário
        password = request.POST.get("password") # senha em texto plano
        remember = request.POST.get("remember") # "on" ou "off"

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # expiração de sessão
            if remember == "on":
                request.session.set_expiry(1209600)
            else:
                request.session.set_expiry(0)

            # redirecionamento condicional
            if user.is_superuser or user.is_staff:
                # leva para o admin Django ou um dashboard de admin customizado
                return redirect(reverse('painel_admin'))
            else:
                # usuário normal: next ou dashboard
                next_url = request.POST.get("next")
                return redirect(next_url or reverse('painel_funcionario'))

        else:
            messages.error(request, "Usuário ou senha inválidos.")

    return render(request, "app_order/login.html", {"next": request.GET.get("next", "")})

def register_view(request):
    """Form de registro de novo usuário."""
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("solicitar_os")
    else:
        form = RegistroUsuarioForm()
    return render(request, "app_order/register.html", {"form": form})


def logout_view(request):
    """Limpa mensagens e faz logout."""
    list(messages.get_messages(request))
    logout(request)
    return redirect("login")


def is_funcionario(user):
    """True se o usuário pertence ao grupo 'Funcionario'."""
    return user.groups.filter(name="Funcionario").exists()


def is_admin(user):
    """True se superuser ou pertence ao grupo 'Administrador'."""
    return user.is_superuser or user.groups.filter(name="Administrador").exists()


# ##########################################################
#                      PAINÉIS
# ##########################################################


@login_required(login_url="login")
@user_passes_test(is_funcionario, login_url="login")
@debug_view
def painel_funcionario(request):
    """Tela inicial do técnico."""
    return render(request, "app_order/painel_funcionario.html")


@login_required(login_url="login")
@user_passes_test(is_admin, login_url="login")
@debug_view
def painel_admin(request):
    ordens = OrdemServico.objects.annotate(stage_count=Count("stages")).order_by(
        "-data_solicitacao"
    )
    total_andamento = ordens.filter(status="em_andamento").count()
    novas_os = ordens.filter(status="aguardando").count()
    novas_24h = OrdemServico.objects.filter(
        data_solicitacao__gte=timezone.now() - datetime.timedelta(hours=24)
    ).count()
    concluidas = ordens.filter(status="concluida").count()  # <-- aqui
    return render(
        request,
        "app_order/painel_admin.html",
        {
            "ordens": ordens,
            "total_andamento": total_andamento,
            "novas_os": novas_os,
            "novas_24h": novas_24h,
            "concluidas": concluidas,  # <-- e adiciona no contexto
        },
    )


@login_required(login_url="login")
@user_passes_test(is_admin, login_url="login")
@debug_view
def user_list(request):
    """
    Lista todos os usuários do sistema para o admin.
    """
    users = User.objects.all().order_by("username")
    return render(
        request,
        "app_order/admin_user_list.html",
        {
            "users": users,
        },
    )


@login_required(login_url="login")
@user_passes_test(is_admin, login_url="login")
@require_POST
def toggle_user_active(request, user_id):
    """
    Ativa/desativa um usuário via POST.
    """
    user = get_object_or_404(User, pk=user_id)
    # não permitir desativar a si mesmo
    if user == request.user:
        return JsonResponse(
            {"error": "Não é possível alterar seu próprio status."}, status=400
        )
    user.is_active = not user.is_active
    user.save()
    return JsonResponse({"success": True, "is_active": user.is_active})


@login_required(login_url="login")
@user_passes_test(is_admin, login_url="login")
@require_GET
def notificacoes_os(request):
    """API: retorna JSON com total de OS aguardando aprovação."""
    count = OrdemServico.objects.filter(status="aguardando").count()
    return JsonResponse({"count": count})


@login_required(login_url="login")
@user_passes_test(is_admin, login_url="login")
@require_POST
def atribuir_numero_os(request, os_id):
    """
    API: atribui/atualiza numero_os via AJAX.
    Se estava 'aguardando', passa para 'em_andamento'.
    """
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
    """API: adiciona +5 ao repass_limite da OS selecionada."""
    ordem = get_object_or_404(OrdemServico, pk=os_id)
    ordem.repass_limite += 5
    ordem.save()
    return JsonResponse({"success": True, "repass_limite": ordem.repass_limite})


@login_required
@user_passes_test(is_admin)
def user_edit(request, user_id):
    """Retorna JSON com dados do usuário para preencher o modal."""
    user = get_object_or_404(User, pk=user_id)
    groups = list(Group.objects.values("id", "name"))
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "groups": list(user.groups.values_list("id", flat=True)),
    }
    return JsonResponse({"user": user_data, "all_groups": groups})


@login_required
@user_passes_test(is_admin)
@require_POST
def user_update(request, user_id):
    """Recebe POST e atualiza username, email, is_active e grupos."""
    user = get_object_or_404(User, pk=user_id)
    data = request.POST
    user.username = data.get("username", user.username)
    user.email = data.get("email", user.email)
    user.is_active = data.get("is_active") == "on"
    # atualizar grupos
    group_ids = data.getlist("groups")
    user.groups.set(Group.objects.filter(id__in=group_ids))
    user.save()
    return JsonResponse({"success": True})


@login_required
@user_passes_test(is_admin)
@require_POST
def user_delete(request, user_id):
    """Exclui o usuário (hard delete)."""
    user = get_object_or_404(User, pk=user_id)
    if user == request.user:
        return JsonResponse({"error": "Não é possível excluir você mesmo."}, status=400)
    user.delete()
    return JsonResponse({"success": True})


@login_required
@user_passes_test(is_admin)
@require_POST
def user_reset_password(request, user_id):
    """
    Gera senha aleatória, aplica ao usuário e retorna para admin mostrar ou enviar por e-mail.
    """
    import secrets

    user = get_object_or_404(User, pk=user_id)
    new_pw = secrets.token_urlsafe(8)  # 8 caracteres
    user.password = make_password(new_pw)
    user.save()
    # aqui você poderia disparar e-mail se quiser
    return JsonResponse({"success": True, "new_password": new_pw})


# ##########################################################
#                   ETAPAS DE SERVIÇO
# ##########################################################


@login_required(login_url="login")
@user_passes_test(is_funcionario, login_url="login")
@debug_view
def listar_os_funcionario(request):
    """
    Lista:
      - etapas em execução do técnico (status='em_andamento')
      - histórico de OS criadas e que contribuiu
    """
    etapas = Stage.objects.filter(
        tecnico=request.user, status="em_execucao", order__status="em_andamento"
    )
    criadas = OrdemServico.objects.filter(usuario=request.user).order_by(
        "-data_solicitacao"
    )
    contribui = (
        OrdemServico.objects.filter(stages__tecnico=request.user)
        .exclude(usuario=request.user)
        .distinct()
        .order_by("-data_solicitacao")
    )
    return render(
        request,
        "app_order/listar_os_funcionario.html",
        {
            "etapas": etapas,
            "criadas": criadas,
            "contribui": contribui,
        },
    )


@login_required(login_url="login")
@user_passes_test(is_funcionario, login_url="login")
@debug_view
def acao_stage(request, stage_id):
    """
    Concluir/Repasse/Finaliza uma etapa:
      - conclui somente se repasse for permitido
      - respeita order.repass_limite
    """
    stage = get_object_or_404(
        Stage, pk=stage_id, tecnico=request.user, status="em_execucao"
    )
    form = StageActionForm(
        request.POST or None, request.FILES or None, user=request.user
    )
    if form.is_valid():
        ordem = stage.order
        total = Stage.objects.filter(order=ordem).count()
        # repassar para outro técnico
        novo_tecnico = form.cleaned_data["repassar_para"]
        if novo_tecnico:
            if total < ordem.repass_limite:
                # conclui etapa atual
                stage.status = "concluida"
                stage.comentario = form.cleaned_data["comentario"]
                if form.cleaned_data["foto"]:
                    stage.foto = form.cleaned_data["foto"]
                stage.save()
                # cria próxima etapa
                Stage.objects.create(order=ordem, tecnico=novo_tecnico, ordem=total + 1)
                messages.success(
                    request,
                    f"Ordem repassada para {novo_tecnico.username} com sucesso.",
                )
            else:
                messages.warning(
                    request,
                    "Limite de repasses atingido. Entre em contato com o administrador.",
                )
        # finalizar a OS por completo
        elif form.cleaned_data["finalizar_os"]:
            stage.status = "concluida"
            stage.comentario = form.cleaned_data["comentario"]
            if form.cleaned_data["foto"]:
                stage.foto = form.cleaned_data["foto"]
            stage.save()
            ordem.status = "concluida"
            ordem.save()
            messages.success(request, "OS finalizada com sucesso!")
        # somente concluir etapa
        else:
            stage.status = "concluida"
            stage.comentario = form.cleaned_data["comentario"]
            if form.cleaned_data["foto"]:
                stage.foto = form.cleaned_data["foto"]
            stage.save()
            messages.success(request, "Serviço concluído com sucesso.")
        return redirect("listar_os_funcionario")

    return render(request, "app_order/acao_stage.html", {"form": form, "stage": stage})


# ##########################################################
#                  ENDPOINTS & APIs
# ##########################################################


@login_required(login_url="login")
@require_GET
def verificar_numero_os(request, pk):
    """
    API: retorna numero_os e status de uma OS,
    ou nulls caso não exista ou não pertença ao user.
    """
    ordem = get_object_or_404(OrdemServico, pk=pk, usuario=request.user)
    return JsonResponse({
        "numero_os": ordem.numero_os or None,
        "status":    ordem.status,
    })


@login_required(login_url="login")
@require_GET
def api_os_funcionario(request):
    """API: lista as OS do usuário em JSON."""
    ordens = OrdemServico.objects.filter(usuario=request.user)
    dados = list(
        ordens.values("id", "numero_os", "nome_cliente", "descricao", "status")
    )
    return JsonResponse(dados, safe=False)


@login_required(login_url="login")
def detalhes_os(request, os_id):
    """
    API: retorna o partial HTML da timeline de etapas para o modal.
    Só acessível se for criador ou técnico de alguma etapa.
    """
    qs = OrdemServico.objects.filter(
        Q(usuario=request.user) | Q(stages__tecnico=request.user)
    ).distinct()
    ordem = get_object_or_404(qs, pk=os_id)
    etapas = ordem.stages.all().order_by("ordem", "criado_em")
    return render(request, "app_order/partials/timeline.html", {"etapas": etapas})

