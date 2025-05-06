from functools import wraps
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.http import require_POST, require_GET
from .forms import OrdemServicoForm, RegistroUsuarioForm, ConcluirOSForm
from .models import OrdemServico
from django.http import JsonResponse

#############################################################
# ORDEM DE SERVIÇO
#############################################################

# Debug decorator: preserves metadata and logs view calls
def debug_view(func):
    @wraps(func)  # preserva nome e docstring da função original
    def wrapper(request, *args, **kwargs):
        print(f"[DEBUG] View chamada: {func.__name__}")
        return func(request, *args, **kwargs)
    return wrapper

@login_required(login_url="login")
@debug_view  # debug-mode
def solicitar_os(request):
    """
    Exibe e processa o formulário de solicitação de OS.
    """
    if request.method == "POST":
        form = OrdemServicoForm(request.POST)
        if form.is_valid():
            # evita shadowing do módulo os
            ordem = form.save(commit=False)
            ordem.usuario = request.user
            ordem.save()
            return redirect("os_sucesso")
    else:
        form = OrdemServicoForm()

    return render(request, "app_order/solicitar_os.html", {"form": form})

@login_required(login_url="login")
@debug_view  # debug-mode
def os_sucesso(request):
    """
    Exibe confirmação de envio e número da OS (ou aguardando aprovação).
    """
    ultima_ordem = OrdemServico.objects.last()
    return render(request, "app_order/os_sucesso.html", {"ordem_servico": ultima_ordem})

#############################################################
# AUTENTICAÇÃO DE USUÁRIO
#############################################################

def login_view(request):
    """
    Exibe tela de login e redireciona conforme perfil do usuário.
    """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        next_url = request.POST.get("next")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if next_url:
                return redirect(next_url)
            if is_admin(user):
                return redirect("painel_admin")
            if is_funcionario(user):
                return redirect("painel_funcionario")
            return redirect("solicitar_os")
        messages.error(request, "Usuário ou senha inválidos.")
    else:
        next_url = request.GET.get("next", "")

    return render(request, "app_order/login.html", {"next": next_url})

def register_view(request):
    """
    Exibe formulário de registro e cria novo usuário.
    """
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()  # já chama set_password
            login(request, user)
            return redirect("solicitar_os")
    else:
        form = RegistroUsuarioForm()
    return render(request, "app_order/register.html", {"form": form})

def is_funcionario(user):
    """Retorna True se o usuário pertence ao grupo Funcionario."""
    return user.groups.filter(name="Funcionario").exists()

def is_admin(user):
    """Retorna True se o usuário for superusuário ou pertence ao grupo Administrador."""
    if user.is_superuser:
        print(f"[DEBUG] {user.username} é superusuário.")
        return True
    grupos = [g.name for g in user.groups.all()]
    print(f"[DEBUG] {user.username} - Grupos: {grupos}")
    return "Administrador" in grupos

def logout_view(request):
    """
    Faz logout e redireciona para a tela de login.
    """
    logout(request)
    return redirect("login")

@user_passes_test(is_funcionario, login_url="login")
@debug_view  # debug-mode
def painel_funcionario(request):
    return render(request, "app_order/painel_funcionario.html")

@login_required(login_url="login")
@debug_view  # debug-mode
def painel_admin(request):
    """
    Exibe painel do admin; redireciona se não for administrador.
    """
    if not is_admin(request.user):
        return redirect("login")
    return render(request, "app_order/painel_admin.html")

@user_passes_test(is_funcionario, login_url="login")
@debug_view  # debug-mode
def listar_os_funcionario(request):
    """
    Lista histórico de OS do funcionário logado.
    """
    ordens = OrdemServico.objects.filter(usuario=request.user)
    return render(
        request,
        "app_order/listar_os_funcionario.html",
        {"ordens": ordens}
    )

@user_passes_test(is_funcionario, login_url="login")
@debug_view  # debug-mode
def concluir_os(request, numero_os):
    """
    Permite ao funcionário concluir uma OS.
    """
    ordem = get_object_or_404(OrdemServico, numero_os=numero_os, usuario=request.user)
    if request.method == "POST":
        form = ConcluirOSForm(request.POST, request.FILES, instance=ordem)
        if form.is_valid():
            ordem = form.save(commit=False)
            ordem.status = "concluida"
            ordem.save()
            messages.success(
                request,
                f"Ordem de serviço nº {ordem.numero_os} concluída com sucesso."
            )
            return redirect("listar_os_funcionario")
    else:
        form = ConcluirOSForm(instance=ordem)
    return render(
        request,
        "app_order/concluir_os.html",
        {"form": form, "os": ordem}
    )

# Protege endpoints de API contra acesso não autenticado
@login_required(login_url="login")
@require_GET
def verificar_numero_os(request, pk):
    """
    Retorna JSON com o número da OS (ou null se não existir).
    """
    try:
        ordem = OrdemServico.objects.get(pk=pk, usuario=request.user)
        return JsonResponse({"numero_os": ordem.numero_os})
    except OrdemServico.DoesNotExist:
        return JsonResponse({"numero_os": None})

@login_required(login_url="login")
@require_GET
def api_os_funcionario(request):
    """
    Retorna JSON com lista de OS do usuário logado.
    """
    ordens = OrdemServico.objects.filter(usuario=request.user)
    dados = list(
        ordens.values("id", "numero_os", "nome_cliente", "descricao", "status")
    )
    return JsonResponse(dados, safe=False)

# print("[DEBUG] Arquivo views.py carregado com sucesso.")  # removido para evitar ruído em produção