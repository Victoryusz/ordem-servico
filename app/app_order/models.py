# Create your models here.
from django.db import models

class OrdemServico(models.Model):
    """
    Modelo que representa uma Ordem de Serviço solicitada por um cliente.
    """

    STATUS_CHOICES = [
        ('aguardando', 'Aguardando aprovação'),   # padrão inicial
        ('em_andamento', 'Em andamento'),         # após adm inserir o número da OS
        ('concluida', 'Concluída')                # após cliente inserir o código de finalização
    ]

    nome_cliente = models.CharField(
        max_length=100,
        help_text="Nome do cliente que está solicitando o serviço."
    )

    email_cliente = models.EmailField(
        help_text="E-mail para contato com o cliente."
    )

    gmg = models.CharField(
        max_length=50,
        verbose_name="GMG",
        help_text="Identificação ou código específico fornecido pelo cliente (ex: GMG: 123456)."
    )

    descricao = models.TextField(
        help_text="Descrição detalhada do problema ou necessidade do cliente."
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='aguardando',
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

    def __str__(self):
        return f"OS {self.numero_os or self.id} - {self.nome_cliente} ({self.status})"
