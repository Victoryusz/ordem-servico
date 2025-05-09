from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import OrdemServico

User = get_user_model()


class OrdemServicoForm(forms.ModelForm):
    """
    Form para colaborador solicitar OS.
    """

    class Meta:
        model = OrdemServico
        fields = ["nome_cliente", "gmg", "descricao"]
        labels = {
            "nome_cliente": "Nome do Técnico",
            "gmg": "GMG do Gerador",
            "descricao": "Tipo de serviço a ser executado",
        }
        widgets = {
            "nome_cliente": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Seu nome completo"}
            ),
            "gmg": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ex: 432"}
            ),
            "descricao": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": (
                        "Descreva o serviço ex: Montagem do motor, revisão, "
                        "troca de filtros, limpeza..."
                    ),
                }
            ),
        }


class RegistroUsuarioForm(forms.ModelForm):
    """
    Form para registrar usuário com confirmação de senha.
    """

    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
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
        pwd = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")
        if pwd and confirm and pwd != confirm:
            self.add_error("confirm_password", "As senhas não coincidem.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class StageActionForm(forms.Form):
    """
    Form para ações na etapa: concluir, repassar ou finalizar OS.
    """

    comentario = forms.CharField(
        label="Comentário",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    )
    foto = forms.ImageField(
        label="Foto (obrigatória)",
        required=True,  # agora é obrigatório
        widget=forms.ClearableFileInput(attrs={"class": "form-control"}),
    )
    repassar_para = forms.ModelChoiceField(
        label="Repassar para",
        required=False,
        queryset=User.objects.none(),  # queryset configurado no __init__
        help_text="Escolha outro técnico (opcional).",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    finalizar_os = forms.BooleanField(
        label="Finalizar OS",
        required=False,
        help_text="Marcar OS como encerrada após esta etapa.",
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields["repassar_para"].queryset = User.objects.filter(
                groups__name="Funcionario"
            ).exclude(pk=user.pk)

    def clean(self):
        data = super().clean()

        # ❌ não permitir repassar E finalizar ao mesmo tempo
        if data.get("repassar_para") and data.get("finalizar_os"):
            raise ValidationError(
                "Não é possível repassar e finalizar a OS ao mesmo tempo."
            )

        # ❌ foto obrigatória
        if not data.get("foto"):
            raise ValidationError("É obrigatório enviar uma foto para esta etapa.")

        # ❌ exigir repassar OU finalizar
        if not data.get("repassar_para") and not data.get("finalizar_os"):
            raise ValidationError(
                "Você deve repassar a OS para outro técnico ou marcar “Finalizar OS”."
            )

        return data
