from django.shortcuts import render
from equipe.models import MembroEquipe, LiderancaDestaque

# Create your views here.

def index(request):
    """View principal do site - página inicial"""
    # Carregar dados da liderança
    lideranca = LiderancaDestaque.objects.filter(
        exibir_na_lideranca=True
    ).select_related('membro', 'membro__cargo').order_by('ordem_lideranca')
    
    # Carregar membros da equipe (excluindo liderança)
    equipe_tecnica = MembroEquipe.objects.filter(
        tipo='equipe',
        ativo=True
    ).select_related('cargo').prefetch_related('areas_especialidade').order_by(
        'destaque', 'ordem_exibicao'
    )
    
    # Carregar todos os membros ativos para a seção de equipe completa
    todos_membros = MembroEquipe.objects.filter(
        ativo=True
    ).select_related('cargo').prefetch_related('areas_especialidade').order_by(
        'destaque', 'ordem_exibicao', 'cargo__nivel_hierarquico'
    )
    
    context = {
        'lideranca': lideranca,
        'equipe_tecnica': equipe_tecnica,
        'todos_membros': todos_membros.order_by('ordem_exibicao', 'nome_exibicao'),
    }
    
    return render(request, 'core/index.html', context)
