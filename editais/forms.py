from django import forms
from django.core.exceptions import ValidationError
from .models import NotificacaoEdital
import re


class NotificacaoEditalForm(forms.ModelForm):
    """Formulário para solicitação de notificação de edital"""
    
    cpf = forms.CharField(
        max_length=14,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '000.000.000-00',
            'pattern': r'[0-9]{3}\.?[0-9]{3}\.?[0-9]{3}-?[0-9]{2}',
            'title': 'Digite um CPF válido'
        }),
        label="CPF",
        help_text="Digite seu CPF"
    )
    
    nome_completo = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu nome completo'
        }),
        label="Nome Completo"
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'seu@email.com'
        }),
        label="E-mail"
    )
    
    telefone_whatsapp = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '(00) 00000-0000',
            'pattern': r'\([0-9]{2}\) [0-9]{4,5}-[0-9]{4}'
        }),
        label="Telefone/WhatsApp (Opcional)",
        help_text="Digite seu telefone ou WhatsApp"
    )
    
    # Campo oculto para aceitar termos
    aceito_termos = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Aceito receber notificações por e-mail sobre este edital",
        error_messages={
            'required': 'Você deve aceitar os termos para continuar.'
        }
    )
    
    class Meta:
        model = NotificacaoEdital
        fields = ['cpf', 'nome_completo', 'email', 'telefone_whatsapp']
    
    def clean_cpf(self):
        """Validação do CPF"""
        cpf = self.cleaned_data.get('cpf')
        if not cpf:
            raise ValidationError('CPF é obrigatório.')
        
        # Remove caracteres especiais
        cpf_limpo = re.sub(r'[^0-9]', '', cpf)
        
        # Verifica se tem 11 dígitos
        if len(cpf_limpo) != 11:
            raise ValidationError('CPF deve ter 11 dígitos.')
        
        # Verifica se não são todos os números iguais
        if cpf_limpo == cpf_limpo[0] * 11:
            raise ValidationError('CPF inválido.')
        
        # Algoritmo de validação do CPF
        def calcular_digito(cpf_parcial, peso_inicial):
            soma = sum(int(digito) * peso for digito, peso in zip(cpf_parcial, range(peso_inicial, 1, -1)))
            resto = soma % 11
            return 0 if resto < 2 else 11 - resto
        
        # Validar primeiro dígito
        if int(cpf_limpo[9]) != calcular_digito(cpf_limpo[:9], 10):
            raise ValidationError('CPF inválido.')
        
        # Validar segundo dígito
        if int(cpf_limpo[10]) != calcular_digito(cpf_limpo[:10], 11):
            raise ValidationError('CPF inválido.')
        
        # Formatar CPF
        return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
    
    def clean_telefone_whatsapp(self):
        """Validação do telefone"""
        telefone = self.cleaned_data.get('telefone_whatsapp')
        if not telefone:
            return telefone
        
        # Remove caracteres especiais
        telefone_limpo = re.sub(r'[^0-9]', '', telefone)
        
        # Verifica se tem pelo menos 10 dígitos (telefone fixo) ou 11 (celular)
        if len(telefone_limpo) not in [10, 11]:
            raise ValidationError('Telefone deve ter 10 ou 11 dígitos.')
        
        # Formatar telefone
        if len(telefone_limpo) == 10:
            return f"({telefone_limpo[:2]}) {telefone_limpo[2:6]}-{telefone_limpo[6:]}"
        else:
            return f"({telefone_limpo[:2]}) {telefone_limpo[2:7]}-{telefone_limpo[7:]}"
    
    def clean(self):
        """Validação geral do formulário"""
        cleaned_data = super().clean()
        cpf = cleaned_data.get('cpf')
        email = cleaned_data.get('email')
        edital = getattr(self.instance, 'edital', None)
        
        # Verificar se já existe notificação para este CPF e edital
        if cpf and edital:
            if NotificacaoEdital.objects.filter(cpf=cpf, edital=edital).exists():
                raise ValidationError('Você já solicitou notificação para este edital com este CPF.')
        
        return cleaned_data