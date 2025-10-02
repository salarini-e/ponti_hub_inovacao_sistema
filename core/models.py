from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.

class SessaoQuemSomos(models.Model):
    """
    Model para gerenciar o conteúdo da Sessão 1 - Quem Somos
    Apenas um registro deve existir (Singleton)
    """
    # Identificação da sessão
    nome_sessao = models.CharField(
        max_length=100,
        default="Quem Somos",
        verbose_name="Nome da Sessão"
    )
    
    # Títulos
    titulo_principal = models.CharField(
        max_length=200,
        default="Somos um Hub de Inovação da",
        verbose_name="Título Principal"
    )
    
    titulo_azul = models.CharField(
        max_length=100,
        default="SECTIDE Nova Friburgo",
        verbose_name="Título em Azul"
    )
    
    # Parágrafos
    paragrafo_1 = models.TextField(
        default="Atuamos no desenvolvimento científico, tecnológico, econômico e na transformação digital de Nova Friburgo. Acreditamos que iniciativas em inovação, startups e empresas de base tecnológica constroem alicerces sólidos rumo à CIDADE INTELIGENTE. Projetos que unem ciência, tecnologia e empreendedorismo são a base para um futuro conectado, sustentável e inclusivo.",
        verbose_name="Primeiro Parágrafo"
    )
    
    paragrafo_2 = models.TextField(
        default="<strong style=\"color: #1e40af;\">PONTI - Hub de Inovação</strong> é a <strong style=\"color: #1e40af;\">BASE DE LANÇAMENTO DE FOGUETES</strong> da Secretária Municipal de Ciência, Tecnologia, Inovação e Desenvolvimento Econômico de Nova Friburgo.",
        verbose_name="Segundo Parágrafo"
    )
    
    # Imagem
    imagem = models.ImageField(
        upload_to='sessoes/quem_somos/',
        blank=True,
        null=True,
        verbose_name="Imagem da Sessão"
    )
    
    # Controles de estado
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )
    
    class Meta:
        verbose_name = "Sessão - Quem Somos"
        verbose_name_plural = "SESSÕES - Quem Somos"
        ordering = ['-criado_em']
    
    def clean(self):
        """Validação para garantir apenas um registro"""
        if not self.pk and SessaoQuemSomos.objects.exists():
            raise ValidationError('Apenas um registro de "Quem Somos" é permitido. Edite o registro existente.')
    
    def save(self, *args, **kwargs):
        """Override do save para garantir apenas um registro"""
        self.clean()
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Impede a exclusão do registro"""
        raise ValidationError('Este registro não pode ser excluído. Apenas editado.')
    
    @classmethod
    def get_instancia(cls):
        """Método para obter ou criar a instância única"""
        instancia, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'nome_sessao': 'Quem Somos',
                'titulo_principal': 'Somos um Hub de Inovação da',
                'titulo_azul': 'SECTIDE Nova Friburgo',
            }
        )
        return instancia
    
    def __str__(self):
        return f"{self.nome_sessao} - {self.titulo_principal}"
    
    def get_imagem_url(self):
        """Retorna URL da imagem ou placeholder"""
        if self.imagem:
            return self.imagem.url
        return None


class CardQuemSomos(models.Model):
    """
    Model para gerenciar os cards da Sessão Quem Somos
    Permite cards dinâmicos com dados iniciais padrão
    """
    # Conteúdo do card
    titulo = models.CharField(
        max_length=100,
        verbose_name="Título do Card"
    )
    
    corpo = models.TextField(
        verbose_name="Conteúdo do Card"
    )
    
    # Ordem e controles
    ordem = models.PositiveIntegerField(
        default=1,
        verbose_name="Ordem de Exibição",
        help_text="Ordem em que o card será exibido (1, 2, 3...)"
    )
    
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )
    
    class Meta:
        verbose_name = "Card - Quem Somos"
        verbose_name_plural = "CARDS - Quem Somos"
        ordering = ['ordem', 'criado_em']
        unique_together = ['ordem']
    
    @classmethod
    def criar_cards_iniciais(cls):
        """Cria os cards iniciais se não existirem"""
        if not cls.objects.exists():
            cards_iniciais = [
                {
                    'titulo': 'Nossa Missão',
                    'corpo': 'Promover o desenvolvimento científico, tecnológico e econômico de Nova Friburgo, transformando processos analógicos em soluções digitais integradas. Desenvolvemos sistematicamente tecnologias, startups e empresas de base tecnológica através da colaboração entre setores público e privado.',
                    'ordem': 1
                },
                {
                    'titulo': 'Nossa Visão',
                    'corpo': 'Consolidar Nova Friburgo como uma cidade inteligente e referência em inovação. A PONTI é a "BASE DE LANÇAMENTO DE FOGUETES" da SECTIDE, formando caminhos sólidos rumo ao futuro tecnológico através de startups e empresas inovadoras.',
                    'ordem': 2
                },
                {
                    'titulo': 'Nossos Objetivos',
                    'corpo': 'Fomentar e desenvolver o empreendedorismo em Nova Friburgo, agregando valor desde a criação de novas empresas até o desenvolvimento das já existentes. Criamos um ambiente promotor de inovação, potencializamos vocações locais, atraímos investimentos e disponibilizamos estrutura de apoio.',
                    'ordem': 3
                }
            ]
            
            for card_data in cards_iniciais:
                cls.objects.create(**card_data)
            
            return True
        return False
    
    @classmethod
    def get_cards_ativos(cls):
        """Retorna todos os cards ativos ordenados"""
        cards = cls.objects.filter(ativo=True).order_by('ordem')
        if not cards.exists():
            cls.criar_cards_iniciais()
            cards = cls.objects.filter(ativo=True).order_by('ordem')
        return cards
    
    def __str__(self):
        return f"{self.ordem}. {self.titulo}"
    
    def save(self, *args, **kwargs):
        """Override do save para validar ordem"""
        if not self.ordem:
            # Se não foi especificada uma ordem, usar a próxima disponível
            ultima_ordem = CardQuemSomos.objects.aggregate(
                max_ordem=models.Max('ordem')
            )['max_ordem']
            self.ordem = (ultima_ordem or 0) + 1
        super().save(*args, **kwargs)


class SessaoOndeAtuamos(models.Model):
    """
    Model para gerenciar o conteúdo da Sessão Onde Atuamos
    Apenas um registro deve existir (Singleton)
    """
    # Identificação da sessão
    nome_sessao = models.CharField(
        max_length=100,
        default="Onde Atuamos",
        verbose_name="Nome da Sessão"
    )
    
    # Emoji e título do badge
    emoji_badge = models.CharField(
        max_length=10,
        default="🎯",
        verbose_name="Emoji do Badge"
    )
    
    titulo_badge = models.CharField(
        max_length=50,
        default="Onde Atuamos",
        verbose_name="Título do Badge"
    )
    
    # Subtítulo descritivo
    subtitulo = models.CharField(
        max_length=200,
        default="Foco na transformação digital com desenvolvimento científico, tecnológico, inovador e econômico",
        verbose_name="Subtítulo"
    )
    
    # Título principal da descrição
    titulo_principal = models.CharField(
        max_length=200,
        default="Formação, Inovação e Oportunidades",
        verbose_name="Título Principal"
    )
    
    # Descrição principal
    descricao_principal = models.TextField(
        default="Nova Friburgo possui grande potencial para o desenvolvimento de negócios que tenham como base a inovação e a tecnologia, destacando-se que o ensino e o aprendizado estão estruturados numa larga capacidade de formação e desenvolvimento profissional existentes nas diversas instituições de ensino público e privado de nível superior instaladas na região e também na oferta de uma robusta rede de educação técnica e profissionalizante que visa preparar profissionais altamente qualificados para as diversas atividades setoriais como: indústria metal mecânica, indústria têxtil, indústria alimentícia, comércio, serviços, educação, saúde, transportes, distribuição, tecnologia, agronegócio e turismo.",
        verbose_name="Descrição Principal"
    )
    
    # Imagem principal
    imagem_principal = models.ImageField(
        upload_to='sessoes/onde_atuamos/',
        blank=True,
        null=True,
        verbose_name="Imagem Principal",
        help_text="Imagem que será exibida na descrição principal"
    )
    
    # URL da imagem como alternativa
    url_imagem_principal = models.URLField(
        blank=True,
        null=True,
        verbose_name="URL da Imagem Principal",
        help_text="URL alternativa para a imagem (se não houver upload)"
    )
    
    # Controles de estado
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )
    
    class Meta:
        verbose_name = "Sessão - Onde Atuamos"
        verbose_name_plural = "SESSÕES - Onde Atuamos"
        ordering = ['-criado_em']
    
    def clean(self):
        """Validação para garantir apenas um registro"""
        if not self.pk and SessaoOndeAtuamos.objects.exists():
            raise ValidationError('Apenas um registro de "Onde Atuamos" é permitido. Edite o registro existente.')
    
    def save(self, *args, **kwargs):
        """Override do save para garantir apenas um registro"""
        self.clean()
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Impede a exclusão do registro"""
        raise ValidationError('Este registro não pode ser excluído. Apenas editado.')
    
    @classmethod
    def get_instancia(cls):
        """Método para obter ou criar a instância única"""
        instancia, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'nome_sessao': 'Onde Atuamos',
                'emoji_badge': '🎯',
                'titulo_badge': 'Onde Atuamos',
                'subtitulo': 'Foco na transformação digital com desenvolvimento científico, tecnológico, inovador e econômico',
                'titulo_principal': 'Formação, Inovação e Oportunidades',
            }
        )
        return instancia
    
    def get_imagem_url(self):
        """Retorna URL da imagem principal"""
        if self.imagem_principal:
            return self.imagem_principal.url
        elif self.url_imagem_principal:
            return self.url_imagem_principal
        return "/static/assets/images/friburgo.jpg"  # Fallback padrão
    
    def __str__(self):
        return f"{self.nome_sessao} - {self.titulo_principal}"


class AreaAtuacao(models.Model):
    """
    Model para gerenciar as áreas de atuação da PONTI
    Cards dinâmicos para a seção Onde Atuamos
    """
    # Conteúdo da área
    titulo = models.CharField(
        max_length=100,
        verbose_name="Título da Área"
    )
    
    icone = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Ícone (Classe CSS)",
        help_text="Classe CSS para o ícone (ex: fa-solid fa-industry). Pode ficar vazio."
    )   
    corpo = models.TextField(
        verbose_name="Corpo/Descrição da Área",
        default="Descrição da área de atuação."
    )
    
    # Badges/Tags
    badges = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Badges",
        help_text="Badges separadas por vírgula (ex: Automação, Inovação). Pode ficar vazio."
    )
    
    # Ordem e controles
    ordem = models.PositiveIntegerField(
        default=1,
        verbose_name="Ordem de Exibição"
    )
    
    ativo = models.BooleanField(
        default=False,  # Por padrão desativado
        verbose_name="Ativo"
    )
    
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )
    
    class Meta:
        verbose_name = "Área de Atuação"
        verbose_name_plural = "ÁREAS DE ATUAÇÃO"
        ordering = ['ordem', 'criado_em']
        unique_together = ['ordem']
    
    @classmethod
    def criar_areas_iniciais(cls):
        """Cria áreas iniciais se não existirem"""
        if not cls.objects.exists():
            areas_iniciais = [
                {
                    'titulo': 'Indústria Metal Mecânica',
                    'corpo': 'Desenvolvimento e inovação no setor metal mecânico com foco em novas tecnologias e processos industriais avançados, promovendo a modernização e competitividade das empresas locais.',
                    'badges': 'Automação, Inovação',
                    'ordem': 1,
                    'ativo': False
                },
                {
                    'titulo': 'Indústria Têxtil',
                    'corpo': 'Transformação digital e inovação na indústria têxtil, promovendo modernização e competitividade no setor através de tecnologias avançadas e processos sustentáveis.',
                    'badges': 'Digitalização, Sustentabilidade',
                    'ordem': 2,
                    'ativo': False
                },
                {
                    'titulo': 'Tecnologia e Inovação',
                    'corpo': 'Desenvolvimento de startups e empresas de base tecnológica nos setores de educação, saúde, transportes, distribuição, agronegócio e turismo, criando um ecossistema inovador.',
                    'badges': 'Startups, Ecossistema',
                    'ordem': 3,
                    'ativo': False
                }
            ]
            
            for area_data in areas_iniciais:
                cls.objects.create(**area_data)
            
            return True
        return False
    
    @classmethod
    def get_areas_ativas(cls):
        """Retorna todas as áreas ativas ordenadas"""
        areas = cls.objects.filter(ativo=True).order_by('ordem')
        # Se não existem registros, cria os iniciais (mas não força a ativação)
        if not cls.objects.exists():
            cls.criar_areas_iniciais()
            areas = cls.objects.filter(ativo=True).order_by('ordem')
        return areas
    
    def get_badges_list(self):
        """Retorna badges como lista"""
        if self.badges:
            return [badge.strip() for badge in self.badges.split(',') if badge.strip()]
        return []
    
    def __str__(self):
        return f"{self.ordem}. {self.titulo}"
    
    def save(self, *args, **kwargs):
        """Override do save para validar ordem"""
        if not self.ordem:
            ultima_ordem = AreaAtuacao.objects.aggregate(
                max_ordem=models.Max('ordem')
            )['max_ordem']
            self.ordem = (ultima_ordem or 0) + 1
        super().save(*args, **kwargs)


class Configuracoes(models.Model):
    """
    Model para gerenciar as configurações gerais do site
    Apenas um registro deve existir (Singleton)
    """
    # Logos
    logo_header = models.ImageField(
        upload_to='configuracoes/logos/',
        blank=True,
        null=True,
        verbose_name="Logo do Header",
        help_text="Logo que aparece no cabeçalho do site"
    )
    
    logo_geral = models.ImageField(
        upload_to='configuracoes/logos/',
        blank=True,
        null=True,
        verbose_name="Logo Geral",
        help_text="Logo para footer e demais seções"
    )
    
    logo_hero = models.ImageField(
        upload_to='configuracoes/logos/',
        blank=True,
        null=True,
        verbose_name="Logo Hero",
        help_text="Logo para seção hero e 'desenvolvido por'"
    )
    
    # Informações de contato
    endereco = models.TextField(
        default="Rua Exemplo, 123<br>Centro - Nova Friburgo/RJ<br>CEP: 28600-000",
        verbose_name="Endereço",
        help_text="Use <br> para quebras de linha"
    )
    
    telefone = models.TextField(
        default="(22) 1234-5678<br>(22) 9 8765-4321",
        verbose_name="Telefone",
        help_text="Use <br> para quebras de linha"
    )
    
    horario_funcionamento = models.TextField(
        default="Segunda a Sexta: 8h às 17h<br>Sábado: 8h às 12h<br>Domingo: Fechado",
        verbose_name="Horário de Funcionamento",
        help_text="Use <br> para quebras de linha"
    )
    
    # Texto do rodapé
    texto_rodape = models.TextField(
        default="Fomentando o ecossistema de inovação e empreendedorismo em Nova Friburgo, conectando ideias transformadoras com oportunidades reais.",
        verbose_name="Texto do Rodapé",
        help_text="Texto descritivo que aparece no rodapé do site"
    )
    
    # Redes sociais
    instagram = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Instagram",
        help_text="URL do perfil do Instagram"
    )
    
    facebook = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Facebook",
        help_text="URL da página do Facebook"
    )
    
    whatsapp = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="WhatsApp",
        help_text="Número do WhatsApp (ex: 5522987654321)"
    )
    
    # Controles de estado
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )
    
    class Meta:
        verbose_name = "Configuração"
        verbose_name_plural = "CONFIGURAÇÕES"
        ordering = ['-criado_em']
    
    def clean(self):
        """Validação para garantir apenas um registro"""
        if not self.pk and Configuracoes.objects.exists():
            raise ValidationError('Apenas um registro de "Configurações" é permitido. Edite o registro existente.')
    
    def save(self, *args, **kwargs):
        """Override do save para garantir apenas um registro"""
        self.clean()
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Impede a exclusão do registro"""
        raise ValidationError('Este registro não pode ser excluído. Apenas editado.')
    
    @classmethod
    def get_instancia(cls):
        """Método para obter ou criar a instância única"""
        instancia, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'endereco': 'Rua Exemplo, 123<br>Centro - Nova Friburgo/RJ<br>CEP: 28600-000',
                'telefone': '(22) 1234-5678<br>(22) 9 8765-4321',
                'horario_funcionamento': 'Segunda a Sexta: 8h às 17h<br>Sábado: 8h às 12h<br>Domingo: Fechado',
                'texto_rodape': 'Fomentando o ecossistema de inovação e empreendedorismo em Nova Friburgo, conectando ideias transformadoras com oportunidades reais.'
            }
        )
        return instancia
    
    def get_logo_header_url(self):
        """Retorna URL da logo do header"""
        if self.logo_header:
            return self.logo_header.url
        return "/static/assets/images/logo_pmnf.png"  # Fallback para logo original do header
    
    def get_logo_geral_url(self):
        """Retorna URL da logo geral"""
        if self.logo_geral:
            return self.logo_geral.url
        return "/static/assets/images/logo_com_pmnf.png"  # Fallback para logo original do footer
    
    def get_logo_hero_url(self):
        """Retorna URL da logo hero"""
        if self.logo_hero:
            return self.logo_hero.url
        return "/static/assets/images/logo.png"  # Fallback para logo original do hero
    
    def get_whatsapp_url(self):
        """Retorna URL formatada para WhatsApp"""
        if self.whatsapp:
            return f"https://wa.me/{self.whatsapp}"
        return None
    
    def __str__(self):
        return "Configurações do Site"
