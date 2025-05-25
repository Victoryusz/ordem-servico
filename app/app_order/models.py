from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.utils import timezone


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
        null=True,
    )
    imagem_conclusao = models.ImageField(
        upload_to="os_concluidas/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(["jpg", "jpeg", "png"])],
        help_text="Imagem do serviço concluído.",
    )
    comentario_conclusao = models.TextField(
        blank=True,
        null=True,
        help_text="Comentário final do funcionário sobre a conclusão do serviço.",
    )
    nome_cliente = models.CharField(
        max_length=100, help_text="Nome do técnico que solicitou."
    )
    gmg = models.CharField(
        max_length=50, verbose_name="GMG", help_text="Identificação do Gerador."
    )
    descricao = models.TextField(help_text="Descrição do serviço.")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="aguardando",
        help_text="Status atual da OS: aguardando, em andamento ou concluída.",
    )
    numero_os = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Número da OS gerado pelo administrador (preenchido manualmente).",
    )
    data_solicitacao = models.DateTimeField(
        auto_now_add=True, help_text="Data e hora da criação da solicitação."
    )
    prazo_inicial = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Prazo inicial estimado para a conclusão do serviço.",
    )
    repass_limite = models.PositiveIntegerField(
        default=5,
        help_text="Máximo de repasses antes de solicitar liberação pelo admin.",
    )
    data_conclusao = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Data e hora em que a OS foi marcada como concluída.",
    )

    def save(self, *args, **kwargs):
        """
        Se o número da OS for preenchido e o status ainda for 'aguardando',
        atualiza automaticamente o status para 'em andamento'.
        Também marca data_conclusao quando passar a 'concluida'.
        """
        if self.numero_os and self.status == "aguardando":
            self.status = "em_andamento"
        # ao concluir, registra timestamp
        if self.status == "concluida" and not self.data_conclusao:
            self.data_conclusao = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"OS {self.numero_os or 'N/A'} - {self.nome_cliente}"


class Stage(models.Model):
    """
    Modelo que representa uma etapa de uma OS, atribuída a um técnico.
    """

    order = models.ForeignKey(
        OrdemServico,
        related_name="stages",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Ordem de Serviço (fica vazio se a OS for excluída).",
    )
    tecnico = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Técnico responsável (fica vazio se excluído).",
    )
    ordem = models.PositiveIntegerField(
        help_text="Sequência da etapa dentro da OS (ex: 1, 2, 3)."
    )
    STATUS_CHOICES = [
        ("em_execucao", "Em execução"),
        ("concluida", "Concluída"),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="em_execucao",
        help_text="Status da etapa: em execução ou concluída.",
    )
    comentario = models.TextField(
        blank=True, help_text="Comentário do técnico ao concluir a etapa."
    )
    foto = models.ImageField(
        upload_to="stages/",
        blank=True,
        null=True,
        help_text="Foto anexada pelo técnico ao concluir a etapa.",
    )
    prazo_estipulado = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Data e hora estimada para a conclusão desta etapa.",
    )
    criado_em = models.DateTimeField(
        auto_now_add=True, help_text="Data e hora de criação da etapa."
    )

    class Meta:
        unique_together = ("order", "ordem")
        ordering = ["order", "ordem"]

    def __str__(self):
        numero = self.order.numero_os or "—"
        return f"OS {numero} – Etapa {self.ordem} ({self.get_status_display()})"
