from django.db import models
from django.core.validators import URLValidator, RegexValidator
from django.utils.text import slugify


class Cargo(models.Model):
    """Model para cargos/posições na equipe"""
    nome = models.CharField(
        max_length=100,
        verbose_name="Nome do Cargo",
        help_text="Ex: Especialista em Inovação e Tecnologia"
    )
    descricao = models.TextField(
        blank=True,
        verbose_name="Descrição do Cargo",
        help_text="Descrição detalhada das responsabilidades do cargo"
    )
    nivel_hierarquico = models.PositiveIntegerField(
        default=1,
        verbose_name="Nível Hierárquico",
        help_text="1 = Mais alto (Prefeito), 2 = Secretário, 3 = Equipe técnica, etc."
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cargo"
        verbose_name_plural = "Cargos"
        ordering = ['nivel_hierarquico', 'nome']

    def __str__(self):
        return self.nome


class AreaEspecialidade(models.Model):
    """Model para áreas de especialidade dos membros"""
    nome = models.CharField(
        max_length=80,
        verbose_name="Área de Especialidade"
    )
    icone = models.CharField(
        max_length=50,
        verbose_name="Ícone FontAwesome",
        help_text="Ex: fas fa-lightbulb",
        blank=True
    )
    cor = models.CharField(
        max_length=7,
        verbose_name="Cor (Hex)",
        help_text="Ex: #fbbf24",
        default="#3b82f6",
        validators=[RegexValidator(regex=r'^#[0-9A-Fa-f]{6}$', message='Use formato hexadecimal (#000000)')]
    )
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Área de Especialidade"
        verbose_name_plural = "Áreas de Especialidade"
        ordering = ['nome']

    def __str__(self):
        return self.nome


class MembroEquipe(models.Model):
    """Model para membros da equipe PONTI"""
    TIPO_CHOICES = [
        ('lideranca', 'Liderança'),
        ('equipe', 'Equipe Técnica'),
    ]

    # Informações básicas
    nome_completo = models.CharField(
        max_length=100,
        verbose_name="Nome Completo"
    )
    nome_exibicao = models.CharField(
        max_length=50,
        verbose_name="Nome para Exibição",
        help_text="Nome que aparecerá na interface (Ex: Johnny Maycon)"
    )
    cargo = models.ForeignKey(
        Cargo,
        on_delete=models.CASCADE,
        verbose_name="Cargo"
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='equipe',
        verbose_name="Tipo de Membro"
    )
    
    # Biografia e descrição
    biografia = models.TextField(
        verbose_name="Biografia",
        help_text="Descrição profissional completa do membro"
    )
    
    # Informações visuais
    foto = models.ImageField(
        blank=True,
        upload_to='equipe/fotos/',
        verbose_name="Foto",
        help_text="Imagem do membro (recomendado: 400x400px)"
    )
    foto_url = models.URLField(
        blank=True,
        verbose_name="URL da Foto",
        help_text="Alternativamente, use uma URL para a foto",
        validators=[URLValidator()]
    )
    
    # Especialidades
    areas_especialidade = models.ManyToManyField(
        AreaEspecialidade,
        verbose_name="Áreas de Especialidade",
        blank=True
    )
    
    # Estatísticas/Métricas (opcionais)
    anos_experiencia = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Anos de Experiência"
    )
    projetos_concluidos = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Projetos Concluídos"
    )
    taxa_sucesso = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Taxa de Sucesso (%)",
        help_text="Porcentagem de 0 a 100"
    )
    metrica_personalizada_nome = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Nome da Métrica Personalizada",
        help_text="Ex: 'Startups Mentoradas', 'Sistemas Criados'"
    )
    metrica_personalizada_valor = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Valor da Métrica Personalizada",
        help_text="Ex: '25+', 'R$5M', '100%'"
    )
    
    # Controle de exibição
    ordem_exibicao = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem de Exibição",
        help_text="Ordem em que aparece na lista (menor número = primeiro)"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    destaque = models.BooleanField(
        default=False,
        verbose_name="Destaque",
        help_text="Marque para destacar este membro (aparecerá primeiro)"
    )
    
    # Metadados
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        verbose_name="Slug"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Membro da Equipe"
        verbose_name_plural = "Membros da Equipe"
        ordering = ['destaque', 'ordem_exibicao', 'cargo__nivel_hierarquico', 'nome_exibicao']

    def __str__(self):
        return f"{self.nome_exibicao} - {self.cargo}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome_exibicao)
        super().save(*args, **kwargs)

    def get_foto_url(self):
        """Retorna a URL da foto, priorizando upload local"""
        if self.foto:
            return self.foto.url
        elif self.foto_url:
            return self.foto_url
        return '/static/assets/images/avatar.svg'  # Foto padrão

    def get_estatisticas(self):
        """Retorna lista de estatísticas para exibição"""
        stats = []
        
        if self.anos_experiencia:
            stats.append({
                'valor': f"{self.anos_experiencia}+",
                'label': 'Anos de Experiência',
                'cor': '#fbbf24'
            })
        
        if self.projetos_concluidos:
            stats.append({
                'valor': f"{self.projetos_concluidos}+",
                'label': 'Projetos Concluídos',
                'cor': '#60a5fa'
            })
        
        if self.taxa_sucesso:
            stats.append({
                'valor': f"{self.taxa_sucesso}%",
                'label': 'Taxa de Sucesso',
                'cor': '#34d399'
            })
        
        if self.metrica_personalizada_nome and self.metrica_personalizada_valor:
            stats.append({
                'valor': self.metrica_personalizada_valor,
                'label': self.metrica_personalizada_nome,
                'cor': '#a855f7'
            })
        
        return stats


class LiderancaDestaque(models.Model):
    """Model para configurar quais líderes aparecem na seção de liderança"""
    membro = models.OneToOneField(
        MembroEquipe,
        on_delete=models.CASCADE,
        limit_choices_to={'tipo': 'lideranca'},
        verbose_name="Membro da Liderança"
    )
    titulo_especial = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Título Especial",
        help_text="Título específico para a seção de liderança (ex: 'Prefeito de Nova Friburgo')"
    )
    descricao_lideranca = models.TextField(
        blank=True,
        verbose_name="Descrição para Liderança",
        help_text="Descrição específica para a seção de liderança (diferente da biografia geral)"
    )
    ordem_lideranca = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem na Liderança",
        help_text="Ordem específica para a seção de liderança"
    )
    exibir_na_lideranca = models.BooleanField(
        default=True,
        verbose_name="Exibir na Seção Liderança"
    )
    
    # Estatísticas específicas para liderança
    estatistica_1_nome = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Nome Estatística 1"
    )
    estatistica_1_valor = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Valor Estatística 1"
    )
    estatistica_2_nome = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Nome Estatística 2"
    )
    estatistica_2_valor = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Valor Estatística 2"
    )
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Liderança em Destaque"
        verbose_name_plural = "Liderança em Destaque"
        ordering = ['ordem_lideranca']

    def __str__(self):
        return f"Liderança: {self.membro.nome_exibicao}"

    def get_titulo(self):
        """Retorna o título para exibição na liderança"""
        return self.titulo_especial or str(self.membro.cargo)

    def get_descricao(self):
        """Retorna a descrição para a seção de liderança"""
        return self.descricao_lideranca or self.membro.biografia

    def get_estatisticas_lideranca(self):
        """Retorna estatísticas específicas da liderança"""
        stats = []
        
        if self.estatistica_1_nome and self.estatistica_1_valor:
            stats.append({
                'nome': self.estatistica_1_nome,
                'valor': self.estatistica_1_valor
            })
        
        if self.estatistica_2_nome and self.estatistica_2_valor:
            stats.append({
                'nome': self.estatistica_2_nome,
                'valor': self.estatistica_2_valor
            })
        
        return stats
