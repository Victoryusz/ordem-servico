from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator


class OrdemServico(models.Model):
    """
    Modelo que representa uma Ordem de Serviço solicitada por um colaborador.
    """

    STATUS_CHOICES = [
        ("aguardando", "Aguardando aprovação"),
        ("em_andamento", "Em andamento"),
        ("concluida", "Concluída"),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ordens_servico",
        help_text="Funcionário que abriu esta OS.",
        null=True
    )

    imagem_conclusao = models.ImageField(
        upload_to='os_concluidas/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])],
        help_text="Imagem do serviço concluído."
    )

    comentario_conclusao = models.TextField(
        blank=True,
        null=True,
        help_text="Comentário final do funcionário sobre a conclusão do serviço."
    )

    nome_cliente = models.CharField( # Nome abaixo da box: seu nome completo
        max_length=100,
        help_text=""
    )

#    email_colaborador = models.EmailField(
#        help_text="E-mail para contato com o colaborador."
#    )

    gmg = models.CharField(
        max_length=50,
        verbose_name="GMG",
        help_text="Identificação do Gerador."
    )

    descricao = models.TextField( #Descrição abaixo da box: descreva o serviço
        help_text=""
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="aguardando",
        help_text="Status atual da OS: aguardando, em andamento ou concluída."
    )

    numero_os = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Número da OS gerado pelo administrador (preenchido manualmente)."
    )

    data_solicitacao = models.DateTimeField(
        auto_now_add=True,
        help_text="Data e hora da criação da solicitação."
    )

    def save(self, *args, **kwargs):
        """
        Se o número da OS for preenchido e o status ainda for 'aguardando',
        atualiza automaticamente o status para 'em andamento'.
        """
        if self.numero_os and self.status == "aguardando":
            self.status = "em_andamento"

        super().save(*args, **kwargs)

numero_os = models.CharField(max_length=20, unique=True, blank=True, null=True)
