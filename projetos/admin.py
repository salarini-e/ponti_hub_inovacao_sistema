from django.contrib import admin
from django.db import models
from django.forms import TextInput, Textarea
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import *

# =============================================================================
# CONFIGURAÇÕES BASE
# =============================================================================

# Widget personalizado para campos de texto grandes
formfield_overrides = {
    models.CharField: {'widget': TextInput(attrs={'size': '80'})},
    models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 80})},
}

# =============================================================================
# INLINES
# =============================================================================

class EquipeProjetoInline(admin.TabularInline):
    model = EquipeProjeto
    extra = 1
    fields = ['membro', 'papel', 'responsabilidades', 'dedicacao_percentual', 
              'data_entrada', 'data_saida', 'ativo']

class RecursoProjetoInline(admin.TabularInline):
    model = RecursoProjeto
    extra = 1
    fields = ['nome', 'tipo', 'quantidade_necessaria', 'quantidade_alocada', 
              'unidade_medida', 'custo_unitario', 'data_necessidade']

class FaseProjetoInline(admin.TabularInline):
    model = FaseProjeto
    extra = 1
    fields = ['ordem', 'nome', 'data_inicio_prevista', 'data_fim_prevista', 
              'percentual_conclusao', 'status']

class EntregaInline(admin.TabularInline):
    model = Entrega
    extra = 1
    fields = ['nome', 'tipo', 'responsavel', 'data_prevista', 'status']

class RiscoProjetoInline(admin.TabularInline):
    model = RiscoProjeto
    extra = 1
    fields = ['titulo', 'categoria', 'probabilidade', 'impacto', 'responsavel', 'status']

class StakeholderProjetoInline(admin.TabularInline):
    model = StakeholderProjeto
    extra = 1
    fields = ['nome', 'cargo', 'tipo', 'nivel_influencia', 'nivel_interesse']

class AnexoProjetoInline(admin.TabularInline):
    model = AnexoProjeto
    extra = 1
    fields = ['nome', 'categoria', 'tipo', 'arquivo', 'link', 'versao']

# =============================================================================
# CONFIGURAÇÕES
# =============================================================================

@admin.register(CategoriaEstrategica)
class CategoriaEstrategicaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'peso_estrategico', 'cor_display', 'ativo', 'criado_em']
    list_filter = ['ativo', 'peso_estrategico']
    search_fields = ['nome', 'descricao']
    list_editable = ['peso_estrategico', 'ativo']
    readonly_fields = ['uuid', 'criado_em', 'atualizado_em']
    fieldsets = [
        ('Informações Básicas', {
            'fields': ['nome', 'descricao']
        }),
        ('Configurações', {
            'fields': ['cor', 'icone', 'peso_estrategico', 'ativo']
        }),
        ('Controle', {
            'fields': ['uuid', 'criado_em', 'atualizado_em'],
            'classes': ['collapse']
        })
    ]
    
    def cor_display(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 5px 15px; color: white; border-radius: 3px;">{}</span>',
            obj.cor, obj.cor
        )
    cor_display.short_description = 'Cor'

@admin.register(TipoProjeto)
class TipoProjetoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'prefixo', 'metodologia_sugerida', 'ativo']
    list_filter = ['metodologia_sugerida', 'ativo']
    search_fields = ['nome', 'descricao']
    readonly_fields = ['uuid', 'criado_em', 'atualizado_em']

@admin.register(UnidadeOrganizacional)
class UnidadeOrganizacionalAdmin(admin.ModelAdmin):
    list_display = ['nome', 'sigla', 'responsavel', 'unidade_pai', 'ativo']
    list_filter = ['ativo', 'unidade_pai']
    search_fields = ['nome', 'sigla', 'descricao']
    readonly_fields = ['uuid', 'criado_em', 'atualizado_em']

# =============================================================================
# PORTFÓLIO
# =============================================================================

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nome', 'gestor_portfolio', 'status', 'prioridade', 
                   'orcamento_total', 'percentual_display']
    list_filter = ['status', 'prioridade', 'categoria_estrategica', 'unidade_organizacional']
    search_fields = ['codigo', 'nome', 'descricao']
    date_hierarchy = 'data_inicio'
    readonly_fields = ['uuid', 'criado_em', 'atualizado_em', 'percentual_display']
    
    fieldsets = [
        ('Identificação', {
            'fields': ['codigo', 'nome', 'descricao']
        }),
        ('Responsabilidades', {
            'fields': ['gestor_portfolio', 'patrocinador', 'unidade_organizacional']
        }),
        ('Alinhamento Estratégico', {
            'fields': ['categoria_estrategica']
        }),
        ('Orçamento e Cronograma', {
            'fields': ['orcamento_total', 'data_inicio', 'data_fim_prevista', 'data_fim_real']
        }),
        ('Status e Controle', {
            'fields': ['status', 'prioridade', 'ativo']
        }),
        ('Informações do Sistema', {
            'fields': ['uuid', 'percentual_display', 'criado_em', 'atualizado_em'],
            'classes': ['collapse']
        })
    ]
    
    def percentual_display(self, obj):
        percentual = obj.get_percentual_conclusao()
        cor = '#28a745' if percentual >= 80 else '#ffc107' if percentual >= 50 else '#dc3545'
        return format_html(
            '<div style="width: 100px; background-color: #f8f9fa; border-radius: 5px; padding: 2px;">'
            '<div style="width: {}%; background-color: {}; height: 20px; border-radius: 3px; text-align: center; color: white; font-size: 12px; line-height: 20px;">'
            '{:.1f}%</div></div>',
            percentual, cor, percentual
        )
    percentual_display.short_description = 'Conclusão'

# =============================================================================
# PROGRAMA
# =============================================================================

@admin.register(Programa)
class ProgramaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nome', 'portfolio', 'gerente_programa', 'status', 
                   'prioridade', 'percentual_display']
    list_filter = ['status', 'prioridade', 'portfolio']
    search_fields = ['codigo', 'nome', 'descricao']
    date_hierarchy = 'data_inicio'
    readonly_fields = ['uuid', 'criado_em', 'atualizado_em', 'percentual_display']
    
    fieldsets = [
        ('Identificação', {
            'fields': ['codigo', 'nome', 'descricao', 'portfolio']
        }),
        ('Responsabilidades', {
            'fields': ['gerente_programa']
        }),
        ('Objetivos e Benefícios', {
            'fields': ['objetivos', 'beneficios_esperados']
        }),
        ('Orçamento e Cronograma', {
            'fields': ['orcamento_total', 'data_inicio', 'data_fim_prevista', 'data_fim_real']
        }),
        ('Status e Controle', {
            'fields': ['status', 'prioridade', 'ativo']
        }),
        ('Informações do Sistema', {
            'fields': ['uuid', 'percentual_display', 'criado_em', 'atualizado_em'],
            'classes': ['collapse']
        })
    ]
    
    def percentual_display(self, obj):
        percentual = obj.get_percentual_conclusao()
        cor = '#28a745' if percentual >= 80 else '#ffc107' if percentual >= 50 else '#dc3545'
        return format_html(
            '<div style="width: 100px; background-color: #f8f9fa; border-radius: 5px; padding: 2px;">'
            '<div style="width: {}%; background-color: {}; height: 20px; border-radius: 3px; text-align: center; color: white; font-size: 12px; line-height: 20px;">'
            '{:.1f}%</div></div>',
            percentual, cor, percentual
        )
    percentual_display.short_description = 'Conclusão'

# =============================================================================
# PROJETO
# =============================================================================

@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nome', 'gerente_projeto', 'status', 'prioridade', 
                   'percentual_conclusao', 'orcamento_display', 'prazo_display']
    list_filter = ['status', 'prioridade', 'tipo_projeto', 'metodologia', 'portfolio', 'programa']
    search_fields = ['codigo', 'nome', 'descricao']
    date_hierarchy = 'data_inicio_prevista'
    readonly_fields = ['uuid', 'criado_em', 'atualizado_em']
    
    inlines = [
        EquipeProjetoInline,
        FaseProjetoInline,
        EntregaInline,
        RecursoProjetoInline,
        RiscoProjetoInline,
        StakeholderProjetoInline,
        AnexoProjetoInline,
    ]
    
    fieldsets = [
        ('Identificação', {
            'fields': ['codigo', 'nome', 'descricao', 'tipo_projeto']
        }),
        ('Hierarquia', {
            'fields': ['portfolio', 'programa']
        }),
        ('Responsabilidades', {
            'fields': ['gerente_projeto', 'patrocinador']
        }),
        ('Definição do Projeto', {
            'fields': ['objetivos', 'escopo_produto', 'escopo_trabalho', 
                      'premissas', 'restricoes', 'nao_escopo']
        }),
        ('Orçamento', {
            'fields': ['orcamento_total', 'orcamento_consumido']
        }),
        ('Cronograma', {
            'fields': ['data_inicio_prevista', 'data_inicio_real', 
                      'data_fim_prevista', 'data_fim_real']
        }),
        ('Status e Controle', {
            'fields': ['percentual_conclusao', 'status', 'prioridade', 'metodologia', 'ativo']
        }),
        ('Informações do Sistema', {
            'fields': ['uuid', 'criado_em', 'atualizado_em'],
            'classes': ['collapse']
        })
    ]
    
    formfield_overrides = formfield_overrides
    
    def orcamento_display(self, obj):
        percentual = obj.get_percentual_orcamento_consumido()
        cor = '#dc3545' if percentual > 90 else '#ffc107' if percentual > 75 else '#28a745'
        return format_html(
            'R$ {:,.2f}<br><small style="color: {};">{:.1f}% consumido</small>',
            obj.orcamento_total, cor, percentual
        )
    orcamento_display.short_description = 'Orçamento'
    
    def prazo_display(self, obj):
        status_prazo = obj.get_status_prazo()
        cor_map = {'no_prazo': '#28a745', 'atencao': '#ffc107', 'atrasado': '#dc3545'}
        status_map = {'no_prazo': 'No Prazo', 'atencao': 'Atenção', 'atrasado': 'Atrasado'}
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            cor_map.get(status_prazo, '#6c757d'),
            status_map.get(status_prazo, 'N/A')
        )
    prazo_display.short_description = 'Status Prazo'

# =============================================================================
# GESTÃO DE EQUIPE E RECURSOS
# =============================================================================

@admin.register(EquipeProjeto)
class EquipeProjetoAdmin(admin.ModelAdmin):
    list_display = ['projeto', 'membro', 'papel', 'dedicacao_percentual', 'data_entrada', 'ativo']
    list_filter = ['papel', 'ativo', 'projeto']
    search_fields = ['membro__first_name', 'membro__last_name', 'projeto__nome']
    readonly_fields = ['uuid', 'criado_em']

@admin.register(RecursoProjeto)
class RecursoProjetoAdmin(admin.ModelAdmin):
    list_display = ['projeto', 'nome', 'tipo', 'quantidade_necessaria', 
                   'quantidade_alocada', 'percentual_display']
    list_filter = ['tipo', 'projeto']
    search_fields = ['nome', 'projeto__nome']
    readonly_fields = ['uuid', 'criado_em']
    
    def percentual_display(self, obj):
        percentual = obj.get_percentual_alocado()
        cor = '#28a745' if percentual >= 100 else '#ffc107' if percentual >= 75 else '#dc3545'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            cor, percentual
        )
    percentual_display.short_description = '% Alocado'

# =============================================================================
# CRONOGRAMA E ENTREGAS
# =============================================================================

@admin.register(FaseProjeto)
class FaseProjetoAdmin(admin.ModelAdmin):
    list_display = ['projeto', 'ordem', 'nome', 'data_inicio_prevista', 
                   'data_fim_prevista', 'percentual_conclusao', 'status']
    list_filter = ['status', 'projeto']
    search_fields = ['nome', 'projeto__nome']
    readonly_fields = ['uuid', 'criado_em']

@admin.register(Entrega)
class EntregaAdmin(admin.ModelAdmin):
    list_display = ['projeto', 'nome', 'tipo', 'responsavel', 'data_prevista', 
                   'status', 'prazo_display']
    list_filter = ['tipo', 'status', 'projeto']
    search_fields = ['nome', 'projeto__nome']
    readonly_fields = ['uuid', 'criado_em']
    
    def prazo_display(self, obj):
        status_prazo = obj.get_status_prazo()
        cor_map = {'no_prazo': '#28a745', 'atencao': '#ffc107', 'atrasado': '#dc3545'}
        status_map = {'no_prazo': 'No Prazo', 'atencao': 'Atenção', 'atrasado': 'Atrasado'}
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            cor_map.get(status_prazo, '#6c757d'),
            status_map.get(status_prazo, 'N/A')
        )
    prazo_display.short_description = 'Status Prazo'

@admin.register(Marco)
class MarcoAdmin(admin.ModelAdmin):
    list_display = ['projeto', 'nome', 'tipo', 'data_prevista', 'data_real', 'status']
    list_filter = ['tipo', 'status', 'projeto']
    search_fields = ['nome', 'projeto__nome']
    readonly_fields = ['uuid', 'criado_em']

# =============================================================================
# GESTÃO DE RISCOS
# =============================================================================

@admin.register(RiscoProjeto)
class RiscoProjetoAdmin(admin.ModelAdmin):
    list_display = ['projeto', 'titulo', 'categoria', 'probabilidade', 
                   'impacto', 'nivel_display', 'responsavel', 'status']
    list_filter = ['categoria', 'probabilidade', 'impacto', 'status', 'projeto']
    search_fields = ['titulo', 'descricao', 'projeto__nome']
    readonly_fields = ['uuid', 'criado_em', 'atualizado_em']
    
    def nivel_display(self, obj):
        nivel = obj.get_nivel_risco()
        cor_map = {'baixo': '#28a745', 'medio': '#ffc107', 'alto': '#dc3545'}
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            cor_map.get(nivel, '#6c757d'),
            nivel.title()
        )
    nivel_display.short_description = 'Nível'

# =============================================================================
# COMUNICAÇÃO E MUDANÇAS
# =============================================================================

@admin.register(StakeholderProjeto)
class StakeholderProjetoAdmin(admin.ModelAdmin):
    list_display = ['projeto', 'nome', 'cargo', 'tipo', 'nivel_influencia', 
                   'nivel_interesse', 'frequencia_comunicacao']
    list_filter = ['tipo', 'nivel_influencia', 'nivel_interesse', 'projeto']
    search_fields = ['nome', 'cargo', 'organizacao', 'projeto__nome']
    readonly_fields = ['uuid', 'criado_em']

@admin.register(SolicitacaoMudanca)
class SolicitacaoMudancaAdmin(admin.ModelAdmin):
    list_display = ['numero', 'projeto', 'titulo', 'solicitante', 'status', 
                   'data_solicitacao', 'impacto_orcamento']
    list_filter = ['status', 'projeto']
    search_fields = ['numero', 'titulo', 'projeto__nome']
    readonly_fields = ['uuid', 'criado_em', 'atualizado_em']
    date_hierarchy = 'data_solicitacao'

# =============================================================================
# ANEXOS E DOCUMENTOS
# =============================================================================

@admin.register(AnexoProjeto)
class AnexoProjetoAdmin(admin.ModelAdmin):
    list_display = ['projeto', 'nome', 'categoria', 'tipo', 'versao', 'autor', 'atualizado_em']
    list_filter = ['categoria', 'tipo', 'projeto']
    search_fields = ['nome', 'descricao', 'projeto__nome']
    readonly_fields = ['uuid', 'criado_em', 'atualizado_em']

# =============================================================================
# CONFIGURAÇÕES DO ADMIN
# =============================================================================

# Customização do site admin
admin.site.site_header = "PONTI - Sistema de Gestão de Projetos"
admin.site.site_title = "PONTI - Projetos"
admin.site.index_title = "Gerenciamento de Projetos, Programas e Portfólios"
