from django import forms
from django.contrib.auth.models import User
from .models import Portfolio, CategoriaEstrategica, UnidadeOrganizacional, StatusChoices, PrioridadeChoices, Programa


class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = [
            'nome',
            'codigo',
            'descricao',
            'categoria_estrategica',
            'unidade_organizacional',
            'gestor_portfolio',
            'patrocinador',
            'status',
            'prioridade',
            'data_inicio',
            'data_fim_prevista',
            'orcamento_total',
        ]
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do portfólio'
            }),
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código único do portfólio (ex: PORT-001)'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descrição detalhada do portfólio'
            }),
            'categoria_estrategica': forms.Select(attrs={
                'class': 'form-control'
            }),
            'unidade_organizacional': forms.Select(attrs={
                'class': 'form-control'
            }),
            'gestor_portfolio': forms.Select(attrs={
                'class': 'form-control'
            }),
            'patrocinador': forms.Select(attrs={
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'prioridade': forms.Select(attrs={
                'class': 'form-control'
            }),
            'data_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'data_fim_prevista': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'orcamento_total': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
        }
        labels = {
            'nome': 'Nome do Portfólio',
            'codigo': 'Código',
            'descricao': 'Descrição',
            'categoria_estrategica': 'Categoria Estratégica',
            'unidade_organizacional': 'Unidade Organizacional',
            'gestor_portfolio': 'Gestor do Portfólio',
            'patrocinador': 'Patrocinador',
            'status': 'Status',
            'prioridade': 'Prioridade',
            'data_inicio': 'Data de Início',
            'data_fim_prevista': 'Data de Fim Prevista',
            'orcamento_total': 'Orçamento Total (R$)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar queryset para usuários
        self.fields['gestor_portfolio'].queryset = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
        self.fields['patrocinador'].queryset = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
        
        # Configurar choices para status e prioridade
        self.fields['status'].choices = StatusChoices.choices
        self.fields['prioridade'].choices = PrioridadeChoices.choices
        
        # Adicionar classes CSS extras
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
            
            # Adicionar asterisco para campos obrigatórios
            if field.required:
                field.label = f"{field.label} *"

    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo')
        if codigo:
            # Verificar se o código já existe (exceto para o próprio objeto na edição)
            queryset = Portfolio.objects.filter(codigo=codigo)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise forms.ValidationError('Este código já está em uso. Escolha outro.')
        
        return codigo

    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim_prevista = cleaned_data.get('data_fim_prevista')
        
        if data_inicio and data_fim_prevista:
            if data_inicio >= data_fim_prevista:
                raise forms.ValidationError('A data de fim deve ser posterior à data de início.')
        
        return cleaned_data


class ProgramaForm(forms.ModelForm):
    class Meta:
        model = Programa
        fields = [
            'nome',
            'codigo',
            'descricao',
            'portfolio',
            'gerente_programa',
            'objetivos',
            'beneficios_esperados',
            'orcamento_total',
            'data_inicio',
            'data_fim_prevista',
            'status',
            'prioridade',
        ]
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do programa'
            }),
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código único do programa (ex: PROG-001)'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descrição detalhada do programa'
            }),
            'portfolio': forms.Select(attrs={
                'class': 'form-control'
            }),
            'gerente_programa': forms.Select(attrs={
                'class': 'form-control'
            }),
            'objetivos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Objetivos do programa'
            }),
            'beneficios_esperados': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Benefícios esperados com o programa'
            }),
            'orcamento_total': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'data_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'data_fim_prevista': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'prioridade': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'nome': 'Nome do Programa',
            'codigo': 'Código',
            'descricao': 'Descrição',
            'portfolio': 'Portfólio',
            'gerente_programa': 'Gerente do Programa',
            'objetivos': 'Objetivos',
            'beneficios_esperados': 'Benefícios Esperados',
            'orcamento_total': 'Orçamento Total (R$)',
            'data_inicio': 'Data de Início',
            'data_fim_prevista': 'Data de Fim Prevista',
            'status': 'Status',
            'prioridade': 'Prioridade',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar queryset para usuários
        self.fields['gerente_programa'].queryset = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
        
        # Configurar choices para status e prioridade
        self.fields['status'].choices = StatusChoices.choices
        self.fields['prioridade'].choices = PrioridadeChoices.choices
        
        # Adicionar classes CSS extras
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
            
            # Adicionar asterisco para campos obrigatórios
            if field.required:
                field.label = f"{field.label} *"

    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo')
        if codigo:
            # Verificar se o código já existe (exceto para o próprio objeto na edição)
            queryset = Programa.objects.filter(codigo=codigo)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise forms.ValidationError('Este código já está em uso. Escolha outro.')
        
        return codigo

    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim_prevista = cleaned_data.get('data_fim_prevista')
        
        if data_inicio and data_fim_prevista:
            if data_inicio >= data_fim_prevista:
                raise forms.ValidationError('A data de fim deve ser posterior à data de início.')
        
        return cleaned_data