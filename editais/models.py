from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.core.validators import FileExtensionValidator
import os


class CategoriaEdital(models.Model):
    """Categorias dos editais (Startups, Aceleração, Fomento, etc.)"""
    
    nome = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nome da Categoria",
        help_text="Ex: STARTUPS, ACELERAÇÃO, FOMENTO"
    )
    
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name="Slug",
        help_text="Identificador único para URLs"
    )
    
    cor = models.CharField(
        max_length=7,
        default="#3b82f6",
        verbose_name="Cor",
        help_text="Código hex da cor (#3b82f6)"
    )
    
    icone = models.CharField(
        max_length=50,
        default="fas fa-file-alt",
        verbose_name="Ícone",
        help_text="Classe do FontAwesome (fas fa-rocket)"
    )
    
    descricao = models.TextField(
        blank=True,
        verbose_name="Descrição",
        help_text="Descrição da categoria"
    )
    
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    
    class Meta:
        verbose_name = "Categoria de Edital"
        verbose_name_plural = "Categorias de Editais"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class AreaInteresse(models.Model):
    """Áreas de interesse dos editais"""
    
    nome = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nome da Área",
        help_text="Ex: Saúde Digital, Educação Tech"
    )
    
    cor = models.CharField(
        max_length=7,
        default="#3b82f6",
        verbose_name="Cor",
        help_text="Código hex da cor para o badge"
    )
    
    icone = models.CharField(
        max_length=50,
        default="fas fa-circle",
        verbose_name="Ícone",
        help_text="Classe do FontAwesome"
    )
    
    descricao = models.TextField(
        blank=True,
        verbose_name="Descrição"
    )
    
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    
    class Meta:
        verbose_name = "Área de Interesse"
        verbose_name_plural = "Áreas de Interesse"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


def edital_upload_path(instance, filename):
    """Função para definir o caminho de upload dos arquivos do edital"""
    return f'editais/{instance.numero_edital}/{filename}'


class Edital(models.Model):
    """Model principal para editais"""
    
    STATUS_CHOICES = [
        ('rascunho', 'Rascunho'),
        ('em_breve', 'Em Breve'),
        ('aberto', 'Aberto'),
        ('encerrado', 'Encerrado'),
        ('suspenso', 'Suspenso'),
        ('cancelado', 'Cancelado'),
    ]
    
    MODALIDADE_CHOICES = [
        ('fomento', 'Fomento'),
        ('aceleracao', 'Aceleração'),
        ('premio', 'Prêmio'),
        ('chamada_publica', 'Chamada Pública'),
        ('outro', 'Outro'),
    ]
    
    # Informações básicas
    titulo = models.CharField(
        max_length=200,
        verbose_name="Título do Edital",
        help_text="Ex: EDITAL SECTIDE 001/2025"
    )
    
    numero_edital = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Número do Edital",
        help_text="Ex: SECTIDE-001/2025"
    )
    
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name="Slug",
        help_text="Gerado automaticamente a partir do título"
    )
    
    subtitulo = models.CharField(
        max_length=300,
        verbose_name="Subtítulo",
        help_text="Descrição breve do edital"
    )
    
    descricao_completa = models.TextField(
        verbose_name="Descrição Completa",
        help_text="Descrição detalhada do edital"
    )
    
    # Classificação
    categoria = models.ForeignKey(
        CategoriaEdital,
        on_delete=models.CASCADE,
        verbose_name="Categoria"
    )
    
    areas_interesse = models.ManyToManyField(
        AreaInteresse,
        blank=True,
        verbose_name="Áreas de Interesse",
        help_text="Áreas temáticas do edital"
    )
    
    modalidade = models.CharField(
        max_length=20,
        choices=MODALIDADE_CHOICES,
        default='fomento',
        verbose_name="Modalidade"
    )
    
    # Status e datas
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='rascunho',
        verbose_name="Status"
    )
    
    data_publicacao = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Data de Publicação"
    )
    
    data_abertura = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Data de Abertura",
        help_text="Quando as inscrições se iniciam"
    )
    
    data_encerramento = models.DateTimeField(
        verbose_name="Data de Encerramento",
        help_text="Quando as inscrições se encerram"
    )
    
    # Informações específicas
    numero_desafios = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Número de Desafios",
        help_text="Quantidade de desafios ou vagas (se aplicável)"
    )
    
    valor_premio = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Valor do Prêmio",
        help_text="Valor total em R$ (se aplicável)"
    )
    
    # Arquivos
    arquivo_edital = models.FileField(
        upload_to=edital_upload_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['pdf', 'doc', 'docx'])],
        verbose_name="Arquivo do Edital",
        help_text="Arquivo PDF ou DOC do edital completo"
    )
    
    link_inscricao = models.URLField(
        blank=True,
        verbose_name="Link de Inscrição",
        help_text="URL para inscrições (se externo)"
    )
    
    link_mais_informacoes = models.URLField(
        blank=True,
        verbose_name="Link Mais Informações",
        help_text="URL para mais informações"
    )
    
    # Configurações de exibição
    destaque = models.BooleanField(
        default=False,
        verbose_name="Destacar",
        help_text="Destacar este edital na listagem"
    )
    
    cor_status = models.CharField(
        max_length=7,
        blank=True,
        verbose_name="Cor do Status",
        help_text="Cor personalizada para o status (opcional)"
    )
    
    # Metadados
    data_criacao = models.DateTimeField(
        default=timezone.now,
        verbose_name="Data de Criação"
    )
    
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )
    
    criado_por = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Criado por"
    )
    
    visualizacoes = models.PositiveIntegerField(
        default=0,
        verbose_name="Visualizações"
    )
    
    class Meta:
        verbose_name = "Edital"
        verbose_name_plural = "Editais"
        ordering = ['-data_criacao', '-destaque']
    
    def __str__(self):
        return f"{self.titulo} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.titulo)
        
        # Auto-definir data de publicação quando status muda para aberto
        if self.status == 'aberto' and not self.data_publicacao:
            self.data_publicacao = timezone.now()
            
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('editais:detalhe', kwargs={'slug': self.slug})
    
    @property
    def esta_aberto(self):
        """Verifica se o edital está aberto para inscrições"""
        if self.status != 'aberto':
            return False
        
        agora = timezone.now()
        
        # Verifica se está dentro do período
        if self.data_abertura and agora < self.data_abertura:
            return False
            
        if self.data_encerramento and agora > self.data_encerramento:
            return False
            
        return True
    
    @property
    def dias_restantes(self):
        """Calcula quantos dias restam para o encerramento"""
        if not self.data_encerramento:
            return None
            
        agora = timezone.now()
        if agora > self.data_encerramento:
            return 0
            
        delta = self.data_encerramento - agora
        return delta.days
    
    @property
    def cor_status_calculada(self):
        """Retorna a cor do status (personalizada ou padrão)"""
        if self.cor_status:
            return self.cor_status
            
        cores_padrao = {
            'rascunho': '#6b7280',
            'em_breve': '#1e40af',
            'aberto': '#10b981',
            'encerrado': '#ef4444',
            'suspenso': '#f59e0b',
            'cancelado': '#ef4444',
        }
        
        return cores_padrao.get(self.status, '#6b7280')
    
    @property
    def icone_status(self):
        """Retorna o ícone apropriado para o status"""
        icones = {
            'rascunho': 'fas fa-edit',
            'em_breve': 'fas fa-clock',
            'aberto': 'fas fa-door-open',
            'encerrado': 'fas fa-lock',
            'suspenso': 'fas fa-pause',
            'cancelado': 'fas fa-times',
        }
        
        return icones.get(self.status, 'fas fa-file-alt')
    
    def incrementar_visualizacao(self):
        """Incrementa o contador de visualizações"""
        self.visualizacoes += 1
        self.save(update_fields=['visualizacoes'])


class NotificacaoEdital(models.Model):
    """Model para notificações de editais"""
    
    edital = models.ForeignKey(
        Edital,
        on_delete=models.CASCADE,
        verbose_name="Edital"
    )
    
    # Dados pessoais
    cpf = models.CharField(
        max_length=14,
        blank=False,
        null=True,
        verbose_name="CPF",
        help_text="CPF do interessado (xxx.xxx.xxx-xx)"
    )
    
    nome_completo = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Nome Completo"
    )
    
    email = models.EmailField(
        verbose_name="E-mail"
    )
    
    telefone_whatsapp = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Telefone/WhatsApp",
        help_text="Telefone ou WhatsApp (opcional)"
    )
    
    # Metadados
    data_solicitacao = models.DateTimeField(
        default=timezone.now,
        verbose_name="Data da Solicitação"
    )
    
    notificado = models.BooleanField(
        default=False,
        verbose_name="Notificado"
    )
    
    data_notificacao = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Data da Notificação"
    )
    
    # Dados adicionais
    ip_endereco = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name="Endereço IP",
        help_text="IP do usuário que fez a solicitação"
    )
    
    user_agent = models.TextField(
        blank=True,
        verbose_name="User Agent",
        help_text="Informações do navegador"
    )
    
    class Meta:
        verbose_name = "Notificação de Edital"
        verbose_name_plural = "Notificações de Editais"
        unique_together = ['edital', 'cpf']
        ordering = ['-data_solicitacao']
    
    def __str__(self):
        return f"{self.nome_completo} - {self.edital.titulo}"
    
    def clean(self):
        """Validação customizada"""
        from django.core.exceptions import ValidationError
        import re
        
        # Validar CPF (formato básico)
        if self.cpf:
            # Remove caracteres especiais
            cpf_limpo = re.sub(r'[^0-9]', '', self.cpf)
            if len(cpf_limpo) != 11:
                raise ValidationError({'cpf': 'CPF deve ter 11 dígitos.'})
            
            # Formatar CPF
            self.cpf = f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def cpf_mascarado(self):
        """Retorna CPF mascarado para exibição"""
        if self.cpf:
            return f"{self.cpf[:3]}.***.**{self.cpf[-2:]}"
        return ""
    
    def __str__(self):
        return f"{self.email} - {self.edital.titulo}"
