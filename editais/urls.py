from django.urls import path
from . import views

app_name = 'editais'

urlpatterns = [
    path('', views.lista_editais, name='lista'),
    path('<slug:slug>/', views.detalhe_edital, name='detalhe'),
    path('<slug:slug>/notificar/', views.solicitar_notificacao, name='notificar'),
]