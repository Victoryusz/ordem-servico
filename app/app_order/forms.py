from django import forms
from .models import OrdemServico

class OrdemServicoForm(forms.ModelForm):
    """
    Formulário baseado no modelo OrdemServico.
    Usado para que o cliente possa enviar uma solicitação de OS.
    """

    class Meta:
        model = OrdemServico  # Diz ao Django de qual model esse form se baseia
        fields = ['nome_cliente', 'email_cliente', 'gmg', 'descricao']  # Campos que o usuário pode preencher

        # Labels mais amigáveis (opcional, mas melhora a aparência)
        labels = {
            'nome_cliente': 'Nome completo',
            'email_cliente': 'E-mail para contato',
            'gmg': 'GMG',
            'descricao': 'Descreva o problema',
        }

        # Campos com widgets do Bootstrap (será aplicado no HTML)
        widgets = {
            'descricao': forms.Textarea(attrs={
                'rows': 5,
                'class': 'form-control',
                'placeholder': 'Descreva detalhadamente o problema...'
            }),
            'nome_cliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Seu nome completo'
            }),
            'email_cliente': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'exemplo@empresa.com'
            }),
            'gmg': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: GMG123456'
            }),
        }
