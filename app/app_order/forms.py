from django import forms
from .models import OrdemServico
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class OrdemServicoForm(forms.ModelForm):
    """
    Formulário baseado no modelo OrdemServico.
    Usado para que o colaborador possa enviar uma solicitação de OS.
    """

    class Meta:
        model = OrdemServico  # Diz ao Django de qual model esse form se baseia
        fields = [
            "nome_cliente",
            "gmg",
            "descricao",
        ]  # Campos que o usuário pode preencher

        # Labels mais amigáveis (opcional, mas melhora a aparência)
        labels = {
            "nome_cliente": "Nome do Técnico",
            "gmg": "GMG do Gerador",
            "descricao": "Tipo de serviço a ser executado",
        }

        # Campos com widgets do Bootstrap (será aplicado no HTML)
        widgets = {
            "descricao": forms.Textarea(
                attrs={
                    "rows": 5,
                    "class": "form-control",
                    "placeholder": "Descreva o serviço ex: Montagem do motor, revisão, troca de filtros, limpeza...",
                }
            ),
            "nome_cliente": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Seu nome completo"}
            ),
            "gmg": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ex: 432"}
            ),
        }


class RegistroUsuarioForm(forms.ModelForm):
    """
    Formulário para registrar um novo usuário (usuário e senha).
    """

    # Campos adicionais para senha e confirmação
    password = forms.CharField(
        label="Senha", widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    confirm_password = forms.CharField(
        label="Confirmar senha",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = User
        fields = ["username", "email"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def clean(self):
        """
        Verifica se as senhas coincidem.
        """
        cleaned_data = super().clean()
        senha = cleaned_data.get("password")
        confirmar = cleaned_data.get("confirm_password")

        if senha and confirmar and senha != confirmar:
            raise ValidationError("As senhas não coincidem.")

    def save(self, commit=True):
        """
        ⚠️ Método ajustado:
        Salva o usuário com a senha criptografada usando `set_password`,
        garantindo compatibilidade com o sistema de autenticação do Django.
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # 🔐 Criptografa a senha
        if commit:
            user.save()
        return user


class ConcluirOSForm(forms.ModelForm):
    class Meta:
        model = OrdemServico
        fields = ["imagem_conclusao", "comentario_conclusao"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Torna o campo de imagem obrigatório
        self.fields["imagem_conclusao"].required = True
