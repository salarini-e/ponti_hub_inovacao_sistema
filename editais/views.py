from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils.text import slugify
from .models import Edital, NotificacaoEdital, CategoriaEdital, AreaInteresse
from .forms import NotificacaoEditalForm
import json


def staff_required(user):
    """Verificar se o usuário é staff"""
    return user.is_staff


def obter_ip_usuario(request):
    """Obtém o IP real do usuário"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# ===== VIEWS ADMINISTRATIVAS - CRUD EDITAIS =====

@login_required
@user_passes_test(staff_required)
def admin_dashboard(request):
    """Dashboard administrativo dos editais"""
    
    # Estatísticas gerais
    total_editais = Edital.objects.count()
    editais_abertos = Edital.objects.filter(status='aberto').count()
    editais_rascunho = Edital.objects.filter(status='rascunho').count()
    total_notificacoes = NotificacaoEdital.objects.count()
    
    # Editais recentes
    editais_recentes = Edital.objects.order_by('-data_criacao')[:5]
    
    # Editais por status
    editais_por_status = Edital.objects.values('status').annotate(
        total=Count('id')
    ).order_by('status')
    
    # Notificações recentes
    notificacoes_recentes = NotificacaoEdital.objects.select_related('edital').order_by('-data_solicitacao')[:10]
    
    context = {
        'total_editais': total_editais,
        'editais_abertos': editais_abertos,
        'editais_rascunho': editais_rascunho,
        'total_notificacoes': total_notificacoes,
        'editais_recentes': editais_recentes,
        'editais_por_status': editais_por_status,
        'notificacoes_recentes': notificacoes_recentes,
    }
    
    return render(request, 'editais/admin/dashboard.html', context)


@login_required
@user_passes_test(staff_required)
def admin_listar_editais(request):
    """Listar todos os editais com filtros"""
    
    editais = Edital.objects.select_related('categoria', 'criado_por').prefetch_related('areas_interesse')
    
    # Filtros
    busca = request.GET.get('busca', '')
    categoria_id = request.GET.get('categoria', '')
    status = request.GET.get('status', '')
    
    if busca:
        editais = editais.filter(
            Q(titulo__icontains=busca) | 
            Q(numero_edital__icontains=busca) |
            Q(subtitulo__icontains=busca)
        )
    
    if categoria_id:
        editais = editais.filter(categoria_id=categoria_id)
    
    if status:
        editais = editais.filter(status=status)
    
    # Ordenação
    ordenacao = request.GET.get('ordenacao', '-data_criacao')
    editais = editais.order_by(ordenacao)
    
    # Paginação
    paginator = Paginator(editais, 15)
    page = request.GET.get('page')
    editais = paginator.get_page(page)
    
    # Dados para filtros
    categorias = CategoriaEdital.objects.filter(ativo=True)
    status_choices = Edital.STATUS_CHOICES
    
    context = {
        'editais': editais,
        'categorias': categorias,
        'status_choices': status_choices,
        'filtros': {
            'busca': busca,
            'categoria': categoria_id,
            'status': status,
            'ordenacao': ordenacao,
        }
    }
    
    return render(request, 'editais/admin/listar.html', context)


@login_required
@user_passes_test(staff_required)
def admin_criar_edital(request):
    """Criar novo edital"""
    
    if request.method == 'POST':
        try:
            # Obter dados do formulário
            titulo = request.POST.get('titulo')
            numero_edital = request.POST.get('numero_edital')
            subtitulo = request.POST.get('subtitulo')
            descricao_completa = request.POST.get('descricao_completa')
            categoria_id = request.POST.get('categoria')
            modalidade = request.POST.get('modalidade')
            status = request.POST.get('status')
            data_encerramento = request.POST.get('data_encerramento')
            data_abertura = request.POST.get('data_abertura')
            numero_desafios = request.POST.get('numero_desafios')
            valor_premio = request.POST.get('valor_premio')
            link_inscricao = request.POST.get('link_inscricao')
            link_mais_informacoes = request.POST.get('link_mais_informacoes')
            destaque = 'destaque' in request.POST
            cor_status = request.POST.get('cor_status')
            areas_interesse = request.POST.getlist('areas_interesse')
            
            # Criar slug único
            slug = slugify(titulo)
            original_slug = slug
            counter = 1
            while Edital.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1
            
            # Criar edital
            edital = Edital.objects.create(
                titulo=titulo,
                numero_edital=numero_edital,
                slug=slug,
                subtitulo=subtitulo,
                descricao_completa=descricao_completa,
                categoria_id=categoria_id,
                modalidade=modalidade,
                status=status,
                data_encerramento=data_encerramento if data_encerramento else None,
                data_abertura=data_abertura if data_abertura else None,
                numero_desafios=int(numero_desafios) if numero_desafios else None,
                valor_premio=float(valor_premio) if valor_premio else None,
                link_inscricao=link_inscricao,
                link_mais_informacoes=link_mais_informacoes,
                destaque=destaque,
                cor_status=cor_status if cor_status else '',
                criado_por=request.user,
            )
            
            # Adicionar áreas de interesse
            if areas_interesse:
                edital.areas_interesse.set(areas_interesse)
            
            # Upload de arquivo se fornecido
            if 'arquivo_edital' in request.FILES:
                edital.arquivo_edital = request.FILES['arquivo_edital']
                edital.save()
            
            messages.success(request, f'Edital "{titulo}" criado com sucesso!')
            return redirect('editais:admin_editar_edital', edital_id=edital.id)
            
        except Exception as e:
            messages.error(request, f'Erro ao criar edital: {str(e)}')
    
    # Dados para o formulário
    categorias = CategoriaEdital.objects.filter(ativo=True)
    areas_interesse = AreaInteresse.objects.filter(ativo=True)
    status_choices = Edital.STATUS_CHOICES
    modalidade_choices = Edital.MODALIDADE_CHOICES
    
    context = {
        'categorias': categorias,
        'areas_interesse': areas_interesse,
        'status_choices': status_choices,
        'modalidade_choices': modalidade_choices,
    }
    
    return render(request, 'editais/admin/criar.html', context)


@login_required
@user_passes_test(staff_required)
def admin_editar_edital(request, edital_id):
    """Editar edital existente"""
    
    edital = get_object_or_404(Edital, id=edital_id)
    
    if request.method == 'POST':
        try:
            # Atualizar dados
            edital.titulo = request.POST.get('titulo')
            edital.numero_edital = request.POST.get('numero_edital')
            edital.subtitulo = request.POST.get('subtitulo')
            edital.descricao_completa = request.POST.get('descricao_completa')
            edital.categoria_id = request.POST.get('categoria')
            edital.modalidade = request.POST.get('modalidade')
            edital.status = request.POST.get('status')
            
            # Datas
            data_encerramento = request.POST.get('data_encerramento')
            edital.data_encerramento = data_encerramento if data_encerramento else None
            
            data_abertura = request.POST.get('data_abertura')
            edital.data_abertura = data_abertura if data_abertura else None
            
            # Campos opcionais
            numero_desafios = request.POST.get('numero_desafios')
            edital.numero_desafios = int(numero_desafios) if numero_desafios else None
            
            valor_premio = request.POST.get('valor_premio')
            edital.valor_premio = float(valor_premio) if valor_premio else None
            
            edital.link_inscricao = request.POST.get('link_inscricao')
            edital.link_mais_informacoes = request.POST.get('link_mais_informacoes')
            edital.destaque = 'destaque' in request.POST
            edital.cor_status = request.POST.get('cor_status', '')
            
            # Áreas de interesse
            areas_interesse = request.POST.getlist('areas_interesse')
            edital.areas_interesse.set(areas_interesse)
            
            # Upload de novo arquivo se fornecido
            if 'arquivo_edital' in request.FILES:
                edital.arquivo_edital = request.FILES['arquivo_edital']
            
            edital.save()
            
            messages.success(request, f'Edital "{edital.titulo}" atualizado com sucesso!')
            return redirect('editais:admin_editar_edital', edital_id=edital.id)
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar edital: {str(e)}')
    
    # Dados para o formulário
    categorias = CategoriaEdital.objects.filter(ativo=True)
    areas_interesse = AreaInteresse.objects.filter(ativo=True)
    status_choices = Edital.STATUS_CHOICES
    modalidade_choices = Edital.MODALIDADE_CHOICES
    
    # Notificações relacionadas
    notificacoes = NotificacaoEdital.objects.filter(edital=edital).order_by('-data_solicitacao')[:10]
    
    context = {
        'edital': edital,
        'categorias': categorias,
        'areas_interesse': areas_interesse,
        'status_choices': status_choices,
        'modalidade_choices': modalidade_choices,
        'notificacoes': notificacoes,
        'total_notificacoes': NotificacaoEdital.objects.filter(edital=edital).count(),
    }
    
    return render(request, 'editais/admin/editar.html', context)


@login_required
@user_passes_test(staff_required)
def admin_visualizar_edital(request, edital_id):
    """Visualizar detalhes do edital"""
    
    edital = get_object_or_404(Edital, id=edital_id)
    
    # Estatísticas
    notificacoes = NotificacaoEdital.objects.filter(edital=edital)
    
    context = {
        'edital': edital,
        'notificacoes': notificacoes,
        'total_notificacoes': notificacoes.count(),
        'notificacoes_pendentes': notificacoes.filter(notificado=False).count(),
    }
    
    return render(request, 'editais/admin/visualizar.html', context)


@login_required
@user_passes_test(staff_required)
def admin_deletar_edital(request, edital_id):
    """Deletar edital"""
    
    edital = get_object_or_404(Edital, id=edital_id)
    
    if request.method == 'POST':
        titulo = edital.titulo
        edital.delete()
        messages.success(request, f'Edital "{titulo}" deletado com sucesso!')
        return redirect('editais:admin_listar_editais')
    
    context = {
        'edital': edital,
        'total_notificacoes': NotificacaoEdital.objects.filter(edital=edital).count(),
    }
    
    return render(request, 'editais/admin/deletar.html', context)


# ===== VIEWS AJAX =====

@login_required
@user_passes_test(staff_required)
@require_http_methods(["POST"])
def admin_alterar_status_edital(request, edital_id):
    """Alterar status do edital via AJAX"""
    
    try:
        edital = get_object_or_404(Edital, id=edital_id)
        novo_status = request.POST.get('status')
        
        if novo_status not in dict(Edital.STATUS_CHOICES):
            return JsonResponse({'success': False, 'message': 'Status inválido'})
        
        edital.status = novo_status
        edital.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Status alterado para "{edital.get_status_display()}"',
            'novo_status': novo_status,
            'novo_status_display': edital.get_status_display(),
            'cor_status': edital.cor_status_calculada,
            'icone_status': edital.icone_status,
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
@user_passes_test(staff_required)
@require_http_methods(["POST"])
def admin_toggle_destaque_edital(request, edital_id):
    """Toggle destaque do edital via AJAX"""
    
    try:
        edital = get_object_or_404(Edital, id=edital_id)
        edital.destaque = not edital.destaque
        edital.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Destaque {"ativado" if edital.destaque else "desativado"}',
            'destaque': edital.destaque
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


# ===== VIEWS ORIGINAIS =====


@csrf_protect
@require_http_methods(["GET", "POST"])
def solicitar_notificacao(request, edital_slug):
    """View para solicitar notificação de edital"""
    edital = get_object_or_404(Edital, slug=edital_slug)
    
    # Verificar se o edital permite notificações (só editais em breve ou rascunho)
    if edital.status not in ['em_breve', 'rascunho']:
        messages.error(request, 'Este edital não está disponível para notificações.')
        return redirect('core:index')
    
    if request.method == 'POST':
        form = NotificacaoEditalForm(request.POST)
        
        if form.is_valid():
            try:
                # Verificar se já existe notificação para este CPF e edital
                cpf = form.cleaned_data['cpf']
                
                if NotificacaoEdital.objects.filter(cpf=cpf, edital=edital).exists():
                    messages.warning(request, 'Você já solicitou notificação para este edital com este CPF.')
                    return redirect('core:index')
                
                # Criar nova notificação
                notificacao = form.save(commit=False)
                notificacao.edital = edital
                notificacao.ip_endereco = obter_ip_usuario(request)
                notificacao.user_agent = request.META.get('HTTP_USER_AGENT', '')
                notificacao.save()
                
                messages.success(
                    request, 
                    f'Notificação solicitada com sucesso! Você será avisado por e-mail quando o edital "{edital.titulo}" for lançado.'
                )
                return redirect('core:index')
                
            except Exception as e:
                messages.error(request, 'Erro ao processar sua solicitação. Tente novamente.')
                
        else:
            # Se há erros no formulário, mostrar mensagens de erro
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    
    else:
        form = NotificacaoEditalForm()
    
    context = {
        'edital': edital,
        'form': form,
    }
    
    return render(request, 'editais/solicitar_notificacao.html', context)


@csrf_protect
@require_http_methods(["POST"])
def solicitar_notificacao_ajax(request):
    """View AJAX para solicitar notificação de edital"""
    try:
        data = json.loads(request.body)
        edital_id = data.get('edital_id')
        
        if not edital_id:
            return JsonResponse({
                'success': False,
                'message': 'ID do edital não fornecido.'
            })
        
        edital = get_object_or_404(Edital, id=edital_id)
        
        # Verificar se o edital permite notificações
        if edital.status not in ['em_breve', 'rascunho']:
            return JsonResponse({
                'success': False,
                'message': 'Este edital não está disponível para notificações.'
            })
        
        # Criar formulário com os dados recebidos
        form_data = {
            'cpf': data.get('cpf'),
            'nome_completo': data.get('nome_completo'),
            'email': data.get('email'),
            'telefone_whatsapp': data.get('telefone_whatsapp', ''),
            'aceito_termos': data.get('aceito_termos', False)
        }
        
        form = NotificacaoEditalForm(form_data)
        
        if form.is_valid():
            # Verificar se já existe notificação para este CPF e edital
            cpf = form.cleaned_data['cpf']
            
            if NotificacaoEdital.objects.filter(cpf=cpf, edital=edital).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Você já solicitou notificação para este edital com este CPF.'
                })
            
            # Criar nova notificação
            notificacao = form.save(commit=False)
            notificacao.edital = edital
            notificacao.ip_endereco = obter_ip_usuario(request)
            notificacao.user_agent = request.META.get('HTTP_USER_AGENT', '')
            notificacao.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Notificação solicitada com sucesso! Você será avisado por e-mail quando o edital "{edital.titulo}" for lançado.'
            })
        
        else:
            # Retornar erros do formulário
            errors = []
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    errors.append(f"{form.fields[field].label}: {error}")
            
            return JsonResponse({
                'success': False,
                'message': 'Dados inválidos: ' + '; '.join(errors)
            })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dados JSON inválidos.'
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Erro interno do servidor.'
        })


def listar_notificacoes_edital(request, edital_slug):
    """View para administradores verem as notificações de um edital"""
    if not request.user.is_staff:
        messages.error(request, 'Acesso negado.')
        return redirect('core:index')
    
    edital = get_object_or_404(Edital, slug=edital_slug)
    notificacoes = NotificacaoEdital.objects.filter(edital=edital).order_by('-data_solicitacao')
    
    context = {
        'edital': edital,
        'notificacoes': notificacoes,
        'total_notificacoes': notificacoes.count(),
        'notificacoes_pendentes': notificacoes.filter(notificado=False).count(),
    }
    
    return render(request, 'editais/listar_notificacoes.html', context)
