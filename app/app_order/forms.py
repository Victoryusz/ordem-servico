from django import forms
from .models import OrdemServico
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class OrdemServicoForm(forms.ModelForm):
    """
    Formulário baseado no modelo OrdemServico.
    Usado para que o cliente possa enviar uma solicitação de OS.
    """

    class Meta:
        model = OrdemServico  # Diz ao Django de qual model esse form se baseia
        fields = [
            "nome_cliente",
            "email_cliente",
            "gmg",
            "descricao",
        ]  # Campos que o usuário pode preencher

        # Labels mais amigáveis (opcional, mas melhora a aparência)
        labels = {
            "nome_cliente": "Nome completo",
            "email_cliente": "E-mail para contato",
            "gmg": "GMG",
            "descricao": "Descreva o problema",
        }

        # Campos com widgets do Bootstrap (será aplicado no HTML)
        widgets = {
            "descricao": forms.Textarea(
                attrs={
                    "rows": 5,
                    "class": "form-control",
                    "placeholder": "Descreva detalhadamente o problema...",
                }
            ),
            "nome_cliente": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Seu nome completo"}
            ),
            "email_cliente": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "exemplo@empresa.com"}
            ),
            "gmg": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ex: GMG123456"}
            ),
        }


class RegistroUsuarioForm(forms.ModelForm):
    """
    Formulário para registrar um novo usuário (usuário e senha).
    """

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
        cleaned_data = super().clean()
        senha = cleaned_data.get("password")
        confirmar = cleaned_data.get("confirm_password")

        if senha and confirmar and senha != confirmar:
            raise ValidationError("As senhas não coincidem.")


class ConcluirOSForm(forms.ModelForm):
    class Meta:
        model = OrdemServico
        fields = ["imagem_conclusao", "comentario_conclusao"]
        widgets = {
            "comentario_conclusao": forms.Textarea(
                attrs={"rows": 4, "class": "form-control"}
            ),
        }
