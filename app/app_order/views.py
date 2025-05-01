from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import OrdemServicoForm
from .models import OrdemServico

#############################################################
# ORDEM DE SERVIÇO
#############################################################


@login_required(login_url="login")  # Garante que só usuários logados podem abrir OS
def solicitar_os(request):
    """
    View responsável por exibir o formulário de OS ao cliente
    e processar os dados enviados para salvar no banco.
    """

    if request.method == "POST":
        form = OrdemServicoForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("os_sucesso")  # Redireciona para a tela de sucesso

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
    Exibe a tela de login e realiza a autenticação do usuário.
    """
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("solicitar_os")
        else:
            messages.error(request, "Usuário ou senha inválidos.")

    return render(request, "app_order/login.html")


def logout_view(request):
    """
    Faz logout do usuário e redireciona para a tela de login.
    """
    logout(request)
    return redirect("login")
