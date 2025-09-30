from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from .models import Edital, NotificacaoEdital
from .forms import NotificacaoEditalForm
import json


def obter_ip_usuario(request):
    """Obtém o IP real do usuário"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


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
