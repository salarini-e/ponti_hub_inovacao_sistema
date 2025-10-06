from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from django.views.decorators.http import require_POST
from datetime import date, timedelta
from .models import *
from .forms import PortfolioForm, ProgramaForm

# =============================================================================
# DASHBOARD PRINCIPAL
# =============================================================================

@login_required
def dashboard(request):
    """Dashboard principal do sistema de projetos"""
    # Estatísticas gerais
    total_portfolios = Portfolio.objects.filter(ativo=True).count()
    total_programas = Programa.objects.filter(ativo=True).count()
    total_projetos = Projeto.objects.filter(ativo=True).count()
    
    # Projetos por status
    projetos_por_status = Projeto.objects.filter(ativo=True).values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Orçamento total
    orcamento_total = Portfolio.objects.filter(ativo=True).aggregate(
        total=Sum('orcamento_total')
    )['total'] or 0
    
    # Projetos críticos (atrasados ou com problemas)
    hoje = date.today()
    projetos_criticos = Projeto.objects.filter(
        ativo=True,
        data_fim_prevista__lt=hoje,
        status__in=['em_execucao', 'em_planejamento', 'em_monitoramento']
    ).count()
    
    # Riscos altos
    riscos_altos = RiscoProjeto.objects.filter(
        ativo=True,
        projeto__ativo=True,
        status__in=['identificado', 'em_analise', 'em_tratamento', 'monitorando']
    ).count()
    
    context = {
        'total_portfolios': total_portfolios,
        'total_programas': total_programas,
        'total_projetos': total_projetos,
        'projetos_por_status': projetos_por_status,
        'orcamento_total': orcamento_total,
        'projetos_criticos': projetos_criticos,
        'riscos_altos': riscos_altos,
    }
    
    return render(request, 'projetos/dashboard.html', context)

# =============================================================================
# PORTFÓLIOS
# =============================================================================

@login_required
def listar_portfolios(request):
    """Lista todos os portfólios"""
    portfolios = Portfolio.objects.filter(ativo=True).order_by('-prioridade', 'nome')
    
    context = {
        'portfolios': portfolios,
    }
    
    return render(request, 'projetos/portfolios/listar.html', context)

@login_required
def detalhar_portfolio(request, uuid):
    """Detalha um portfólio específico"""
    portfolio = get_object_or_404(Portfolio, uuid=uuid)
    
    # Programas do portfólio
    programas = portfolio.programas.filter(ativo=True)
    
    # Projetos diretos do portfólio
    projetos_diretos = portfolio.projetos.filter(ativo=True)
    
    # Projetos dos programas
    projetos_programas = Projeto.objects.filter(
        programa__in=programas,
        ativo=True
    )
    
    # Estatísticas
    total_projetos = projetos_diretos.count() + projetos_programas.count()
    orcamento_consumido = (
        projetos_diretos.aggregate(Sum('orcamento_consumido'))['orcamento_consumido__sum'] or 0
    ) + (
        projetos_programas.aggregate(Sum('orcamento_consumido'))['orcamento_consumido__sum'] or 0
    )
    
    context = {
        'portfolio': portfolio,
        'programas': programas,
        'projetos_diretos': projetos_diretos,
        'projetos_programas': projetos_programas,
        'total_projetos': total_projetos,
        'orcamento_consumido': orcamento_consumido,
    }
    
    return render(request, 'projetos/portfolios/detalhar.html', context)

@login_required
def criar_portfolio(request):
    """Cria um novo portfólio"""
    if request.method == 'POST':
        form = PortfolioForm(request.POST)
        if form.is_valid():
            portfolio = form.save(commit=False)
            portfolio.criado_por = request.user
            portfolio.save()
            messages.success(request, f'Portfólio "{portfolio.nome}" criado com sucesso!')
            return redirect('projetos:detalhar_portfolio', uuid=portfolio.uuid)
    else:
        form = PortfolioForm()
    
    context = {
        'form': form,
        'title': 'Criar Novo Portfólio',
        'submit_text': 'Criar Portfólio',
        'cancel_url': 'projetos:listar_portfolios',
    }
    
    return render(request, 'projetos/portfolios/form.html', context)

@login_required
def editar_portfolio(request, uuid):
    """Edita um portfólio existente"""
    portfolio = get_object_or_404(Portfolio, uuid=uuid)
    
    if request.method == 'POST':
        form = PortfolioForm(request.POST, instance=portfolio)
        if form.is_valid():
            portfolio = form.save()
            messages.success(request, f'Portfólio "{portfolio.nome}" atualizado com sucesso!')
            return redirect('projetos:detalhar_portfolio', uuid=portfolio.uuid)
    else:
        form = PortfolioForm(instance=portfolio)
    
    context = {
        'form': form,
        'portfolio': portfolio,
        'title': f'Editar Portfólio - {portfolio.nome}',
        'submit_text': 'Salvar Alterações',
        'cancel_url': 'projetos:detalhar_portfolio',
        'cancel_args': [portfolio.uuid],
    }
    
    return render(request, 'projetos/portfolios/form.html', context)

@login_required
@require_POST
def excluir_portfolio(request, uuid):
    """Exclui um portfólio (soft delete)"""
    portfolio = get_object_or_404(Portfolio, uuid=uuid)
    
    # Verificar se o portfólio tem programas ou projetos ativos
    programas_ativos = portfolio.programas.filter(ativo=True).count()
    projetos_ativos = portfolio.projetos.filter(ativo=True).count()
    
    if programas_ativos > 0 or projetos_ativos > 0:
        messages.error(
            request, 
            f'Não é possível excluir o portfólio "{portfolio.nome}" pois ele possui '
            f'{programas_ativos} programa(s) e {projetos_ativos} projeto(s) ativo(s). '
            'Remova ou desative todos os itens vinculados antes de excluir.'
        )
        return redirect('projetos:detalhar_portfolio', uuid=portfolio.uuid)
    
    # Soft delete
    portfolio.ativo = False
    portfolio.save()
    
    messages.success(request, f'Portfólio "{portfolio.nome}" foi removido com sucesso.')
    return redirect('projetos:listar_portfolios')

# =============================================================================
# PROGRAMAS
# =============================================================================

@login_required
def listar_programas(request):
    """Lista todos os programas"""
    programas = Programa.objects.filter(ativo=True).select_related('portfolio').order_by('-prioridade', 'nome')
    
    context = {
        'programas': programas,
    }
    
    return render(request, 'projetos/programas/listar.html', context)

@login_required
def detalhar_programa(request, uuid):
    """Detalha um programa específico"""
    programa = get_object_or_404(Programa, uuid=uuid)
    
    # Projetos do programa
    projetos = programa.projetos.filter(ativo=True)
    
    # Estatísticas
    orcamento_consumido = projetos.aggregate(
        Sum('orcamento_consumido')
    )['orcamento_consumido__sum'] or 0
    
    context = {
        'programa': programa,
        'projetos': projetos,
        'orcamento_consumido': orcamento_consumido,
    }
    
    return render(request, 'projetos/programas/detalhar.html', context)

# =============================================================================
# PROJETOS
# =============================================================================

@login_required
def listar_projetos(request):
    """Lista todos os projetos"""
    projetos = Projeto.objects.filter(ativo=True).select_related(
        'portfolio', 'programa', 'tipo_projeto', 'gerente_projeto'
    ).order_by('-prioridade', 'nome')
    
    # Filtros
    status_filter = request.GET.get('status')
    if status_filter:
        projetos = projetos.filter(status=status_filter)
    
    portfolio_filter = request.GET.get('portfolio')
    if portfolio_filter:
        projetos = projetos.filter(portfolio__uuid=portfolio_filter)
    
    context = {
        'projetos': projetos,
        'portfolios': Portfolio.objects.filter(ativo=True),
        'status_choices': StatusChoices.choices,
        'status_filter': status_filter,
        'portfolio_filter': portfolio_filter,
    }
    
    return render(request, 'projetos/projetos/listar.html', context)

@login_required
def detalhar_projeto(request, uuid):
    """Detalha um projeto específico"""
    projeto = get_object_or_404(Projeto, uuid=uuid)
    
    # Dados relacionados
    equipe = projeto.equipe.filter(ativo=True)
    fases = projeto.fases.filter(ativo=True).order_by('ordem')
    entregas = projeto.entregas.filter(ativo=True).order_by('data_prevista')
    marcos = projeto.marcos.filter(ativo=True).order_by('data_prevista')
    riscos = projeto.riscos.filter(ativo=True).order_by('-data_identificacao')
    recursos = projeto.recursos.all().order_by('data_necessidade')
    stakeholders = projeto.stakeholders.filter(ativo=True)
    mudancas = projeto.mudancas.filter(ativo=True).order_by('-data_solicitacao')
    anexos = projeto.anexos.filter(ativo=True).order_by('-atualizado_em')
    
    context = {
        'projeto': projeto,
        'equipe': equipe,
        'fases': fases,
        'entregas': entregas,
        'marcos': marcos,
        'riscos': riscos,
        'recursos': recursos,
        'stakeholders': stakeholders,
        'mudancas': mudancas,
        'anexos': anexos,
    }
    
    return render(request, 'projetos/projetos/detalhar.html', context)

# =============================================================================
# RELATÓRIOS
# =============================================================================

@login_required
def relatorios(request):
    """Página principal de relatórios"""
    return render(request, 'projetos/relatorios/index.html')

@login_required
def relatorio_portfolio(request, uuid):
    """Relatório detalhado do portfólio"""
    portfolio = get_object_or_404(Portfolio, uuid=uuid)
    # TODO: Implementar relatório detalhado
    return render(request, 'projetos/relatorios/portfolio.html', {'portfolio': portfolio})

@login_required
def relatorio_programa(request, uuid):
    """Relatório detalhado do programa"""
    programa = get_object_or_404(Programa, uuid=uuid)
    # TODO: Implementar relatório detalhado
    return render(request, 'projetos/relatorios/programa.html', {'programa': programa})

@login_required
def relatorio_projeto(request, uuid):
    """Relatório detalhado do projeto"""
    projeto = get_object_or_404(Projeto, uuid=uuid)
    # TODO: Implementar relatório detalhado
    return render(request, 'projetos/relatorios/projeto.html', {'projeto': projeto})

# =============================================================================
# APIs PARA DASHBOARD
# =============================================================================

@login_required
def api_estatisticas(request):
    """API para estatísticas do dashboard"""
    hoje = date.today()
    
    # Estatísticas gerais
    stats = {
        'portfolios': {
            'total': Portfolio.objects.filter(ativo=True).count(),
            'ativos': Portfolio.objects.filter(ativo=True, status__in=['em_execucao', 'em_planejamento']).count(),
        },
        'programas': {
            'total': Programa.objects.filter(ativo=True).count(),
            'ativos': Programa.objects.filter(ativo=True, status__in=['em_execucao', 'em_planejamento']).count(),
        },
        'projetos': {
            'total': Projeto.objects.filter(ativo=True).count(),
            'em_execucao': Projeto.objects.filter(ativo=True, status='em_execucao').count(),
            'em_planejamento': Projeto.objects.filter(ativo=True, status='em_planejamento').count(),
            'concluidos': Projeto.objects.filter(ativo=True, status='concluido').count(),
            'atrasados': Projeto.objects.filter(
                ativo=True,
                data_fim_prevista__lt=hoje,
                status__in=['em_execucao', 'em_planejamento', 'em_monitoramento']
            ).count(),
        },
        'orcamento': {
            'total': Portfolio.objects.filter(ativo=True).aggregate(
                Sum('orcamento_total')
            )['orcamento_total__sum'] or 0,
            'consumido': Projeto.objects.filter(ativo=True).aggregate(
                Sum('orcamento_consumido')
            )['orcamento_consumido__sum'] or 0,
        },
        'riscos': {
            'total': RiscoProjeto.objects.filter(ativo=True, projeto__ativo=True).count(),
            'altos': RiscoProjeto.objects.filter(
                ativo=True,
                projeto__ativo=True,
                status__in=['identificado', 'em_analise', 'em_tratamento']
            ).count(),
        }
    }
    
    return JsonResponse(stats)

@login_required
def api_graficos(request):
    """API para dados dos gráficos do dashboard"""
    
    # Projetos por status
    projetos_status = list(
        Projeto.objects.filter(ativo=True)
        .values('status')
        .annotate(count=Count('id'))
        .order_by('status')
    )
    
    # Projetos por prioridade
    projetos_prioridade = list(
        Projeto.objects.filter(ativo=True)
        .values('prioridade')
        .annotate(count=Count('id'))
        .order_by('prioridade')
    )
    
    # Orçamento por portfólio
    orcamento_portfolio = list(
        Portfolio.objects.filter(ativo=True)
        .values('nome', 'orcamento_total')
        .order_by('-orcamento_total')[:10]
    )
    
    # Conclusão de projetos ao longo do tempo (últimos 12 meses)
    doze_meses_atras = date.today() - timedelta(days=365)
    conclusao_tempo = list(
        Projeto.objects.filter(
            ativo=True,
            data_fim_real__gte=doze_meses_atras,
            status='concluido'
        )
        .extra({'mes': "strftime('%%Y-%%m', data_fim_real)"})
        .values('mes')
        .annotate(count=Count('id'))
        .order_by('mes')
    )
    
    data = {
        'projetos_status': projetos_status,
        'projetos_prioridade': projetos_prioridade,
        'orcamento_portfolio': orcamento_portfolio,
        'conclusao_tempo': conclusao_tempo,
    }
    
    return JsonResponse(data)


# =============================================================================
# VIEWS CRUD - PROGRAMA
# =============================================================================

@login_required
def criar_programa(request):
    """View para criar um novo programa"""
    if request.method == 'POST':
        form = ProgramaForm(request.POST)
        if form.is_valid():
            programa = form.save(commit=False)
            programa.criado_por = request.user
            programa.save()
            
            messages.success(request, f'Programa "{programa.nome}" criado com sucesso!')
            return redirect('projetos:detalhar_programa', uuid=programa.uuid)
    else:
        form = ProgramaForm()
    
    context = {
        'form': form,
        'title': 'Criar Programa',
        'action': 'criar'
    }
    
    return render(request, 'projetos/programas/form.html', context)


@login_required
def editar_programa(request, uuid):
    """View para editar um programa existente"""
    programa = get_object_or_404(Programa, uuid=uuid, ativo=True)
    
    if request.method == 'POST':
        form = ProgramaForm(request.POST, instance=programa)
        if form.is_valid():
            programa = form.save(commit=False)
            programa.atualizado_por = request.user
            programa.save()
            
            messages.success(request, f'Programa "{programa.nome}" atualizado com sucesso!')
            return redirect('projetos:detalhar_programa', uuid=programa.uuid)
    else:
        form = ProgramaForm(instance=programa)
    
    context = {
        'form': form,
        'programa': programa,
        'title': f'Editar Programa - {programa.nome}',
        'action': 'editar'
    }
    
    return render(request, 'projetos/programas/form.html', context)


@login_required
@require_POST
def excluir_programa(request, uuid):
    """View para excluir (soft delete) um programa"""
    programa = get_object_or_404(Programa, uuid=uuid, ativo=True)
    
    # Verificar se há projetos vinculados
    projetos_vinculados = programa.projetos.filter(ativo=True).count()
    
    if projetos_vinculados > 0:
        messages.error(
            request, 
            f'Não é possível excluir o programa "{programa.nome}" pois existem {projetos_vinculados} projeto(s) vinculado(s). '
            'Exclua ou transfira os projetos antes de excluir o programa.'
        )
    else:
        programa.ativo = False
        programa.atualizado_por = request.user
        programa.save()
        
        messages.success(request, f'Programa "{programa.nome}" excluído com sucesso!')
    
    return redirect('projetos:listar_programas')
