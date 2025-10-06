from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from datetime import timedelta
import uuid

# =============================================================================
# MODELOS BASE E CONFIGURAÇÕES
# =============================================================================

class StatusChoices(models.TextChoices):
    """Status padrão para projetos e programas"""
    NAO_INICIADO = 'nao_iniciado', 'Não Iniciado'
    EM_PLANEJAMENTO = 'em_planejamento', 'Em Planejamento'
    EM_EXECUCAO = 'em_execucao', 'Em Execução'
    EM_MONITORAMENTO = 'em_monitoramento', 'Em Monitoramento'
    SUSPENSO = 'suspenso', 'Suspenso'
    CANCELADO = 'cancelado', 'Cancelado'
    CONCLUIDO = 'concluido', 'Concluído'

class PrioridadeChoices(models.TextChoices):
    """Níveis de prioridade"""
    MUITO_BAIXA = 'muito_baixa', 'Muito Baixa'
    BAIXA = 'baixa', 'Baixa'
    MEDIA = 'media', 'Média'
    ALTA = 'alta', 'Alta'
    MUITO_ALTA = 'muito_alta', 'Muito Alta'
    CRITICA = 'critica', 'Crítica'

class TipoRecursoChoices(models.TextChoices):
    """Tipos de recursos"""
    HUMANO = 'humano', 'Recurso Humano'
    FINANCEIRO = 'financeiro', 'Recurso Financeiro'
    MATERIAL = 'material', 'Recurso Material'
    TECNOLOGICO = 'tecnologico', 'Recurso Tecnológico'
    INFRAESTRUTURA = 'infraestrutura', 'Infraestrutura'

class TipoRiscoChoices(models.TextChoices):
    """Tipos de risco"""
    TECNICO = 'tecnico', 'Técnico'
    CRONOGRAMA = 'cronograma', 'Cronograma'
    ORCAMENTO = 'orcamento', 'Orçamento'
    RECURSO = 'recurso', 'Recurso'
    EXTERNO = 'externo', 'Externo'
    ORGANIZACIONAL = 'organizacional', 'Organizacional'
    QUALIDADE = 'qualidade', 'Qualidade'

class ProbabilidadeChoices(models.TextChoices):
    """Probabilidade de ocorrência do risco"""
    MUITO_BAIXA = 'muito_baixa', 'Muito Baixa (1-10%)'
    BAIXA = 'baixa', 'Baixa (11-30%)'
    MEDIA = 'media', 'Média (31-50%)'
    ALTA = 'alta', 'Alta (51-70%)'
    MUITO_ALTA = 'muito_alta', 'Muito Alta (71-90%)'
    QUASE_CERTA = 'quase_certa', 'Quase Certa (91-99%)'

class ImpactoChoices(models.TextChoices):
    """Impacto do risco"""
    MUITO_BAIXO = 'muito_baixo', 'Muito Baixo'
    BAIXO = 'baixo', 'Baixo'
    MEDIO = 'medio', 'Médio'
    ALTO = 'alto', 'Alto'
    MUITO_ALTO = 'muito_alto', 'Muito Alto'

# =============================================================================
# CONFIGURAÇÕES E CATEGORIAS
# =============================================================================

class CategoriaEstrategica(models.Model):
    """Categorias estratégicas para alinhamento dos portfólios"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nome = models.CharField(max_length=100, verbose_name="Nome da Categoria")
    descricao = models.TextField(verbose_name="Descrição", blank=True)
    cor = models.CharField(max_length=7, default="#007bff", verbose_name="Cor (Hex)")
    icone = models.CharField(max_length=50, blank=True, verbose_name="Ícone CSS")
    peso_estrategico = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Peso Estratégico (1-10)"
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Categoria Estratégica"
        verbose_name_plural = "Categorias Estratégicas"
        ordering = ['-peso_estrategico', 'nome']

    def __str__(self):
        return f"{self.nome} (Peso: {self.peso_estrategico})"

class TipoProjeto(models.Model):
    """Tipos de projeto para categorização"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nome = models.CharField(max_length=100, verbose_name="Nome do Tipo")
    descricao = models.TextField(verbose_name="Descrição", blank=True)
    prefixo = models.CharField(max_length=10, verbose_name="Prefixo para Códigos")
    metodologia_sugerida = models.CharField(
        max_length=50,
        choices=[
            ('tradicional', 'Tradicional (Cascata)'),
            ('agil', 'Ágil (Scrum/Kanban)'),
            ('hibrido', 'Híbrido'),
            ('lean', 'Lean'),
        ],
        default='tradicional',
        verbose_name="Metodologia Sugerida"
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tipo de Projeto"
        verbose_name_plural = "Tipos de Projeto"
        ordering = ['nome']

    def __str__(self):
        return self.nome

class UnidadeOrganizacional(models.Model):
    """Unidades organizacionais responsáveis pelos projetos"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nome = models.CharField(max_length=100, verbose_name="Nome da Unidade")
    sigla = models.CharField(max_length=10, verbose_name="Sigla")
    descricao = models.TextField(verbose_name="Descrição", blank=True)
    unidade_pai = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Unidade Superior"
    )
    responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Responsável"
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Unidade Organizacional"
        verbose_name_plural = "Unidades Organizacionais"
        ordering = ['nome']

    def __str__(self):
        return f"{self.sigla} - {self.nome}"

# =============================================================================
# PORTFÓLIO
# =============================================================================

class Portfolio(models.Model):
    """Portfólio de projetos e programas"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nome = models.CharField(max_length=100, verbose_name="Nome do Portfólio")
    descricao = models.TextField(verbose_name="Descrição")
    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código")
    
    # Responsabilidades
    gestor_portfolio = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='portfolios_gerenciados',
        verbose_name="Gestor do Portfólio"
    )
    patrocinador = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='portfolios_patrocinados',
        verbose_name="Patrocinador"
    )
    unidade_organizacional = models.ForeignKey(
        UnidadeOrganizacional,
        on_delete=models.PROTECT,
        verbose_name="Unidade Organizacional"
    )
    
    # Alinhamento estratégico
    categoria_estrategica = models.ForeignKey(
        CategoriaEstrategica,
        on_delete=models.PROTECT,
        verbose_name="Categoria Estratégica"
    )
    
    # Orçamento e recursos
    orcamento_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Orçamento Total"
    )
    
    # Datas
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_fim_prevista = models.DateField(verbose_name="Data Fim Prevista")
    data_fim_real = models.DateField(null=True, blank=True, verbose_name="Data Fim Real")
    
    # Status e controle
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.NAO_INICIADO,
        verbose_name="Status"
    )
    prioridade = models.CharField(
        max_length=15,
        choices=PrioridadeChoices.choices,
        default=PrioridadeChoices.MEDIA,
        verbose_name="Prioridade"
    )
    
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Portfólio"
        verbose_name_plural = "Portfólios"
        ordering = ['-prioridade', 'nome']

    def __str__(self):
        return f"{self.codigo} - {self.nome}"

    def get_valor_total_projetos(self):
        """Calcula o valor total dos projetos do portfólio"""
        return sum([p.orcamento_total for p in self.projetos.all()] + 
                  [p.orcamento_total for programa in self.programas.all() 
                   for p in programa.projetos.all()])

    def get_percentual_conclusao(self):
        """Calcula o percentual médio de conclusão do portfólio"""
        projetos = list(self.projetos.all())
        for programa in self.programas.all():
            projetos.extend(programa.projetos.all())
        
        if not projetos:
            return 0
        
        total_conclusao = sum([p.percentual_conclusao for p in projetos])
        return total_conclusao / len(projetos)

# =============================================================================
# PROGRAMA
# =============================================================================

class Programa(models.Model):
    """Programa que agrupa projetos relacionados"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nome = models.CharField(max_length=100, verbose_name="Nome do Programa")
    descricao = models.TextField(verbose_name="Descrição")
    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código")
    
    # Relacionamentos
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name='programas',
        verbose_name="Portfólio"
    )
    
    # Responsabilidades
    gerente_programa = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='programas_gerenciados',
        verbose_name="Gerente do Programa"
    )
    
    # Objetivos e benefícios
    objetivos = models.TextField(verbose_name="Objetivos do Programa")
    beneficios_esperados = models.TextField(verbose_name="Benefícios Esperados")
    
    # Orçamento e recursos
    orcamento_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Orçamento Total"
    )
    
    # Datas
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_fim_prevista = models.DateField(verbose_name="Data Fim Prevista")
    data_fim_real = models.DateField(null=True, blank=True, verbose_name="Data Fim Real")
    
    # Status e controle
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.NAO_INICIADO,
        verbose_name="Status"
    )
    prioridade = models.CharField(
        max_length=15,
        choices=PrioridadeChoices.choices,
        default=PrioridadeChoices.MEDIA,
        verbose_name="Prioridade"
    )
    
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Programa"
        verbose_name_plural = "Programas"
        ordering = ['-prioridade', 'nome']

    def __str__(self):
        return f"{self.codigo} - {self.nome}"

    def get_percentual_conclusao(self):
        """Calcula o percentual médio de conclusão do programa"""
        projetos = self.projetos.all()
        if not projetos:
            return 0
        
        total_conclusao = sum([p.percentual_conclusao for p in projetos])
        return total_conclusao / len(projetos)

# =============================================================================
# PROJETO
# =============================================================================

class Projeto(models.Model):
    """Projeto individual"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nome = models.CharField(max_length=100, verbose_name="Nome do Projeto")
    descricao = models.TextField(verbose_name="Descrição")
    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código")
    
    # Relacionamentos
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name='projetos',
        verbose_name="Portfólio",
        null=True,
        blank=True
    )
    programa = models.ForeignKey(
        Programa,
        on_delete=models.CASCADE,
        related_name='projetos',
        verbose_name="Programa",
        null=True,
        blank=True
    )
    tipo_projeto = models.ForeignKey(
        TipoProjeto,
        on_delete=models.PROTECT,
        verbose_name="Tipo de Projeto"
    )
    
    # Responsabilidades
    gerente_projeto = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='projetos_gerenciados',
        verbose_name="Gerente do Projeto"
    )
    patrocinador = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='projetos_patrocinados',
        verbose_name="Patrocinador"
    )
    
    # Definição do projeto
    objetivos = models.TextField(verbose_name="Objetivos")
    escopo_produto = models.TextField(verbose_name="Escopo do Produto")
    escopo_trabalho = models.TextField(verbose_name="Escopo do Trabalho")
    premissas = models.TextField(verbose_name="Premissas", blank=True)
    restricoes = models.TextField(verbose_name="Restrições", blank=True)
    nao_escopo = models.TextField(verbose_name="Não Escopo", blank=True)
    
    # Orçamento e recursos
    orcamento_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Orçamento Total"
    )
    orcamento_consumido = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Orçamento Consumido"
    )
    
    # Datas
    data_inicio_prevista = models.DateField(verbose_name="Data Início Prevista")
    data_inicio_real = models.DateField(null=True, blank=True, verbose_name="Data Início Real")
    data_fim_prevista = models.DateField(verbose_name="Data Fim Prevista")
    data_fim_real = models.DateField(null=True, blank=True, verbose_name="Data Fim Real")
    
    # Percentual de conclusão
    percentual_conclusao = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Percentual de Conclusão (%)"
    )
    
    # Status e controle
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.NAO_INICIADO,
        verbose_name="Status"
    )
    prioridade = models.CharField(
        max_length=15,
        choices=PrioridadeChoices.choices,
        default=PrioridadeChoices.MEDIA,
        verbose_name="Prioridade"
    )
    
    # Metodologia
    metodologia = models.CharField(
        max_length=50,
        choices=[
            ('tradicional', 'Tradicional (Cascata)'),
            ('agil', 'Ágil (Scrum/Kanban)'),
            ('hibrido', 'Híbrido'),
            ('lean', 'Lean'),
        ],
        default='tradicional',
        verbose_name="Metodologia"
    )
    
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Projeto"
        verbose_name_plural = "Projetos"
        ordering = ['-prioridade', 'nome']

    def __str__(self):
        return f"{self.codigo} - {self.nome}"

    def clean(self):
        """Validações do modelo"""
        if self.data_inicio_prevista and self.data_fim_prevista:
            if self.data_inicio_prevista >= self.data_fim_prevista:
                raise ValidationError('Data de início deve ser anterior à data de fim.')
        
        if self.data_inicio_real and self.data_fim_real:
            if self.data_inicio_real >= self.data_fim_real:
                raise ValidationError('Data de início real deve ser anterior à data de fim real.')
        
        if self.orcamento_consumido > self.orcamento_total:
            raise ValidationError('Orçamento consumido não pode ser maior que o orçamento total.')

    def get_percentual_orcamento_consumido(self):
        """Calcula o percentual do orçamento consumido"""
        if self.orcamento_total > 0:
            return (self.orcamento_consumido / self.orcamento_total) * 100
        return 0

    def get_saldo_orcamento(self):
        """Calcula o saldo do orçamento"""
        return self.orcamento_total - self.orcamento_consumido

    def get_status_prazo(self):
        """Retorna o status do prazo do projeto"""
        from datetime import date
        hoje = date.today()
        
        if self.status == StatusChoices.CONCLUIDO:
            if self.data_fim_real and self.data_fim_real <= self.data_fim_prevista:
                return 'no_prazo'
            else:
                return 'atrasado'
        
        if hoje > self.data_fim_prevista:
            return 'atrasado'
        elif hoje > self.data_fim_prevista - timedelta(days=7):  # Uma semana de antecedência
            return 'atencao'
        else:
            return 'no_prazo'

# =============================================================================
# EQUIPE E RECURSOS
# =============================================================================

class EquipeProjeto(models.Model):
    """Equipe do projeto"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        related_name='equipe',
        verbose_name="Projeto"
    )
    membro = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Membro da Equipe"
    )
    papel = models.CharField(
        max_length=50,
        choices=[
            ('gerente', 'Gerente de Projeto'),
            ('coordenador', 'Coordenador'),
            ('analista', 'Analista'),
            ('desenvolvedor', 'Desenvolvedor'),
            ('designer', 'Designer'),
            ('tester', 'Testador'),
            ('especialista', 'Especialista'),
            ('consultor', 'Consultor'),
            ('outro', 'Outro'),
        ],
        verbose_name="Papel"
    )
    responsabilidades = models.TextField(verbose_name="Responsabilidades", blank=True)
    dedicacao_percentual = models.IntegerField(
        default=100,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name="Dedicação (%)"
    )
    data_entrada = models.DateField(verbose_name="Data de Entrada")
    data_saida = models.DateField(null=True, blank=True, verbose_name="Data de Saída")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Membro da Equipe"
        verbose_name_plural = "Equipe do Projeto"
        unique_together = ['projeto', 'membro']

    def __str__(self):
        return f"{self.projeto.codigo} - {self.membro.get_full_name()} ({self.papel})"

class RecursoProjeto(models.Model):
    """Recursos necessários/alocados ao projeto"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        related_name='recursos',
        verbose_name="Projeto"
    )
    nome = models.CharField(max_length=100, verbose_name="Nome do Recurso")
    tipo = models.CharField(
        max_length=20,
        choices=TipoRecursoChoices.choices,
        verbose_name="Tipo de Recurso"
    )
    descricao = models.TextField(verbose_name="Descrição", blank=True)
    quantidade_necessaria = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Quantidade Necessária"
    )
    quantidade_alocada = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Quantidade Alocada"
    )
    unidade_medida = models.CharField(
        max_length=20,
        verbose_name="Unidade de Medida"
    )
    custo_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Custo Unitário"
    )
    data_necessidade = models.DateField(verbose_name="Data de Necessidade")
    observacoes = models.TextField(verbose_name="Observações", blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Recurso do Projeto"
        verbose_name_plural = "Recursos do Projeto"
        ordering = ['data_necessidade', 'nome']

    def __str__(self):
        return f"{self.projeto.codigo} - {self.nome}"

    def get_custo_total(self):
        """Calcula o custo total do recurso"""
        return self.quantidade_necessaria * self.custo_unitario

    def get_percentual_alocado(self):
        """Calcula o percentual alocado do recurso"""
        if self.quantidade_necessaria > 0:
            return (self.quantidade_alocada / self.quantidade_necessaria) * 100
        return 0

# =============================================================================
# CRONOGRAMA E ENTREGAS
# =============================================================================

class FaseProjeto(models.Model):
    """Fases do projeto"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        related_name='fases',
        verbose_name="Projeto"
    )
    nome = models.CharField(max_length=100, verbose_name="Nome da Fase")
    descricao = models.TextField(verbose_name="Descrição", blank=True)
    ordem = models.PositiveIntegerField(verbose_name="Ordem")
    data_inicio_prevista = models.DateField(verbose_name="Data Início Prevista")
    data_inicio_real = models.DateField(null=True, blank=True, verbose_name="Data Início Real")
    data_fim_prevista = models.DateField(verbose_name="Data Fim Prevista")
    data_fim_real = models.DateField(null=True, blank=True, verbose_name="Data Fim Real")
    percentual_conclusao = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Percentual de Conclusão (%)"
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.NAO_INICIADO,
        verbose_name="Status"
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Fase do Projeto"
        verbose_name_plural = "Fases do Projeto"
        ordering = ['projeto', 'ordem']
        unique_together = ['projeto', 'ordem']

    def __str__(self):
        return f"{self.projeto.codigo} - Fase {self.ordem}: {self.nome}"

class Entrega(models.Model):
    """Entregas/Deliverables do projeto"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        related_name='entregas',
        verbose_name="Projeto"
    )
    fase = models.ForeignKey(
        FaseProjeto,
        on_delete=models.CASCADE,
        related_name='entregas',
        verbose_name="Fase",
        null=True,
        blank=True
    )
    nome = models.CharField(max_length=100, verbose_name="Nome da Entrega")
    descricao = models.TextField(verbose_name="Descrição")
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('documento', 'Documento'),
            ('prototipo', 'Protótipo'),
            ('sistema', 'Sistema'),
            ('relatorio', 'Relatório'),
            ('treinamento', 'Treinamento'),
            ('outro', 'Outro'),
        ],
        default='documento',
        verbose_name="Tipo de Entrega"
    )
    responsavel = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Responsável"
    )
    data_prevista = models.DateField(verbose_name="Data Prevista")
    data_entrega = models.DateField(null=True, blank=True, verbose_name="Data de Entrega")
    status = models.CharField(
        max_length=20,
        choices=[
            ('nao_iniciado', 'Não Iniciado'),
            ('em_desenvolvimento', 'Em Desenvolvimento'),
            ('em_revisao', 'Em Revisão'),
            ('aprovado', 'Aprovado'),
            ('rejeitado', 'Rejeitado'),
            ('entregue', 'Entregue'),
        ],
        default='nao_iniciado',
        verbose_name="Status"
    )
    criterios_aceitacao = models.TextField(
        verbose_name="Critérios de Aceitação",
        blank=True
    )
    observacoes = models.TextField(verbose_name="Observações", blank=True)
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Entrega"
        verbose_name_plural = "Entregas"
        ordering = ['data_prevista', 'nome']

    def __str__(self):
        return f"{self.projeto.codigo} - {self.nome}"

    def get_status_prazo(self):
        """Retorna o status do prazo da entrega"""
        from datetime import date
        hoje = date.today()
        
        if self.status == 'entregue':
            if self.data_entrega and self.data_entrega <= self.data_prevista:
                return 'no_prazo'
            else:
                return 'atrasado'
        
        if hoje > self.data_prevista:
            return 'atrasado'
        elif hoje > self.data_prevista - timedelta(days=3):  # 3 dias de antecedência
            return 'atencao'
        else:
            return 'no_prazo'

class Marco(models.Model):
    """Marcos/Milestones do projeto"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        related_name='marcos',
        verbose_name="Projeto"
    )
    nome = models.CharField(max_length=100, verbose_name="Nome do Marco")
    descricao = models.TextField(verbose_name="Descrição")
    data_prevista = models.DateField(verbose_name="Data Prevista")
    data_real = models.DateField(null=True, blank=True, verbose_name="Data Real")
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('inicio_projeto', 'Início do Projeto'),
            ('fim_fase', 'Fim de Fase'),
            ('aprovacao', 'Aprovação'),
            ('entrega_principal', 'Entrega Principal'),
            ('fim_projeto', 'Fim do Projeto'),
            ('outro', 'Outro'),
        ],
        default='outro',
        verbose_name="Tipo de Marco"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pendente', 'Pendente'),
            ('atingido', 'Atingido'),
            ('atrasado', 'Atrasado'),
        ],
        default='pendente',
        verbose_name="Status"
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Marco"
        verbose_name_plural = "Marcos"
        ordering = ['data_prevista', 'nome']

    def __str__(self):
        return f"{self.projeto.codigo} - {self.nome}"

# =============================================================================
# GESTÃO DE RISCOS
# =============================================================================

class RiscoProjeto(models.Model):
    """Riscos identificados no projeto"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        related_name='riscos',
        verbose_name="Projeto"
    )
    titulo = models.CharField(max_length=100, verbose_name="Título do Risco")
    descricao = models.TextField(verbose_name="Descrição do Risco")
    categoria = models.CharField(
        max_length=20,
        choices=TipoRiscoChoices.choices,
        verbose_name="Categoria"
    )
    probabilidade = models.CharField(
        max_length=15,
        choices=ProbabilidadeChoices.choices,
        verbose_name="Probabilidade"
    )
    impacto = models.CharField(
        max_length=15,
        choices=ImpactoChoices.choices,
        verbose_name="Impacto"
    )
    
    # Estratégia de resposta
    estrategia_resposta = models.CharField(
        max_length=20,
        choices=[
            ('evitar', 'Evitar'),
            ('mitigar', 'Mitigar'),
            ('transferir', 'Transferir'),
            ('aceitar', 'Aceitar'),
        ],
        verbose_name="Estratégia de Resposta"
    )
    plano_resposta = models.TextField(
        verbose_name="Plano de Resposta",
        blank=True
    )
    responsavel = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Responsável"
    )
    
    # Datas
    data_identificacao = models.DateField(verbose_name="Data de Identificação")
    data_prazo_resposta = models.DateField(
        null=True,
        blank=True,
        verbose_name="Prazo para Resposta"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('identificado', 'Identificado'),
            ('em_analise', 'Em Análise'),
            ('em_tratamento', 'Em Tratamento'),
            ('monitorando', 'Monitorando'),
            ('materializado', 'Materializado'),
            ('encerrado', 'Encerrado'),
        ],
        default='identificado',
        verbose_name="Status"
    )
    
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Risco do Projeto"
        verbose_name_plural = "Riscos do Projeto"
        ordering = ['-data_identificacao']

    def __str__(self):
        return f"{self.projeto.codigo} - {self.titulo}"

    def get_nivel_risco(self):
        """Calcula o nível do risco baseado em probabilidade e impacto"""
        niveis_prob = {
            'muito_baixa': 1, 'baixa': 2, 'media': 3, 'alta': 4, 'muito_alta': 5, 'quase_certa': 6
        }
        niveis_imp = {
            'muito_baixo': 1, 'baixo': 2, 'medio': 3, 'alto': 4, 'muito_alto': 5
        }
        
        prob_valor = niveis_prob.get(self.probabilidade, 1)
        imp_valor = niveis_imp.get(self.impacto, 1)
        nivel = prob_valor * imp_valor
        
        if nivel <= 6:
            return 'baixo'
        elif nivel <= 15:
            return 'medio'
        else:
            return 'alto'

# =============================================================================
# COMUNICAÇÃO E MUDANÇAS
# =============================================================================

class StakeholderProjeto(models.Model):
    """Partes interessadas do projeto"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        related_name='stakeholders',
        verbose_name="Projeto"
    )
    nome = models.CharField(max_length=100, verbose_name="Nome")
    cargo = models.CharField(max_length=100, verbose_name="Cargo")
    organizacao = models.CharField(max_length=100, verbose_name="Organização")
    email = models.EmailField(verbose_name="E-mail", blank=True)
    telefone = models.CharField(max_length=20, verbose_name="Telefone", blank=True)
    
    # Classificação
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('interno', 'Interno'),
            ('externo', 'Externo'),
            ('cliente', 'Cliente'),
            ('fornecedor', 'Fornecedor'),
            ('usuario_final', 'Usuário Final'),
        ],
        verbose_name="Tipo"
    )
    nivel_influencia = models.CharField(
        max_length=10,
        choices=[
            ('baixo', 'Baixo'),
            ('medio', 'Médio'),
            ('alto', 'Alto'),
        ],
        default='medio',
        verbose_name="Nível de Influência"
    )
    nivel_interesse = models.CharField(
        max_length=10,
        choices=[
            ('baixo', 'Baixo'),
            ('medio', 'Médio'),
            ('alto', 'Alto'),
        ],
        default='medio',
        verbose_name="Nível de Interesse"
    )
    
    # Comunicação
    frequencia_comunicacao = models.CharField(
        max_length=20,
        choices=[
            ('diaria', 'Diária'),
            ('semanal', 'Semanal'),
            ('quinzenal', 'Quinzenal'),
            ('mensal', 'Mensal'),
            ('sob_demanda', 'Sob Demanda'),
        ],
        default='semanal',
        verbose_name="Frequência de Comunicação"
    )
    metodo_comunicacao = models.CharField(
        max_length=20,
        choices=[
            ('email', 'E-mail'),
            ('reuniao', 'Reunião'),
            ('relatorio', 'Relatório'),
            ('dashboard', 'Dashboard'),
            ('telefone', 'Telefone'),
        ],
        default='email',
        verbose_name="Método de Comunicação"
    )
    
    observacoes = models.TextField(verbose_name="Observações", blank=True)
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Stakeholder"
        verbose_name_plural = "Stakeholders"
        ordering = ['nome']

    def __str__(self):
        return f"{self.projeto.codigo} - {self.nome}"

class SolicitacaoMudanca(models.Model):
    """Solicitações de mudança no projeto"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        related_name='mudancas',
        verbose_name="Projeto"
    )
    numero = models.CharField(max_length=20, verbose_name="Número da Solicitação")
    titulo = models.CharField(max_length=100, verbose_name="Título")
    descricao = models.TextField(verbose_name="Descrição da Mudança")
    justificativa = models.TextField(verbose_name="Justificativa")
    
    # Solicitante
    solicitante = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='mudancas_solicitadas',
        verbose_name="Solicitante"
    )
    data_solicitacao = models.DateField(verbose_name="Data da Solicitação")
    
    # Impactos
    impacto_cronograma = models.TextField(
        verbose_name="Impacto no Cronograma",
        blank=True
    )
    impacto_orcamento = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Impacto no Orçamento"
    )
    impacto_qualidade = models.TextField(
        verbose_name="Impacto na Qualidade",
        blank=True
    )
    impacto_recursos = models.TextField(
        verbose_name="Impacto nos Recursos",
        blank=True
    )
    
    # Aprovação
    status = models.CharField(
        max_length=20,
        choices=[
            ('pendente', 'Pendente'),
            ('em_analise', 'Em Análise'),
            ('aprovada', 'Aprovada'),
            ('rejeitada', 'Rejeitada'),
            ('implementada', 'Implementada'),
        ],
        default='pendente',
        verbose_name="Status"
    )
    aprovador = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='mudancas_aprovadas',
        null=True,
        blank=True,
        verbose_name="Aprovador"
    )
    data_aprovacao = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data da Aprovação"
    )
    observacoes_aprovacao = models.TextField(
        verbose_name="Observações da Aprovação",
        blank=True
    )
    
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Solicitação de Mudança"
        verbose_name_plural = "Solicitações de Mudança"
        ordering = ['-data_solicitacao']
        unique_together = ['projeto', 'numero']

    def __str__(self):
        return f"{self.numero} - {self.titulo}"

# =============================================================================
# ANEXOS E DOCUMENTOS
# =============================================================================

class AnexoProjeto(models.Model):
    """Anexos e documentos do projeto"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        related_name='anexos',
        verbose_name="Projeto"
    )
    nome = models.CharField(max_length=100, verbose_name="Nome do Anexo")
    descricao = models.TextField(verbose_name="Descrição", blank=True)
    
    # Arquivo ou Link
    tipo = models.CharField(
        max_length=10,
        choices=[
            ('arquivo', 'Arquivo'),
            ('link', 'Link Externo'),
        ],
        default='arquivo',
        verbose_name="Tipo"
    )
    arquivo = models.FileField(
        upload_to='projetos/anexos/',
        blank=True,
        null=True,
        verbose_name="Arquivo"
    )
    link = models.URLField(
        blank=True,
        null=True,
        verbose_name="Link Externo"
    )
    
    # Categorização
    categoria = models.CharField(
        max_length=20,
        choices=[
            ('charter', 'Project Charter'),
            ('cronograma', 'Cronograma'),
            ('orcamento', 'Orçamento'),
            ('escopo', 'Escopo'),
            ('risco', 'Análise de Riscos'),
            ('comunicacao', 'Comunicação'),
            ('qualidade', 'Qualidade'),
            ('outro', 'Outro'),
        ],
        default='outro',
        verbose_name="Categoria"
    )
    
    # Controle de versão
    versao = models.CharField(
        max_length=10,
        default='1.0',
        verbose_name="Versão"
    )
    autor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Autor"
    )
    
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Anexo do Projeto"
        verbose_name_plural = "Anexos do Projeto"
        ordering = ['-atualizado_em']

    def __str__(self):
        return f"{self.projeto.codigo} - {self.nome}"

    def clean(self):
        """Validação para garantir arquivo OU link"""
        if self.tipo == 'arquivo' and not self.arquivo:
            raise ValidationError('Arquivo é obrigatório quando tipo é "Arquivo".')
        if self.tipo == 'link' and not self.link:
            raise ValidationError('Link é obrigatório quando tipo é "Link Externo".')

    def get_icone(self):
        """Retorna ícone baseado no tipo"""
        if self.tipo == 'link':
            return 'fa-solid fa-link'
        else:
            # Determinar ícone baseado na extensão do arquivo
            if self.arquivo:
                nome = self.arquivo.name.lower()
                if nome.endswith(('.pdf',)):
                    return 'fa-solid fa-file-pdf'
                elif nome.endswith(('.doc', '.docx')):
                    return 'fa-solid fa-file-word'
                elif nome.endswith(('.xls', '.xlsx')):
                    return 'fa-solid fa-file-excel'
                elif nome.endswith(('.ppt', '.pptx')):
                    return 'fa-solid fa-file-powerpoint'
                elif nome.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    return 'fa-solid fa-file-image'
            return 'fa-solid fa-file'

    def delete(self, *args, **kwargs):
        """Remove arquivo físico ao deletar o registro"""
        if self.arquivo:
            self.arquivo.delete(save=False)
        super().delete(*args, **kwargs)

# =============================================================================
# CRONOGRAMA E ENTREGAS
# =============================================================================

class FaseProjeto(models.Model):
    """Fases do projeto"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        related_name='fases',
        verbose_name="Projeto"
    )
    nome = models.CharField(max_length=100, verbose_name="Nome da Fase")
    descricao = models.TextField(verbose_name="Descrição", blank=True)
    ordem = models.PositiveIntegerField(verbose_name="Ordem")
    data_inicio_prevista = models.DateField(verbose_name="Data Início Prevista")
    data_inicio_real = models.DateField(null=True, blank=True, verbose_name="Data Início Real")
    data_fim_prevista = models.DateField(verbose_name="Data Fim Prevista")
    data_fim_real = models.DateField(null=True, blank=True, verbose_name="Data Fim Real")
    percentual_conclusao = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Percentual de Conclusão (%)"
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.NAO_INICIADO,
        verbose_name="Status"
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Fase do Projeto"
        verbose_name_plural = "Fases do Projeto"
        ordering = ['projeto', 'ordem']
        unique_together = ['projeto', 'ordem']

    def __str__(self):
        return f"{self.projeto.codigo} - Fase {self.ordem}: {self.nome}"

class Entrega(models.Model):
    """Entregas/Deliverables do projeto"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        related_name='entregas',
        verbose_name="Projeto"
    )
    fase = models.ForeignKey(
        FaseProjeto,
        on_delete=models.CASCADE,
        related_name='entregas',
        verbose_name="Fase",
        null=True,
        blank=True
    )
    nome = models.CharField(max_length=100, verbose_name="Nome da Entrega")
    descricao = models.TextField(verbose_name="Descrição")
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('documento', 'Documento'),
            ('prototipo', 'Protótipo'),
            ('sistema', 'Sistema'),
            ('relatorio', 'Relatório'),
            ('treinamento', 'Treinamento'),
            ('outro', 'Outro'),
        ],
        default='documento',
        verbose_name="Tipo de Entrega"
    )
    responsavel = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Responsável"
    )
    data_prevista = models.DateField(verbose_name="Data Prevista")
    data_entrega = models.DateField(null=True, blank=True, verbose_name="Data de Entrega")
    status = models.CharField(
        max_length=20,
        choices=[
            ('nao_iniciado', 'Não Iniciado'),
            ('em_desenvolvimento', 'Em Desenvolvimento'),
            ('em_revisao', 'Em Revisão'),
            ('aprovado', 'Aprovado'),
            ('rejeitado', 'Rejeitado'),
            ('entregue', 'Entregue'),
        ],
        default='nao_iniciado',
        verbose_name="Status"
    )
    criterios_aceitacao = models.TextField(
        verbose_name="Critérios de Aceitação",
        blank=True
    )
    observacoes = models.TextField(verbose_name="Observações", blank=True)
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Entrega"
        verbose_name_plural = "Entregas"
        ordering = ['data_prevista', 'nome']

    def __str__(self):
        return f"{self.projeto.codigo} - {self.nome}"

    def get_status_prazo(self):
        """Retorna o status do prazo da entrega"""
        from datetime import date
        hoje = date.today()
        
        if self.status == 'entregue':
            if self.data_entrega and self.data_entrega <= self.data_prevista:
                return 'no_prazo'
            else:
                return 'atrasado'
        
        if hoje > self.data_prevista:
            return 'atrasado'
        elif hoje > self.data_prevista - timedelta(days=3):  # 3 dias de antecedência
            return 'atencao'
        else:
            return 'no_prazo'

class Marco(models.Model):
    """Marcos/Milestones do projeto"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        related_name='marcos',
        verbose_name="Projeto"
    )
    nome = models.CharField(max_length=100, verbose_name="Nome do Marco")
    descricao = models.TextField(verbose_name="Descrição")
    data_prevista = models.DateField(verbose_name="Data Prevista")
    data_real = models.DateField(null=True, blank=True, verbose_name="Data Real")
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('inicio_projeto', 'Início do Projeto'),
            ('fim_fase', 'Fim de Fase'),
            ('aprovacao', 'Aprovação'),
            ('entrega_principal', 'Entrega Principal'),
            ('fim_projeto', 'Fim do Projeto'),
            ('outro', 'Outro'),
        ],
        default='outro',
        verbose_name="Tipo de Marco"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pendente', 'Pendente'),
            ('atingido', 'Atingido'),
            ('atrasado', 'Atrasado'),
        ],
        default='pendente',
        verbose_name="Status"
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Marco"
        verbose_name_plural = "Marcos"
        ordering = ['data_prevista', 'nome']

    def __str__(self):
        return f"{self.projeto.codigo} - {self.nome}"

# =============================================================================
# GESTÃO DE RISCOS
# =============================================================================

class RiscoProjeto(models.Model):
    """Riscos identificados no projeto"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        related_name='riscos',
        verbose_name="Projeto"
    )
    titulo = models.CharField(max_length=100, verbose_name="Título do Risco")
    descricao = models.TextField(verbose_name="Descrição do Risco")
    categoria = models.CharField(
        max_length=20,
        choices=TipoRiscoChoices.choices,
        verbose_name="Categoria"
    )
    probabilidade = models.CharField(
        max_length=15,
        choices=ProbabilidadeChoices.choices,
        verbose_name="Probabilidade"
    )
    impacto = models.CharField(
        max_length=15,
        choices=ImpactoChoices.choices,
        verbose_name="Impacto"
    )
    
    # Estratégia de resposta
    estrategia_resposta = models.CharField(
        max_length=20,
        choices=[
            ('evitar', 'Evitar'),
            ('mitigar', 'Mitigar'),
            ('transferir', 'Transferir'),
            ('aceitar', 'Aceitar'),
        ],
        verbose_name="Estratégia de Resposta"
    )
    plano_resposta = models.TextField(
        verbose_name="Plano de Resposta",
        blank=True
    )
    responsavel = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Responsável"
    )
    
    # Datas
    data_identificacao = models.DateField(verbose_name="Data de Identificação")
    data_prazo_resposta = models.DateField(
        null=True,
        blank=True,
        verbose_name="Prazo para Resposta"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('identificado', 'Identificado'),
            ('em_analise', 'Em Análise'),
            ('em_tratamento', 'Em Tratamento'),
            ('monitorando', 'Monitorando'),
            ('materializado', 'Materializado'),
            ('encerrado', 'Encerrado'),
        ],
        default='identificado',
        verbose_name="Status"
    )
    
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Risco do Projeto"
        verbose_name_plural = "Riscos do Projeto"
        ordering = ['-data_identificacao']

    def __str__(self):
        return f"{self.projeto.codigo} - {self.titulo}"

    def get_nivel_risco(self):
        """Calcula o nível do risco baseado em probabilidade e impacto"""
        niveis_prob = {
            'muito_baixa': 1, 'baixa': 2, 'media': 3, 'alta': 4, 'muito_alta': 5, 'quase_certa': 6
        }
        niveis_imp = {
            'muito_baixo': 1, 'baixo': 2, 'medio': 3, 'alto': 4, 'muito_alto': 5
        }
        
        prob_valor = niveis_prob.get(self.probabilidade, 1)
        imp_valor = niveis_imp.get(self.impacto, 1)
        nivel = prob_valor * imp_valor
        
        if nivel <= 6:
            return 'baixo'
        elif nivel <= 15:
            return 'medio'
        else:
            return 'alto'

# =============================================================================
# COMUNICAÇÃO E MUDANÇAS
# =============================================================================

class StakeholderProjeto(models.Model):
    """Partes interessadas do projeto"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        related_name='stakeholders',
        verbose_name="Projeto"
    )
    nome = models.CharField(max_length=100, verbose_name="Nome")
    cargo = models.CharField(max_length=100, verbose_name="Cargo")
    organizacao = models.CharField(max_length=100, verbose_name="Organização")
    email = models.EmailField(verbose_name="E-mail", blank=True)
    telefone = models.CharField(max_length=20, verbose_name="Telefone", blank=True)
    
    # Classificação
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('interno', 'Interno'),
            ('externo', 'Externo'),
            ('cliente', 'Cliente'),
            ('fornecedor', 'Fornecedor'),
            ('usuario_final', 'Usuário Final'),
        ],
        verbose_name="Tipo"
    )
    nivel_influencia = models.CharField(
        max_length=10,
        choices=[
            ('baixo', 'Baixo'),
            ('medio', 'Médio'),
            ('alto', 'Alto'),
        ],
        default='medio',
        verbose_name="Nível de Influência"
    )
    nivel_interesse = models.CharField(
        max_length=10,
        choices=[
            ('baixo', 'Baixo'),
            ('medio', 'Médio'),
            ('alto', 'Alto'),
        ],
        default='medio',
        verbose_name="Nível de Interesse"
    )
    
    # Comunicação
    frequencia_comunicacao = models.CharField(
        max_length=20,
        choices=[
            ('diaria', 'Diária'),
            ('semanal', 'Semanal'),
            ('quinzenal', 'Quinzenal'),
            ('mensal', 'Mensal'),
            ('sob_demanda', 'Sob Demanda'),
        ],
        default='semanal',
        verbose_name="Frequência de Comunicação"
    )
    metodo_comunicacao = models.CharField(
        max_length=20,
        choices=[
            ('email', 'E-mail'),
            ('reuniao', 'Reunião'),
            ('relatorio', 'Relatório'),
            ('dashboard', 'Dashboard'),
            ('telefone', 'Telefone'),
        ],
        default='email',
        verbose_name="Método de Comunicação"
    )
    
    observacoes = models.TextField(verbose_name="Observações", blank=True)
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Stakeholder"
        verbose_name_plural = "Stakeholders"
        ordering = ['nome']

    def __str__(self):
        return f"{self.projeto.codigo} - {self.nome}"

class SolicitacaoMudanca(models.Model):
    """Solicitações de mudança no projeto"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        related_name='mudancas',
        verbose_name="Projeto"
    )
    numero = models.CharField(max_length=20, verbose_name="Número da Solicitação")
    titulo = models.CharField(max_length=100, verbose_name="Título")
    descricao = models.TextField(verbose_name="Descrição da Mudança")
    justificativa = models.TextField(verbose_name="Justificativa")
    
    # Solicitante
    solicitante = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='mudancas_solicitadas',
        verbose_name="Solicitante"
    )
    data_solicitacao = models.DateField(verbose_name="Data da Solicitação")
    
    # Impactos
    impacto_cronograma = models.TextField(
        verbose_name="Impacto no Cronograma",
        blank=True
    )
    impacto_orcamento = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Impacto no Orçamento"
    )
    impacto_qualidade = models.TextField(
        verbose_name="Impacto na Qualidade",
        blank=True
    )
    impacto_recursos = models.TextField(
        verbose_name="Impacto nos Recursos",
        blank=True
    )
    
    # Aprovação
    status = models.CharField(
        max_length=20,
        choices=[
            ('pendente', 'Pendente'),
            ('em_analise', 'Em Análise'),
            ('aprovada', 'Aprovada'),
            ('rejeitada', 'Rejeitada'),
            ('implementada', 'Implementada'),
        ],
        default='pendente',
        verbose_name="Status"
    )
    aprovador = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='mudancas_aprovadas',
        null=True,
        blank=True,
        verbose_name="Aprovador"
    )
    data_aprovacao = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data da Aprovação"
    )
    observacoes_aprovacao = models.TextField(
        verbose_name="Observações da Aprovação",
        blank=True
    )
    
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Solicitação de Mudança"
        verbose_name_plural = "Solicitações de Mudança"
        ordering = ['-data_solicitacao']
        unique_together = ['projeto', 'numero']

    def __str__(self):
        return f"{self.numero} - {self.titulo}"

# =============================================================================
# ANEXOS E DOCUMENTOS
# =============================================================================

class AnexoProjeto(models.Model):
    """Anexos e documentos do projeto"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        related_name='anexos',
        verbose_name="Projeto"
    )
    nome = models.CharField(max_length=100, verbose_name="Nome do Anexo")
    descricao = models.TextField(verbose_name="Descrição", blank=True)
    
    # Arquivo ou Link
    tipo = models.CharField(
        max_length=10,
        choices=[
            ('arquivo', 'Arquivo'),
            ('link', 'Link Externo'),
        ],
        default='arquivo',
        verbose_name="Tipo"
    )
    arquivo = models.FileField(
        upload_to='projetos/anexos/',
        blank=True,
        null=True,
        verbose_name="Arquivo"
    )
    link = models.URLField(
        blank=True,
        null=True,
        verbose_name="Link Externo"
    )
    
    # Categorização
    categoria = models.CharField(
        max_length=20,
        choices=[
            ('charter', 'Project Charter'),
            ('cronograma', 'Cronograma'),
            ('orcamento', 'Orçamento'),
            ('escopo', 'Escopo'),
            ('risco', 'Análise de Riscos'),
            ('comunicacao', 'Comunicação'),
            ('qualidade', 'Qualidade'),
            ('outro', 'Outro'),
        ],
        default='outro',
        verbose_name="Categoria"
    )
    
    # Controle de versão
    versao = models.CharField(
        max_length=10,
        default='1.0',
        verbose_name="Versão"
    )
    autor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Autor"
    )
    
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Anexo do Projeto"
        verbose_name_plural = "Anexos do Projeto"
        ordering = ['-atualizado_em']

    def __str__(self):
        return f"{self.projeto.codigo} - {self.nome}"

    def clean(self):
        """Validação para garantir arquivo OU link"""
        if self.tipo == 'arquivo' and not self.arquivo:
            raise ValidationError('Arquivo é obrigatório quando tipo é "Arquivo".')
        if self.tipo == 'link' and not self.link:
            raise ValidationError('Link é obrigatório quando tipo é "Link Externo".')

    def get_icone(self):
        """Retorna ícone baseado no tipo"""
        if self.tipo == 'link':
            return 'fa-solid fa-link'
        else:
            # Determinar ícone baseado na extensão do arquivo
            if self.arquivo:
                nome = self.arquivo.name.lower()
                if nome.endswith(('.pdf',)):
                    return 'fa-solid fa-file-pdf'
                elif nome.endswith(('.doc', '.docx')):
                    return 'fa-solid fa-file-word'
                elif nome.endswith(('.xls', '.xlsx')):
                    return 'fa-solid fa-file-excel'
                elif nome.endswith(('.ppt', '.pptx')):
                    return 'fa-solid fa-file-powerpoint'
                elif nome.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    return 'fa-solid fa-file-image'
            return 'fa-solid fa-file'

    def delete(self, *args, **kwargs):
        """Remove arquivo físico ao deletar o registro"""
        if self.arquivo:
            self.arquivo.delete(save=False)
        super().delete(*args, **kwargs)
