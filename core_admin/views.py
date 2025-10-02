from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from core.models import (
    SessaoQuemSomos, CardQuemSomos, 
    SessaoOndeAtuamos, AreaAtuacao, 
    Configuracoes
)

# Decorator para verificar se o usuário é staff
def staff_required(user):
    return user.is_staff

@login_required
@user_passes_test(staff_required)
def dashboard(request):
    """Dashboard principal do painel administrativo"""
    
    # Estatísticas básicas
    stats = {
        'total_cards_quem_somos': CardQuemSomos.objects.count(),
        'total_areas_atuacao': AreaAtuacao.objects.count(),
        'quem_somos_ativo': SessaoQuemSomos.objects.filter(ativo=True).exists(),
        'onde_atuamos_ativo': SessaoOndeAtuamos.objects.filter(ativo=True).exists(),
    }
    
    # Cards recentes
    recent_cards = CardQuemSomos.objects.filter(ativo=True).order_by('-id')[:5]
    recent_areas = AreaAtuacao.objects.filter(ativo=True).order_by('-id')[:5]
    
    context = {
        'stats': stats,
        'recent_cards': recent_cards,
        'recent_areas': recent_areas,
    }
    
    return render(request, 'core_admin/dashboard.html', context)

@login_required
@user_passes_test(staff_required)
def quem_somos(request):
    """Gerenciamento da seção Quem Somos"""
    
    # Obter ou criar a instância única
    sessao, created = SessaoQuemSomos.objects.get_or_create(
        defaults={
            'nome_sessao': 'Quem Somos',
            'titulo_principal': 'Somos um Hub de Inovação da',
            'titulo_azul': 'SECTIDE Nova Friburgo',
            'ativo': True
        }
    )
    
    # Obter todos os cards
    cards = CardQuemSomos.objects.all().order_by('ordem', '-id')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_sessao':
            try:
                sessao.nome_sessao = request.POST.get('nome_sessao', sessao.nome_sessao)
                sessao.titulo_principal = request.POST.get('titulo_principal', sessao.titulo_principal)
                sessao.titulo_azul = request.POST.get('titulo_azul', sessao.titulo_azul)
                sessao.paragrafo_1 = request.POST.get('paragrafo_1', sessao.paragrafo_1)
                sessao.paragrafo_2 = request.POST.get('paragrafo_2', sessao.paragrafo_2)
                sessao.ativo = 'ativo' in request.POST
                
                if 'imagem' in request.FILES:
                    sessao.imagem = request.FILES['imagem']
                
                sessao.full_clean()
                sessao.save()
                messages.success(request, 'Seção "Quem Somos" atualizada com sucesso!')
                
            except ValidationError as e:
                messages.error(request, f'Erro na validação: {e}')
            except Exception as e:
                messages.error(request, f'Erro ao salvar: {e}')
        
        elif action == 'add_card':
            try:
                card = CardQuemSomos(
                    titulo=request.POST.get('titulo'),
                    descricao=request.POST.get('descricao'),
                    cor_primaria=request.POST.get('cor_primaria', '#1e40af'),
                    cor_secundaria=request.POST.get('cor_secundaria', '#3b82f6'),
                    icone=request.POST.get('icone', 'fas fa-star'),
                    ordem=request.POST.get('ordem', 1),
                    ativo='ativo' in request.POST
                )
                
                if 'imagem' in request.FILES:
                    card.imagem = request.FILES['imagem']
                
                card.full_clean()
                card.save()
                messages.success(request, 'Card adicionado com sucesso!')
                
            except ValidationError as e:
                messages.error(request, f'Erro na validação: {e}')
            except Exception as e:
                messages.error(request, f'Erro ao criar card: {e}')
        
        elif action == 'edit_card':
            try:
                card_id = request.POST.get('card_id')
                card = get_object_or_404(CardQuemSomos, id=card_id)
                
                card.titulo = request.POST.get('titulo', card.titulo)
                card.descricao = request.POST.get('descricao', card.descricao)
                card.cor_primaria = request.POST.get('cor_primaria', card.cor_primaria)
                card.cor_secundaria = request.POST.get('cor_secundaria', card.cor_secundaria)
                card.icone = request.POST.get('icone', card.icone)
                card.ordem = request.POST.get('ordem', card.ordem)
                card.ativo = 'ativo' in request.POST
                
                if 'imagem' in request.FILES:
                    card.imagem = request.FILES['imagem']
                
                card.full_clean()
                card.save()
                messages.success(request, 'Card atualizado com sucesso!')
                
            except ValidationError as e:
                messages.error(request, f'Erro na validação: {e}')
            except Exception as e:
                messages.error(request, f'Erro ao atualizar card: {e}')
        
        return redirect('core_admin:quem_somos')
    
    context = {
        'sessao': sessao,
        'cards': cards,
    }
    
    return render(request, 'core_admin/quem_somos.html', context)

@login_required
@user_passes_test(staff_required)
def onde_atuamos(request):
    """Gerenciamento da seção Onde Atuamos"""
    
    # Obter ou criar a instância única
    sessao, created = SessaoOndeAtuamos.objects.get_or_create(
        defaults={
            'nome_sessao': 'Onde Atuamos',
            'titulo_principal': 'Áreas de Atuação',
            'descricao': 'Conheça as principais áreas onde o PONTI Hub de Inovação atua para transformar Nova Friburgo em uma cidade mais inteligente e inovadora.',
            'ativo': True
        }
    )
    
    # Obter todas as áreas
    areas = AreaAtuacao.objects.all().order_by('ordem', '-id')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_sessao':
            try:
                sessao.nome_sessao = request.POST.get('nome_sessao', sessao.nome_sessao)
                sessao.titulo_principal = request.POST.get('titulo_principal', sessao.titulo_principal)
                sessao.descricao = request.POST.get('descricao', sessao.descricao)
                sessao.ativo = 'ativo' in request.POST
                
                sessao.full_clean()
                sessao.save()
                messages.success(request, 'Seção "Onde Atuamos" atualizada com sucesso!')
                
            except ValidationError as e:
                messages.error(request, f'Erro na validação: {e}')
            except Exception as e:
                messages.error(request, f'Erro ao salvar: {e}')
        
        elif action == 'add_area':
            try:
                area = AreaAtuacao(
                    titulo=request.POST.get('titulo'),
                    descricao=request.POST.get('descricao'),
                    badges=request.POST.get('badges', ''),
                    icone=request.POST.get('icone', 'fas fa-star'),
                    ordem=request.POST.get('ordem', 1),
                    ativo='ativo' in request.POST
                )
                
                area.full_clean()
                area.save()
                messages.success(request, 'Área de atuação adicionada com sucesso!')
                
            except ValidationError as e:
                messages.error(request, f'Erro na validação: {e}')
            except Exception as e:
                messages.error(request, f'Erro ao criar área: {e}')
        
        return redirect('core_admin:onde_atuamos')
    
    context = {
        'sessao': sessao,
        'areas': areas,
    }
    
    return render(request, 'core_admin/onde_atuamos.html', context)

@login_required
@user_passes_test(staff_required)
def configuracoes(request):
    """Gerenciamento das configurações do site"""
    
    # Obter ou criar a instância única
    config, created = Configuracoes.objects.get_or_create(defaults={
        'nome_site': 'PONTI - Hub de Inovação',
        'descricao_site': 'Hub de Inovação da Secretaria Municipal de Ciência, Tecnologia, Inovação e Desenvolvimento Econômico de Nova Friburgo',
    })
    
    if request.method == 'POST':
        try:
            # Informações básicas
            config.nome_site = request.POST.get('nome_site', config.nome_site)
            config.descricao_site = request.POST.get('descricao_site', config.descricao_site)
            
            # Logos
            if 'logo_header' in request.FILES:
                config.logo_header = request.FILES['logo_header']
            if 'logo_geral' in request.FILES:
                config.logo_geral = request.FILES['logo_geral']
            if 'logo_hero' in request.FILES:
                config.logo_hero = request.FILES['logo_hero']
            
            # Contato
            config.endereco = request.POST.get('endereco', config.endereco)
            config.telefone = request.POST.get('telefone', config.telefone)
            config.email = request.POST.get('email', config.email)
            config.horario_funcionamento = request.POST.get('horario_funcionamento', config.horario_funcionamento)
            
            # Redes Sociais
            config.facebook = request.POST.get('facebook', config.facebook)
            config.instagram = request.POST.get('instagram', config.instagram)
            config.twitter = request.POST.get('twitter', config.twitter)
            config.linkedin = request.POST.get('linkedin', config.linkedin)
            config.youtube = request.POST.get('youtube', config.youtube)
            config.whatsapp = request.POST.get('whatsapp', config.whatsapp)
            
            config.full_clean()
            config.save()
            messages.success(request, 'Configurações atualizadas com sucesso!')
            
        except ValidationError as e:
            messages.error(request, f'Erro na validação: {e}')
        except Exception as e:
            messages.error(request, f'Erro ao salvar configurações: {e}')
        
        return redirect('core_admin:configuracoes')
    
    context = {
        'config': config,
    }
    
    return render(request, 'core_admin/configuracoes.html', context)

@login_required
@user_passes_test(staff_required)
@require_http_methods(["GET"])
def get_card(request, card_id):
    """Buscar dados de um card específico"""
    try:
        print(f"DEBUG: Buscando card com ID: {card_id}")
        card = get_object_or_404(CardQuemSomos, id=card_id)
        print(f"DEBUG: Card encontrado: {card.titulo}")
        
        data = {
            'success': True,
            'card': {
                'id': card.id,
                'titulo': card.titulo,
                'descricao': card.descricao,
                'cor_primaria': card.cor_primaria,
                'cor_secundaria': card.cor_secundaria,
                'icone': card.icone,
                'ordem': card.ordem,
                'ativo': card.ativo,
                'imagem_url': card.imagem.url if card.imagem else None,
            }
        }
        
        print(f"DEBUG: Retornando dados: {data}")
        return JsonResponse(data)
        
    except Exception as e:
        print(f"DEBUG: Erro ao buscar card: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Erro ao buscar card: {e}'
        })

# Views AJAX para operações rápidas
@login_required
@user_passes_test(staff_required)
@require_http_methods(["POST"])
def toggle_card_status(request, card_id):
    """Toggle status ativo/inativo de um card"""
    try:
        card = get_object_or_404(CardQuemSomos, id=card_id)
        card.ativo = not card.ativo
        card.save()
        
        return JsonResponse({
            'success': True,
            'status': card.ativo,
            'message': f'Card {"ativado" if card.ativo else "desativado"} com sucesso!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao alterar status: {e}'
        })

@login_required
@user_passes_test(staff_required)
@require_http_methods(["POST"])
def toggle_area_status(request, area_id):
    """Toggle status ativo/inativo de uma área"""
    try:
        area = get_object_or_404(AreaAtuacao, id=area_id)
        area.ativo = not area.ativo
        area.save()
        
        return JsonResponse({
            'success': True,
            'status': area.ativo,
            'message': f'Área {"ativada" if area.ativo else "desativada"} com sucesso!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao alterar status: {e}'
        })

@login_required
@user_passes_test(staff_required)
@require_http_methods(["POST"])
def delete_card(request, card_id):
    """Deletar um card"""
    try:
        card = get_object_or_404(CardQuemSomos, id=card_id)
        titulo = card.titulo
        card.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Card "{titulo}" deletado com sucesso!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao deletar card: {e}'
        })

@login_required
@user_passes_test(staff_required)
@require_http_methods(["POST"])
def delete_area(request, area_id):
    """Deletar uma área"""
    try:
        area = get_object_or_404(AreaAtuacao, id=area_id)
        titulo = area.titulo
        area.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Área "{titulo}" deletada com sucesso!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao deletar área: {e}'
        })
