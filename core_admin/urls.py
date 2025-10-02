from django.urls import path
from . import views

app_name = 'core_admin'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard, name='dashboard'),
    
    # Gerenciamento de conteúdo
    path('quem-somos/', views.quem_somos, name='quem_somos'),
    path('onde-atuamos/', views.onde_atuamos, name='onde_atuamos'),
    path('configuracoes/', views.configuracoes, name='configuracoes'),
    
    # AJAX endpoints
    path('ajax/card/<int:card_id>/get/', views.get_card, name='get_card'),
    path('ajax/card/<int:card_id>/toggle/', views.toggle_card_status, name='toggle_card_status'),
    path('ajax/area/<int:area_id>/toggle/', views.toggle_area_status, name='toggle_area_status'),
    path('ajax/card/<int:card_id>/delete/', views.delete_card, name='delete_card'),
    path('ajax/area/<int:area_id>/delete/', views.delete_area, name='delete_area'),
]