from django.urls import path
from . import views

app_name = 'editais'

urlpatterns = [
    # URLs para views que serão criadas futuramente
    # path('', views.lista_editais, name='lista'),
    # path('<slug:slug>/', views.detalhe_edital, name='detalhe'),
    
    # URLs para sistema de notificações
    path('notificar/<slug:edital_slug>/', views.solicitar_notificacao, name='solicitar_notificacao'),
    path('notificar-ajax/', views.solicitar_notificacao_ajax, name='solicitar_notificacao_ajax'),
    path('admin/notificacoes/<slug:edital_slug>/', views.listar_notificacoes_edital, name='listar_notificacoes'),
]