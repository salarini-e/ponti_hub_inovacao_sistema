from django.urls import path
from . import views

app_name = 'projetos'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Portfólios
    path('portfolios/', views.listar_portfolios, name='listar_portfolios'),
    path('portfolios/criar/', views.criar_portfolio, name='criar_portfolio'),
    path('portfolios/<uuid:uuid>/', views.detalhar_portfolio, name='detalhar_portfolio'),
    path('portfolios/<uuid:uuid>/editar/', views.editar_portfolio, name='editar_portfolio'),
    path('portfolios/<uuid:uuid>/excluir/', views.excluir_portfolio, name='excluir_portfolio'),
    
    # Programas
    path('programas/', views.listar_programas, name='listar_programas'),
    path('programas/criar/', views.criar_programa, name='criar_programa'),
    path('programas/<uuid:uuid>/', views.detalhar_programa, name='detalhar_programa'),
    path('programas/<uuid:uuid>/editar/', views.editar_programa, name='editar_programa'),
    path('programas/<uuid:uuid>/excluir/', views.excluir_programa, name='excluir_programa'),
    
    # Projetos
    path('projetos/', views.listar_projetos, name='listar_projetos'),
    path('projetos/<uuid:uuid>/', views.detalhar_projeto, name='detalhar_projeto'),
    
    # Relatórios
    path('relatorios/', views.relatorios, name='relatorios'),
    path('relatorios/portfolio/<uuid:uuid>/', views.relatorio_portfolio, name='relatorio_portfolio'),
    path('relatorios/programa/<uuid:uuid>/', views.relatorio_programa, name='relatorio_programa'),
    path('relatorios/projeto/<uuid:uuid>/', views.relatorio_projeto, name='relatorio_projeto'),
    
    # APIs para dashboard
    path('api/estatisticas/', views.api_estatisticas, name='api_estatisticas'),
    path('api/graficos/', views.api_graficos, name='api_graficos'),
]