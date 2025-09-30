from django.urls import path
from . import views

app_name = 'contato'

urlpatterns = [
    path('processar/', views.processar_contato, name='processar'),
    path('listar/', views.listar_contatos, name='listar'),
]