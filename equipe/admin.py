from django.contrib import admin
from django.utils.html import format_html
from .models import Cargo, AreaEspecialidade, MembroEquipe, LiderancaDestaque


@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'nivel_hierarquico', 'ativo', 'criado_em']
    list_filter = ['nivel_hierarquico', 'ativo']
    search_fields = ['nome', 'descricao']
    ordering = ['nivel_hierarquico', 'nome']
    list_editable = ['nivel_hierarquico', 'ativo']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'nivel_hierarquico')
        }),
        ('Controle', {
            'fields': ('ativo',)
        })
    )


@admin.register(AreaEspecialidade)
class AreaEspecialidadeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'icone', 'cor_preview', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome']
    list_editable = ['icone', 'ativo']
    
    def cor_preview(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border-radius: 3px; display: inline-block;"></div>',
            obj.cor
        )
    cor_preview.short_description = 'Cor'


class LiderancaDestaqueInline(admin.StackedInline):
    model = LiderancaDestaque
    extra = 0
    fields = (
        'titulo_especial',
        'descricao_lideranca',
        ('ordem_lideranca', 'exibir_na_lideranca'),
        ('estatistica_1_nome', 'estatistica_1_valor'),
        ('estatistica_2_nome', 'estatistica_2_valor'),
    )


@admin.register(MembroEquipe)
class MembroEquipeAdmin(admin.ModelAdmin):
    list_display = [
        'nome_exibicao', 
        'cargo', 
        'tipo', 
        'foto_preview', 
        'destaque', 
        'ativo', 
        'ordem_exibicao'
    ]
    list_filter = ['tipo', 'cargo', 'ativo', 'destaque', 'areas_especialidade']
    search_fields = ['nome_completo', 'nome_exibicao', 'biografia']
    filter_horizontal = ['areas_especialidade']
    list_editable = ['ordem_exibicao', 'ativo', 'destaque']
    ordering = ['destaque', 'ordem_exibicao', 'cargo__nivel_hierarquico']
    inlines = [LiderancaDestaqueInline]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': (
                ('nome_completo', 'nome_exibicao'),
                ('cargo', 'tipo'),
                'biografia'
            )
        }),
        ('Imagem', {
            'fields': ('foto', 'foto_url'),
            'description': 'Adicione uma foto através de upload ou URL externa'
        }),
        ('Especialidades', {
            'fields': ('areas_especialidade',),
        }),
        ('Estatísticas/Métricas', {
            'fields': (
                ('anos_experiencia', 'projetos_concluidos', 'taxa_sucesso'),
                ('metrica_personalizada_nome', 'metrica_personalizada_valor')
            ),
            'classes': ['collapse'],
            'description': 'Métricas opcionais para exibição no perfil'
        }),
        ('Controle de Exibição', {
            'fields': (
                ('ordem_exibicao', 'ativo', 'destaque'),
                'slug'
            )
        })
    )
    
    readonly_fields = ['slug']
    
    def foto_preview(self, obj):
        foto_url = obj.get_foto_url()
        return format_html(
            '<img src="{}" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover;" />',
            foto_url
        )
    foto_preview.short_description = 'Foto'
    
    def save_model(self, request, obj, form, change):
        # Auto-gerar slug se não existir
        if not obj.slug:
            from django.utils.text import slugify
            obj.slug = slugify(obj.nome_exibicao)
        super().save_model(request, obj, form, change)


@admin.register(LiderancaDestaque)
class LiderancaDestaqueAdmin(admin.ModelAdmin):
    list_display = [
        'membro', 
        'titulo_especial', 
        'ordem_lideranca', 
        'exibir_na_lideranca'
    ]
    list_filter = ['exibir_na_lideranca']
    search_fields = ['membro__nome_exibicao', 'titulo_especial']
    list_editable = ['ordem_lideranca', 'exibir_na_lideranca']
    ordering = ['ordem_lideranca']
    
    fieldsets = (
        ('Membro', {
            'fields': ('membro',)
        }),
        ('Configurações da Liderança', {
            'fields': (
                'titulo_especial',
                'descricao_lideranca',
                ('ordem_lideranca', 'exibir_na_lideranca')
            )
        }),
        ('Estatísticas Específicas', {
            'fields': (
                ('estatistica_1_nome', 'estatistica_1_valor'),
                ('estatistica_2_nome', 'estatistica_2_valor')
            ),
            'classes': ['collapse']
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('membro', 'membro__cargo')


# Customização do admin site
admin.site.site_header = "PONTI Hub de Inovação - Administração"
admin.site.site_title = "PONTI Admin"
admin.site.index_title = "Gestão do Hub de Inovação"
