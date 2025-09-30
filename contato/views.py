from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
import json
import logging

from .models import Contato

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Obtém o IP real do cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@csrf_exempt
@require_http_methods(["POST"])
def processar_contato(request):
    """
    View para processar o formulário de contato via AJAX
    """
    try:
        # Verifica se é uma requisição AJAX
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Se não for AJAX, processa como formulário normal
            return processar_contato_form(request)
        
        # Parse dos dados JSON
        data = json.loads(request.body)
        
        # Validação básica
        required_fields = ['name', 'email', 'message']
        for field in required_fields:
            if not data.get(field, '').strip():
                return JsonResponse({
                    'success': False,
                    'error': f'Campo {field} é obrigatório.',
                    'field': field
                }, status=400)
        
        # Validação de email simples
        email = data.get('email', '').strip()
        if '@' not in email or '.' not in email:
            return JsonResponse({
                'success': False,
                'error': 'E-mail inválido.',
                'field': 'email'
            }, status=400)
        
        # Criar objeto Contato
        contato = Contato.objects.create(
            nome=data.get('name', '').strip(),
            email=email,
            telefone=data.get('phone', '').strip() or None,
            assunto=data.get('subject', 'geral'),
            mensagem=data.get('message', '').strip(),
            ip_origem=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Enviar email de notificação (opcional)
        try:
            enviar_notificacao_email(contato)
        except Exception as e:
            logger.error(f"Erro ao enviar email de notificação: {e}")
        
        # Log do contato recebido
        logger.info(f"Novo contato recebido: {contato.nome} ({contato.email})")
        
        return JsonResponse({
            'success': True,
            'message': 'Mensagem enviada com sucesso! Entraremos em contato em breve.',
            'contato_id': contato.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Dados inválidos.'
        }, status=400)
        
    except Exception as e:
        logger.error(f"Erro ao processar contato: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Erro interno do servidor. Tente novamente.'
        }, status=500)


def processar_contato_form(request):
    """
    View para processar formulário de contato tradicional (fallback)
    """
    if request.method == 'POST':
        try:
            # Validação básica
            nome = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()
            mensagem = request.POST.get('message', '').strip()
            
            if not all([nome, email, mensagem]):
                messages.error(request, 'Todos os campos obrigatórios devem ser preenchidos.')
                return redirect('core:index')
            
            # Criar contato
            contato = Contato.objects.create(
                nome=nome,
                email=email,
                telefone=request.POST.get('phone', '').strip() or None,
                assunto=request.POST.get('subject', 'geral'),
                mensagem=mensagem,
                ip_origem=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            # Enviar email de notificação
            try:
                enviar_notificacao_email(contato)
            except Exception as e:
                logger.error(f"Erro ao enviar email: {e}")
            
            messages.success(request, 'Mensagem enviada com sucesso! Entraremos em contato em breve.')
            return redirect('core:index')
            
        except Exception as e:
            logger.error(f"Erro ao processar formulário: {e}")
            messages.error(request, 'Erro ao enviar mensagem. Tente novamente.')
            return redirect('core:index')
    
    return redirect('core:index')


def enviar_notificacao_email(contato):
    """
    Envia email de notificação para a equipe quando um novo contato é recebido
    """
    if not getattr(settings, 'EMAIL_HOST', None):
        return
    
    # Email para a equipe
    assunto_admin = f"[PONTI] Novo Contato: {contato.get_assunto_display()}"
    
    contexto = {
        'contato': contato,
        'data_formatada': contato.data_criacao.strftime('%d/%m/%Y às %H:%M'),
    }
    
    # Renderizar template do email
    try:
        mensagem_admin = render_to_string('contato/email_notificacao.html', contexto)
        
        send_mail(
            subject=assunto_admin,
            message=f"Novo contato recebido de {contato.nome} ({contato.email})\n\n{contato.mensagem}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_EMAIL if hasattr(settings, 'CONTACT_EMAIL') else 'contato@pontistartups.tec.br'],
            html_message=mensagem_admin,
            fail_silently=False,
        )
        
    except Exception as e:
        logger.error(f"Erro ao renderizar/enviar email: {e}")
        # Enviar email simples como fallback
        send_mail(
            subject=assunto_admin,
            message=f"Novo contato recebido:\n\nNome: {contato.nome}\nEmail: {contato.email}\nTelefone: {contato.telefone}\nAssunto: {contato.get_assunto_display()}\nMensagem:\n{contato.mensagem}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['contato@pontistartups.tec.br'],
            fail_silently=False,
        )


def listar_contatos(request):
    """
    View para listar contatos (para uso administrativo)
    """
    if not request.user.is_staff:
        messages.error(request, 'Acesso negado.')
        return redirect('core:index')
    
    contatos = Contato.objects.all().order_by('-data_criacao')
    
    context = {
        'contatos': contatos,
        'total_contatos': contatos.count(),
        'novos': contatos.filter(status='novo').count(),
        'em_andamento': contatos.filter(status='em_andamento').count(),
    }
    
    return render(request, 'contato/listar.html', context)
