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
        fields = ["nome_cliente", "gmg", "descricao", "prazo_inicial"]
        labels = {
            "nome_cliente": "Nome do Técnico",
            "gmg": "GMG do Gerador",
            "descricao": "Tipo de serviço a ser executado",
            "prazo_inicial": "Prazo para conclusão",
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
            "prazo_inicial": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                    "placeholder": "Data de conclusão",
                }
            ),
        }


class RegistroUsuarioForm(forms.ModelForm):
    """
    Form para registrar usuário com confirmação de senha e aceite de termos.
    """
    nome = forms.CharField(
        label="Nome completo",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Seu nome completo"
        }),
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Digite sua senha"
        }),
    )
    confirm_password = forms.CharField(
        label="Confirmar senha",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirme sua senha"
        }),
    )
    terms = forms.BooleanField(
        label="Estou de acordo com os termos e condições",
        error_messages={"required": "Você deve aceitar os termos e condições."},
    )

    class Meta:
        model = User
        fields = ["username", "email"]
        widgets = {
            "username": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Digite seu usuário"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "seu-email@exemplo.com"
            }),
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
        # salva o nome completo em first_name
        user.first_name = self.cleaned_data.get("nome", "")
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class StageActionForm(forms.Form):
    """
    Form para ações na etapa: concluir, repassar, finalizar OS ou apenas ajustar prazo.
    """
    ajustar_prazo = forms.BooleanField(
        label="Atualizar só o prazo",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        help_text="Marque para apenas alterar o prazo sem concluir nem repassar.",
    )
    prazo_estipulado = forms.DateField(
        label="Novo prazo para conclusão",
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
            }
        ),
        help_text="Ajuste aqui a data limite de conclusão. (SOMENTE SE NECESSÁRIO)",
    )
    comentario = forms.CharField(
        label="Tipo de serviço que você executou",
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 3,
            "placeholder": "Descreva aqui o que você fez na OS."
        }),
    )
    foto = forms.ImageField(
        label="Foto do trabalho (obrigatória)",
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "form-control"}),
    )
    repassar_para = forms.ModelChoiceField(
        label="Repassar para",
        required=False,
        queryset=User.objects.none(),  # será configurado no __init__
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
            self.fields['repassar_para'].queryset = User.objects.filter(
                groups__name='Funcionario'
            ).exclude(pk=user.pk)

    def clean(self):
        data = super().clean()

        # Caso de ajuste puro de prazo
        if data.get('ajustar_prazo'):
            if not data.get('prazo_estipulado'):
                raise ValidationError("Informe a nova data de prazo para concluir a etapa.")
            # Se só ajustar prazo, não exigimos foto ou repasse/finalização
            return data

        # Abaixo, fluxo normal: foto obrigatória + repassar OU finalizar
        if not data.get('foto'):
            raise ValidationError("É obrigatório enviar uma foto para esta etapa.")
        if data.get('repassar_para') and data.get('finalizar_os'):
            raise ValidationError(
                "Não é possível repassar e finalizar a OS ao mesmo tempo."
            )
        if not data.get('repassar_para') and not data.get('finalizar_os'):
            raise ValidationError(
                'Você deve repassar a OS para outro técnico ou marcar “Finalizar OS”.'
            )
        return data
