from django.db import models
from django.utils import timezone


class Contato(models.Model):
    ASSUNTO_CHOICES = [
        ('geral', 'Informações Gerais'),
        ('parceria', 'Parceria'),
        ('projeto', 'Proposta de Projeto'),
        ('startup', 'Startup/Empreendedorismo'),
        ('tecnologia', 'Tecnologia e Inovação'),
        ('outro', 'Outro'),
    ]
    
    STATUS_CHOICES = [
        ('novo', 'Novo'),
        ('em_andamento', 'Em Andamento'),
        ('respondido', 'Respondido'),
        ('fechado', 'Fechado'),
    ]
    
    nome = models.CharField(
        max_length=100,
        verbose_name="Nome Completo",
        help_text="Nome completo da pessoa que está entrando em contato"
    )
    
    email = models.EmailField(
        verbose_name="E-mail de Contato",
        help_text="E-mail válido para resposta"
    )
    
    telefone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Telefone",
        help_text="Telefone para contato (opcional)"
    )
    
    assunto = models.CharField(
        max_length=20,
        choices=ASSUNTO_CHOICES,
        default='geral',
        verbose_name="Assunto",
        help_text="Categoria do contato"
    )
    
    mensagem = models.TextField(
        verbose_name="Mensagem",
        help_text="Mensagem detalhada"
    )
    
    data_criacao = models.DateTimeField(
        default=timezone.now,
        verbose_name="Data de Criação"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='novo',
        verbose_name="Status"
    )
    
    data_resposta = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Data da Resposta"
    )
    
    resposta = models.TextField(
        blank=True,
        null=True,
        verbose_name="Resposta",
        help_text="Resposta enviada ao contato"
    )
    
    ip_origem = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name="IP de Origem",
        help_text="IP do usuário que enviou o contato"
    )
    
    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name="User Agent",
        help_text="Informações do navegador"
    )
    
    class Meta:
        verbose_name = "Contato"
        verbose_name_plural = "Contatos"
        ordering = ['-data_criacao']
        
    def __str__(self):
        return f"{self.nome} - {self.get_assunto_display()} ({self.data_criacao.strftime('%d/%m/%Y %H:%M')})"
    
    def save(self, *args, **kwargs):
        if self.status == 'respondido' and not self.data_resposta:
            self.data_resposta = timezone.now()
        super().save(*args, **kwargs)
    
    @property
    def is_novo(self):
        return self.status == 'novo'
    
    @property
    def tempo_resposta(self):
        if self.data_resposta and self.data_criacao:
            return self.data_resposta - self.data_criacao
        return None
    
    def marcar_como_respondido(self, resposta_texto=None):
        """Marca o contato como respondido"""
        self.status = 'respondido'
        self.data_resposta = timezone.now()
        if resposta_texto:
            self.resposta = resposta_texto
        self.save()
