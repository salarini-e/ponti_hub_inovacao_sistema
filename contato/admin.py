from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Contato


@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    list_display = [
        'nome', 'email', 'assunto_display', 'status_display', 
        'data_criacao_display', 'is_novo_display'
    ]
    list_filter = ['status', 'assunto', 'data_criacao']
    search_fields = ['nome', 'email', 'mensagem']
    readonly_fields = ['data_criacao', 'ip_origem', 'user_agent', 'tempo_resposta_display']
    date_hierarchy = 'data_criacao'
    
    fieldsets = (
        ('Informações do Contato', {
            'fields': ('nome', 'email', 'telefone', 'assunto')
        }),
        ('Mensagem', {
            'fields': ('mensagem',)
        }),
        ('Status e Resposta', {
            'fields': ('status', 'resposta', 'data_resposta')
        }),
        ('Informações Técnicas', {
            'fields': ('data_criacao', 'ip_origem', 'user_agent', 'tempo_resposta_display'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['marcar_como_em_andamento', 'marcar_como_respondido', 'marcar_como_fechado']
    
    def assunto_display(self, obj):
        cores = {
            'geral': '#3b82f6',
            'parceria': '#10b981',
            'projeto': '#f59e0b',
            'startup': '#ef4444',
            'tecnologia': '#8b5cf6',
            'outro': '#6b7280'
        }
        cor = cores.get(obj.assunto, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: 600;">{}</span>',
            cor, obj.get_assunto_display()
        )
    assunto_display.short_description = 'Assunto'
    
    def status_display(self, obj):
        cores = {
            'novo': '#ef4444',
            'em_andamento': '#f59e0b',
            'respondido': '#10b981',
            'fechado': '#6b7280'
        }
        icones = {
            'novo': '🆕',
            'em_andamento': '⏳',
            'respondido': '✅',
            'fechado': '📁'
        }
        cor = cores.get(obj.status, '#6b7280')
        icone = icones.get(obj.status, '❓')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: 600;">{} {}</span>',
            cor, icone, obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    def data_criacao_display(self, obj):
        return obj.data_criacao.strftime('%d/%m/%Y %H:%M')
    data_criacao_display.short_description = 'Data/Hora'
    
    def is_novo_display(self, obj):
        if obj.is_novo:
            return format_html('<span style="color: #ef4444; font-weight: bold;">NOVO</span>')
        return '-'
    is_novo_display.short_description = 'Novo?'
    
    def tempo_resposta_display(self, obj):
        tempo = obj.tempo_resposta
        if tempo:
            dias = tempo.days
            horas = tempo.seconds // 3600
            minutos = (tempo.seconds % 3600) // 60
            return f"{dias}d {horas}h {minutos}m"
        return "Não respondido"
    tempo_resposta_display.short_description = 'Tempo de Resposta'
    
    def marcar_como_em_andamento(self, request, queryset):
        count = queryset.update(status='em_andamento')
        self.message_user(request, f'{count} contato(s) marcado(s) como "Em Andamento".')
    marcar_como_em_andamento.short_description = 'Marcar como Em Andamento'
    
    def marcar_como_respondido(self, request, queryset):
        for contato in queryset:
            contato.marcar_como_respondido()
        count = queryset.count()
        self.message_user(request, f'{count} contato(s) marcado(s) como "Respondido".')
    marcar_como_respondido.short_description = 'Marcar como Respondido'
    
    def marcar_como_fechado(self, request, queryset):
        count = queryset.update(status='fechado')
        self.message_user(request, f'{count} contato(s) marcado(s) como "Fechado".')
    marcar_como_fechado.short_description = 'Marcar como Fechado'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()
