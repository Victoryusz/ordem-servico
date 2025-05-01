from django.shortcuts import render, redirect
from .models import OrdemServico
from .forms import OrdemServicoForm

def solicitar_os(request):
    """
    View responsável por exibir o formulário de OS ao cliente
    e processar os dados enviados para salvar no banco.
    """

    if request.method == 'POST':
        # Se o cliente enviou o formulário preenchido (método POST)
        form = OrdemServicoForm(request.POST)  # Preenche o form com os dados

        if form.is_valid():  # Validação automática baseada no model
            form.save()      # Salva a OS no banco
            return redirect('os_sucesso')  # Redireciona para página de confirmação
    else:
        # Se for a primeira vez acessando a página (método GET)
        form = OrdemServicoForm()

    # Renderiza a página com o formulário (form.html que vamos criar)
    return render(request, 'app_order/solicitar_os.html', {'form': form})


def os_sucesso(request):
    """
    Página de sucesso após o envio da OS.
    Se a última OS enviada já tiver número atribuído, mostra na tela.
    """
    ultima_os = OrdemServico.objects.last()
    return render(request, 'app_order/os_sucesso.html', {
        'ordem_servico': ultima_os
    })
