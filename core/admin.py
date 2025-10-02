from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path
from .models import SessaoQuemSomos, CardQuemSomos, SessaoOndeAtuamos, AreaAtuacao, Configuracoes

# Register your models here.

@admin.register(SessaoQuemSomos)
class SessaoQuemSomosAdmin(admin.ModelAdmin):
    """
    Configuração do admin para Sessão Quem Somos (Singleton)
    """
    list_display = ('nome_sessao', 'titulo_principal', 'ativo', 'atualizado_em')
    list_filter = ('ativo', 'criado_em', 'atualizado_em')
    search_fields = ('nome_sessao', 'titulo_principal', 'titulo_azul')
    
    fieldsets = (
        ('Identificação da Sessão', {
            'fields': ('nome_sessao', 'ativo')
        }),
        ('Títulos', {
            'fields': ('titulo_principal', 'titulo_azul')
        }),
        ('Conteúdo', {
            'fields': ('paragrafo_1', 'paragrafo_2')
        }),
        ('Mídia', {
            'fields': ('imagem',)
        }),
        ('Metadados', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ('criado_em', 'atualizado_em')
    
    # Configurações para Singleton
    def has_add_permission(self, request):
        """Impede adicionar novos registros se já existe um"""
        return not SessaoQuemSomos.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Impede exclusão do registro"""
        return False
    
    def get_urls(self):
        """Override das URLs para redirecionar para edição do registro único"""
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_site.admin_view(self.changelist_redirect), name='core_sessaoquemsomos_changelist'),
        ]
        return custom_urls + urls
    
    def changelist_redirect(self, request):
        """Redireciona diretamente para edição do registro único"""
        instance = SessaoQuemSomos.get_instancia()
        return HttpResponseRedirect(f'{instance.pk}/change/')
    
    # Configurações para melhor UX
    save_on_top = True
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }


@admin.register(CardQuemSomos)
class CardQuemSomosAdmin(admin.ModelAdmin):
    """
    Configuração do admin para Cards Quem Somos
    """
    list_display = ('ordem', 'titulo', 'ativo', 'atualizado_em')
    list_filter = ('ativo', 'criado_em', 'atualizado_em')
    search_fields = ('titulo', 'corpo')
    list_editable = ('ativo',)
    ordering = ('ordem',)
    
    fieldsets = (
        ('Conteúdo do Card', {
            'fields': ('titulo', 'corpo')
        }),
        ('Configurações', {
            'fields': ('ordem', 'ativo')
        }),
        ('Metadados', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ('criado_em', 'atualizado_em')
    
    # Configurações para melhor UX
    save_on_top = True
    list_per_page = 20
    
    def get_queryset(self, request):
        """Override para garantir que os cards iniciais existam"""
        qs = super().get_queryset(request)
        if not qs.exists():
            CardQuemSomos.criar_cards_iniciais()
            qs = super().get_queryset(request)
        return qs
    
    actions = ['ativar_cards', 'desativar_cards']
    
    @admin.action(description='Ativar cards selecionados')
    def ativar_cards(self, request, queryset):
        updated = queryset.update(ativo=True)
        self.message_user(request, f'{updated} card(s) ativado(s) com sucesso.')
    
    @admin.action(description='Desativar cards selecionados')
    def desativar_cards(self, request, queryset):
        updated = queryset.update(ativo=False)
        self.message_user(request, f'{updated} card(s) desativado(s) com sucesso.')


@admin.register(SessaoOndeAtuamos)
class SessaoOndeAtuamosAdmin(admin.ModelAdmin):
    """
    Configuração do admin para Sessão Onde Atuamos (Singleton)
    """
    list_display = ('nome_sessao', 'titulo_principal', 'ativo', 'atualizado_em')
    list_filter = ('ativo', 'criado_em', 'atualizado_em')
    search_fields = ('nome_sessao', 'titulo_principal', 'titulo_badge')
    
    fieldsets = (
        ('Identificação da Sessão', {
            'fields': ('nome_sessao', 'ativo')
        }),
        ('Badge/Cabeçalho', {
            'fields': ('emoji_badge', 'titulo_badge', 'subtitulo')
        }),
        ('Conteúdo Principal', {
            'fields': ('titulo_principal', 'descricao_principal')
        }),
        ('Mídia', {
            'fields': ('imagem_principal', 'url_imagem_principal'),
            'description': 'Use o upload de imagem OU a URL, não ambos.'
        }),
        ('Metadados', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ('criado_em', 'atualizado_em')
    
    # Configurações para Singleton
    def has_add_permission(self, request):
        """Impede adicionar novos registros se já existe um"""
        return not SessaoOndeAtuamos.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Impede exclusão do registro"""
        return False
    
    def get_urls(self):
        """Override das URLs para redirecionar para edição do registro único"""
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_site.admin_view(self.changelist_redirect), name='core_sessaoondeatuamos_changelist'),
        ]
        return custom_urls + urls
    
    def changelist_redirect(self, request):
        """Redireciona diretamente para edição do registro único"""
        instance = SessaoOndeAtuamos.get_instancia()
        return HttpResponseRedirect(f'{instance.pk}/change/')
    
    # Configurações para melhor UX
    save_on_top = True
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }


@admin.register(AreaAtuacao)
class AreaAtuacaoAdmin(admin.ModelAdmin):
    """
    Configuração do admin para Áreas de Atuação
    """
    list_display = ('ordem', 'titulo', 'ativo', 'atualizado_em')
    list_filter = ('ativo', 'criado_em', 'atualizado_em')
    search_fields = ('titulo', 'corpo', 'badges')
    list_editable = ('ativo',)
    ordering = ('ordem',)
    
    fieldsets = (
        ('Conteúdo da Área', {
            'fields': ('titulo', 'corpo', 'badges')
        }),
        ('Configurações', {
            'fields': ('ordem', 'ativo')
        }),
        ('Metadados', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ('criado_em', 'atualizado_em')
    
    # Configurações para melhor UX
    save_on_top = True
    list_per_page = 20
    
    def get_queryset(self, request):
        """Override para garantir que as áreas iniciais existam"""
        qs = super().get_queryset(request)
        if not qs.exists():
            AreaAtuacao.criar_areas_iniciais()
            qs = super().get_queryset(request)
        return qs
    
    actions = ['ativar_areas', 'desativar_areas']
    
    @admin.action(description='Ativar áreas selecionadas')
    def ativar_areas(self, request, queryset):
        updated = queryset.update(ativo=True)
        self.message_user(request, f'{updated} área(s) ativada(s) com sucesso.')
    
    @admin.action(description='Desativar áreas selecionadas')
    def desativar_areas(self, request, queryset):
        updated = queryset.update(ativo=False)
        self.message_user(request, f'{updated} área(s) desativada(s) com sucesso.')


@admin.register(Configuracoes)
class ConfiguracoesAdmin(admin.ModelAdmin):
    """
    Configuração do admin para Configurações do Site (Singleton)
    """
    list_display = ('__str__', 'ativo', 'atualizado_em')
    list_filter = ('ativo', 'criado_em', 'atualizado_em')
    
    fieldsets = (
        ('Estado', {
            'fields': ('ativo',)
        }),
        ('Logos', {
            'fields': ('logo_header', 'logo_geral', 'logo_hero'),
            'description': 'Logos utilizadas em diferentes seções do site'
        }),
        ('Informações de Contato', {
            'fields': ('endereco', 'telefone', 'horario_funcionamento'),
            'description': 'Use &lt;br&gt; para quebras de linha'
        }),
        ('Redes Sociais', {
            'fields': ('instagram', 'facebook', 'whatsapp'),
            'description': 'Links das redes sociais (WhatsApp apenas o número com código do país)'
        }),
        ('Textos', {
            'fields': ('texto_rodape',)
        }),
        ('Metadados', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ('criado_em', 'atualizado_em')
    
    # Configurações para Singleton
    def has_add_permission(self, request):
        """Impede adicionar novos registros se já existe um"""
        return not Configuracoes.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Impede exclusão do registro"""
        return False
    
    def get_urls(self):
        """Override das URLs para redirecionar para edição do registro único"""
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_site.admin_view(self.changelist_redirect), name='core_configuracoes_changelist'),
        ]
        return custom_urls + urls
    
    def changelist_redirect(self, request):
        """Redireciona diretamente para edição do registro único"""
        instance = Configuracoes.get_instancia()
        return HttpResponseRedirect(f'{instance.pk}/change/')
    
    # Configurações para melhor UX
    save_on_top = True
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
