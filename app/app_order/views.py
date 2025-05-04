from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import OrdemServicoForm, RegistroUsuarioForm, ConcluirOSForm
from .models import OrdemServico

#############################################################
# ORDEM DE SERVIÇO
#############################################################

### Debuggando
def debug_view(func):
    def wrapper(request, *args, **kwargs):
        print(f"[DEBUG] View chamada: {func.__name__}")
        return func(request, *args, **kwargs)
    return wrapper
### Debuggando

@login_required(login_url="login")
@debug_view  # 👈 debug-mode
def solicitar_os(request):
    """
    View responsável por exibir o formulário de OS ao cliente
    e processar os dados enviados para salvar no banco.
    """
    if request.method == "POST":
        form = OrdemServicoForm(request.POST)
        if form.is_valid():
            os = form.save(commit=False)
            os.usuario = request.user
            os.save()
            return redirect("os_sucesso")
    else:
        form = OrdemServicoForm()

    return render(request, "app_order/solicitar_os.html", {"form": form})


def os_sucesso(request):
    """
    Exibe mensagem de sucesso e, se já houver número da OS,
    exibe também ao solicitante.
    """
    ultima_os = OrdemServico.objects.last()
    return render(request, "app_order/os_sucesso.html", {"ordem_servico": ultima_os})

#############################################################
# AUTENTICAÇÃO DE USUÁRIO
#############################################################

def login_view(request):
    """
    Exibe a tela de login e redireciona conforme o perfil do usuário.
    Se houver parâmetro ?next=, redireciona para ele após login.
    """
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        next_url = request.POST.get("next")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if next_url:
                return redirect(next_url)

            if is_admin(user):
                return redirect("painel_admin")
            elif is_funcionario(user):
                return redirect("painel_funcionario")
            else:
                return redirect("solicitar_os")

        else:
            messages.error(request, "Usuário ou senha inválidos.")

    else:
        next_url = request.GET.get("next", "")

    return render(request, "app_order/login.html", {"next": next_url})


def register_view(request):
    """
    Exibe o formulário de cadastro e cria um novo usuário.
    A senha já será tratada com segurança pelo método `save()` do formulário.
    """
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()  # 👍 Já chama set_password internamente
            login(request, user)  # Autentica automaticamente após o cadastro
            return redirect("solicitar_os")
    else:
        form = RegistroUsuarioForm()

    return render(request, "app_order/register.html", {"form": form})


# Função que verifica se o usuário é funcionário
def is_funcionario(user):
    return user.groups.filter(name="Funcionario").exists()


# Função que verifica se o usuário é administrador (com print de debug)
def is_admin(user):
    if user.is_superuser:
        print(f"[DEBUG] {user.username} é superusuário — acesso liberado.")
        return True

    grupos = [g.name for g in user.groups.all()]
    print(f"[DEBUG] {user.username} - Grupos: {grupos}")
    return "Administrador" in grupos


def logout_view(request):
    """
    Faz logout do usuário e redireciona para a tela de login.
    """
    logout(request)
    return redirect("login")


@user_passes_test(is_funcionario, login_url="login")
@debug_view  # 👈 debug-mode
def painel_funcionario(request):
    return render(request, "app_order/painel_funcionario.html")


@login_required(login_url="login")
@debug_view  # 👈 debug-mode
def painel_admin(request):
    if not is_admin(request.user):
        print("[DEBUG] Acesso negado! Usuário não reconhecido como admin.")
        return redirect("login")

    return render(request, "app_order/painel_admin.html")


@user_passes_test(is_funcionario, login_url="login")
@debug_view  # 👈 debug-mode
def listar_os_funcionario(request):
    """
    Lista todas as OS do funcionário logado (histórico completo).
    """
    os_funcionario = OrdemServico.objects.filter(usuario=request.user)
    return render(
        request, "app_order/listar_os_funcionario.html", {"ordens": os_funcionario}
    )


@user_passes_test(is_funcionario, login_url='login')
@debug_view ## debug mode
def concluir_os(request, numero_os):
    """
    Permite ao funcionário concluir uma OS: enviar imagem e comentário.
    """
    os = get_object_or_404(OrdemServico, numero_os=numero_os, usuario=request.user)

    if request.method == "POST":
        form = ConcluirOSForm(request.POST, request.FILES, instance=os)
        if form.is_valid():
            os = form.save(commit=False)
            os.status = "concluida"
            os.save()
            messages.success(request, f"Ordem de serviço nº {os.numero_os} foi concluída com sucesso.")
            return redirect("listar_os_funcionario")
    else:
        form = ConcluirOSForm(instance=os)

    return render(request, "app_order/concluir_os.html", {"form": form, "os": os})

## Debugando
print("[DEBUG] Arquivo views.py carregado com sucesso.")