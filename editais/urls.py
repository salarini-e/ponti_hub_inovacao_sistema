from django.urls import path
from . import views

app_name = 'editais'

urlpatterns = [
    # ===== URLS ADMINISTRATIVAS =====
    
    # Dashboard
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    
    # CRUD Editais
    path('admin/editais/', views.admin_listar_editais, name='admin_listar_editais'),
    path('admin/editais/criar/', views.admin_criar_edital, name='admin_criar_edital'),
    path('admin/editais/<int:edital_id>/editar/', views.admin_editar_edital, name='admin_editar_edital'),
    path('admin/editais/<int:edital_id>/visualizar/', views.admin_visualizar_edital, name='admin_visualizar_edital'),
    path('admin/editais/<int:edital_id>/deletar/', views.admin_deletar_edital, name='admin_deletar_edital'),
    
    # AJAX
    path('admin/editais/<int:edital_id>/alterar-status/', views.admin_alterar_status_edital, name='admin_alterar_status_edital'),
    path('admin/editais/<int:edital_id>/toggle-destaque/', views.admin_toggle_destaque_edital, name='admin_toggle_destaque_edital'),
    
    # Anexos
    path('admin/editais/<int:edital_id>/anexos/', views.admin_anexos_edital, name='admin_anexos_edital'),
    path('admin/editais/<int:edital_id>/anexos/criar/', views.admin_criar_anexo, name='admin_criar_anexo'),
    path('admin/anexos/<int:anexo_id>/editar/', views.admin_editar_anexo, name='admin_editar_anexo'),
    path('admin/anexos/<int:anexo_id>/deletar/', views.admin_deletar_anexo, name='admin_deletar_anexo'),
    path('admin/anexos/<int:anexo_id>/toggle-ativo/', views.admin_toggle_anexo_ativo, name='admin_toggle_anexo_ativo'),
    
    # ===== URLS ORIGINAIS (Sistema de Notificações) =====
    
    # URLs para views que serão criadas futuramente
    # path('', views.lista_editais, name='lista'),
    # path('<slug:slug>/', views.detalhe_edital, name='detalhe'),
    
    # URLs para sistema de notificações
    path('notificar/<slug:edital_slug>/', views.solicitar_notificacao, name='solicitar_notificacao'),
    path('notificar-ajax/', views.solicitar_notificacao_ajax, name='solicitar_notificacao_ajax'),
    path('admin/notificacoes/<slug:edital_slug>/', views.listar_notificacoes_edital, name='listar_notificacoes'),
]