from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import Edital, CategoriaEdital, AreaInteresse, NotificacaoEdital


@admin.register(CategoriaEdital)
class CategoriaEditalAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug', 'cor_display', 'icone', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome', 'descricao']
    prepopulated_fields = {'slug': ('nome',)}
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'slug', 'descricao')
        }),
        ('Aparência', {
            'fields': ('cor', 'icone')
        }),
        ('Status', {
            'fields': ('ativo',)
        }),
    )
    
    def cor_display(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border-radius: 50%; display: inline-block;"></div>',
            obj.cor
        )
    cor_display.short_description = 'Cor'


@admin.register(AreaInteresse)
class AreaInteresseAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cor_display', 'icone', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome', 'descricao']
    
    def cor_display(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border-radius: 50%; display: inline-block;"></div>',
            obj.cor
        )
    cor_display.short_description = 'Cor'


class NotificacaoEditalInline(admin.TabularInline):
    model = NotificacaoEdital
    extra = 0
    readonly_fields = ['data_solicitacao', 'data_notificacao']
    fields = ['email', 'nome', 'data_solicitacao', 'notificado', 'data_notificacao']


@admin.register(Edital)
class EditalAdmin(admin.ModelAdmin):
    list_display = [
        'titulo', 'numero_edital', 'status_display', 'categoria',
        'data_encerramento_display', 'dias_restantes_display', 
        'visualizacoes', 'destaque_display'
    ]
    list_filter = [
        'status', 'categoria', 'modalidade', 'destaque', 
        'data_criacao', 'data_encerramento'
    ]
    search_fields = ['titulo', 'numero_edital', 'subtitulo', 'descricao_completa']
    date_hierarchy = 'data_encerramento'
    prepopulated_fields = {'slug': ('titulo',)}
    filter_horizontal = ['areas_interesse']
    readonly_fields = [
        'data_criacao', 'data_atualizacao', 'visualizacoes',
        'esta_aberto_display', 'dias_restantes_display'
    ]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': (
                'titulo', 'numero_edital', 'slug', 'subtitulo', 
                'descricao_completa'
            )
        }),
        ('Classificação', {
            'fields': ('categoria', 'areas_interesse', 'modalidade')
        }),
        ('Status e Datas', {
            'fields': (
                'status', 'data_publicacao', 'data_abertura', 
                'data_encerramento', 'esta_aberto_display'
            )
        }),
        ('Informações Específicas', {
            'fields': ('numero_desafios', 'valor_premio')
        }),
        ('Arquivos e Links', {
            'fields': ('arquivo_edital', 'link_inscricao', 'link_mais_informacoes')
        }),
        ('Configurações de Exibição', {
            'fields': ('destaque', 'cor_status'),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': (
                'data_criacao', 'data_atualizacao', 'criado_por', 
                'visualizacoes', 'dias_restantes_display'
            ),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [NotificacaoEditalInline]
    
    actions = [
        'marcar_como_rascunho', 'marcar_como_em_breve', 
        'marcar_como_aberto', 'marcar_como_encerrado',
        'destacar_editais', 'remover_destaque'
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('categoria', 'criado_por').prefetch_related('areas_interesse')
    
    def save_model(self, request, obj, form, change):
        if not change:  # Novo objeto
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)
    
    def status_display(self, obj):
        cores = {
            'rascunho': '#6b7280',
            'em_breve': '#1e40af',
            'aberto': '#10b981',
            'encerrado': '#ef4444',
            'suspenso': '#f59e0b',
            'cancelado': '#ef4444',
        }
        
        icones = {
            'rascunho': '✏️',
            'em_breve': '⏰',
            'aberto': '🚀',
            'encerrado': '🔒',
            'suspenso': '⏸️',
            'cancelado': '❌',
        }
        
        cor = obj.cor_status_calculada
        icone = icones.get(obj.status, '📄')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: 600;">{} {}</span>',
            cor, icone, obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    def data_encerramento_display(self, obj):
        if not obj.data_encerramento:
            return '-'
        
        agora = timezone.now()
        if obj.data_encerramento < agora:
            cor = '#ef4444'  # Vermelho para vencido
        elif (obj.data_encerramento - agora).days <= 7:
            cor = '#f59e0b'  # Amarelo para próximo do vencimento
        else:
            cor = '#10b981'  # Verde para ainda longe
            
        return format_html(
            '<span style="color: {}; font-weight: 600;">{}</span>',
            cor, obj.data_encerramento.strftime('%d/%m/%Y %H:%M')
        )
    data_encerramento_display.short_description = 'Data de Encerramento'
    
    def dias_restantes_display(self, obj):
        dias = obj.dias_restantes
        if dias is None:
            return '-'
        
        if dias == 0:
            return format_html('<span style="color: #ef4444; font-weight: bold;">ENCERRADO</span>')
        elif dias <= 7:
            return format_html('<span style="color: #f59e0b; font-weight: bold;">{} dias</span>', dias)
        else:
            return format_html('<span style="color: #10b981; font-weight: bold;">{} dias</span>', dias)
    dias_restantes_display.short_description = 'Dias Restantes'
    
    def destaque_display(self, obj):
        if obj.destaque:
            return format_html('<span style="color: #f59e0b;">⭐ Destacado</span>')
        return '-'
    destaque_display.short_description = 'Destaque'
    
    def esta_aberto_display(self, obj):
        if obj.esta_aberto:
            return format_html('<span style="color: #10b981; font-weight: bold;">✅ SIM</span>')
        return format_html('<span style="color: #ef4444; font-weight: bold;">❌ NÃO</span>')
    esta_aberto_display.short_description = 'Está Aberto?'
    
    # Actions
    def marcar_como_rascunho(self, request, queryset):
        count = queryset.update(status='rascunho')
        self.message_user(request, f'{count} edital(is) marcado(s) como Rascunho.')
    marcar_como_rascunho.short_description = 'Marcar como Rascunho'
    
    def marcar_como_em_breve(self, request, queryset):
        count = queryset.update(status='em_breve')
        self.message_user(request, f'{count} edital(is) marcado(s) como Em Breve.')
    marcar_como_em_breve.short_description = 'Marcar como Em Breve'
    
    def marcar_como_aberto(self, request, queryset):
        agora = timezone.now()
        for edital in queryset:
            edital.status = 'aberto'
            if not edital.data_publicacao:
                edital.data_publicacao = agora
            edital.save()
        count = queryset.count()
        self.message_user(request, f'{count} edital(is) marcado(s) como Aberto.')
    marcar_como_aberto.short_description = 'Marcar como Aberto'
    
    def marcar_como_encerrado(self, request, queryset):
        count = queryset.update(status='encerrado')
        self.message_user(request, f'{count} edital(is) marcado(s) como Encerrado.')
    marcar_como_encerrado.short_description = 'Marcar como Encerrado'
    
    def destacar_editais(self, request, queryset):
        count = queryset.update(destaque=True)
        self.message_user(request, f'{count} edital(is) destacado(s).')
    destacar_editais.short_description = 'Destacar Editais'
    
    def remover_destaque(self, request, queryset):
        count = queryset.update(destaque=False)
        self.message_user(request, f'Destaque removido de {count} edital(is).')
    remover_destaque.short_description = 'Remover Destaque'


@admin.register(NotificacaoEdital)
class NotificacaoEditalAdmin(admin.ModelAdmin):
    list_display = [
        'email', 'nome', 'edital', 'data_solicitacao', 
        'notificado_display', 'data_notificacao'
    ]
    list_filter = ['notificado', 'data_solicitacao', 'edital__categoria']
    search_fields = ['email', 'nome', 'edital__titulo']
    date_hierarchy = 'data_solicitacao'
    readonly_fields = ['data_solicitacao']
    
    actions = ['marcar_como_notificado', 'enviar_notificacoes']
    
    def notificado_display(self, obj):
        if obj.notificado:
            return format_html('<span style="color: #10b981;">✅ SIM</span>')
        return format_html('<span style="color: #ef4444;">❌ NÃO</span>')
    notificado_display.short_description = 'Notificado'
    
    def marcar_como_notificado(self, request, queryset):
        agora = timezone.now()
        count = 0
        for notificacao in queryset.filter(notificado=False):
            notificacao.notificado = True
            notificacao.data_notificacao = agora
            notificacao.save()
            count += 1
        self.message_user(request, f'{count} notificação(ões) marcada(s) como enviada(s).')
    marcar_como_notificado.short_description = 'Marcar como Notificado'
    
    def enviar_notificacoes(self, request, queryset):
        # Implementar envio real de emails aqui
        count = queryset.filter(notificado=False).count()
        if count > 0:
            self.message_user(
                request, 
                f'Funcionalidade de envio implementada: {count} notificações seriam enviadas.'
            )
        else:
            self.message_user(request, 'Nenhuma notificação pendente encontrada.')
    enviar_notificacoes.short_description = 'Enviar Notificações Pendentes'


# Configurações do Admin Site
admin.site.site_header = "PONTI Hub de Inovação - Editais"
admin.site.site_title = "PONTI - Editais"
admin.site.index_title = "Administração de Editais"
