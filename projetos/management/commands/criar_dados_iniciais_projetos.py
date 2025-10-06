from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from projetos.models import *
from datetime import date, timedelta
from decimal import Decimal

class Command(BaseCommand):
    help = 'Cria dados iniciais para o sistema de projetos'

    def handle(self, *args, **options):
        self.stdout.write('Criando dados iniciais para o sistema de projetos...')

        # Criar usuário admin se não existir
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@ponti.com',
                'first_name': 'Administrador',
                'last_name': 'Sistema',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Usuário admin criado'))

        # Criar usuários de teste
        usuarios = [
            {'username': 'gerente1', 'first_name': 'João', 'last_name': 'Silva', 'email': 'joao@ponti.com'},
            {'username': 'gerente2', 'first_name': 'Maria', 'last_name': 'Santos', 'email': 'maria@ponti.com'},
            {'username': 'patrocinador1', 'first_name': 'Carlos', 'last_name': 'Oliveira', 'email': 'carlos@ponti.com'},
            {'username': 'analista1', 'first_name': 'Ana', 'last_name': 'Costa', 'email': 'ana@ponti.com'},
        ]

        for user_data in usuarios:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults=user_data
            )
            if created:
                user.set_password('123456')
                user.save()

        # Categorias Estratégicas
        categorias = [
            {
                'nome': 'Inovação Tecnológica',
                'descricao': 'Projetos focados em desenvolvimento de novas tecnologias',
                'cor': '#007bff',
                'peso_estrategico': 9,
                'icone': 'fa-solid fa-microchip'
            },
            {
                'nome': 'Transformação Digital',
                'descricao': 'Iniciativas de digitalização e modernização',
                'cor': '#28a745',
                'peso_estrategico': 8,
                'icone': 'fa-solid fa-digital-tachograph'
            },
            {
                'nome': 'Sustentabilidade',
                'descricao': 'Projetos voltados para sustentabilidade ambiental',
                'cor': '#20c997',
                'peso_estrategico': 7,
                'icone': 'fa-solid fa-leaf'
            },
        ]

        for cat_data in categorias:
            categoria, created = CategoriaEstrategica.objects.get_or_create(
                nome=cat_data['nome'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'Categoria criada: {categoria.nome}')

        # Tipos de Projeto
        tipos = [
            {
                'nome': 'Desenvolvimento de Software',
                'descricao': 'Projetos de desenvolvimento de sistemas e aplicações',
                'prefixo': 'DEV',
                'metodologia_sugerida': 'agil'
            },
            {
                'nome': 'Infraestrutura',
                'descricao': 'Projetos de infraestrutura tecnológica',
                'prefixo': 'INF',
                'metodologia_sugerida': 'tradicional'
            },
            {
                'nome': 'Pesquisa e Desenvolvimento',
                'descricao': 'Projetos de P&D e inovação',
                'prefixo': 'PD',
                'metodologia_sugerida': 'lean'
            },
        ]

        for tipo_data in tipos:
            tipo, created = TipoProjeto.objects.get_or_create(
                nome=tipo_data['nome'],
                defaults=tipo_data
            )
            if created:
                self.stdout.write(f'Tipo de projeto criado: {tipo.nome}')

        # Unidades Organizacionais
        unidades = [
            {
                'nome': 'Secretaria de Ciência e Tecnologia',
                'sigla': 'SECTIDE',
                'descricao': 'Secretaria Municipal de Ciência, Tecnologia, Inovação e Desenvolvimento Econômico',
                'responsavel': admin_user
            },
            {
                'nome': 'Hub de Inovação',
                'sigla': 'PONTI',
                'descricao': 'Hub de Inovação da SECTIDE',
                'responsavel': User.objects.get(username='gerente1')
            },
        ]

        sectide = None
        for unidade_data in unidades:
            unidade, created = UnidadeOrganizacional.objects.get_or_create(
                sigla=unidade_data['sigla'],
                defaults=unidade_data
            )
            if created:
                self.stdout.write(f'Unidade criada: {unidade.nome}')
            if unidade.sigla == 'SECTIDE':
                sectide = unidade

        # Atualizar PONTI como filha da SECTIDE
        ponti = UnidadeOrganizacional.objects.get(sigla='PONTI')
        ponti.unidade_pai = sectide
        ponti.save()

        # Portfólios
        hoje = date.today()
        categoria_inovacao = CategoriaEstrategica.objects.get(nome='Inovação Tecnológica')
        categoria_digital = CategoriaEstrategica.objects.get(nome='Transformação Digital')

        portfolios_data = [
            {
                'nome': 'Ecossistema de Inovação',
                'codigo': 'PORT-001',
                'descricao': 'Portfólio focado no desenvolvimento do ecossistema de inovação local',
                'gestor_portfolio': User.objects.get(username='gerente1'),
                'patrocinador': User.objects.get(username='patrocinador1'),
                'unidade_organizacional': ponti,
                'categoria_estrategica': categoria_inovacao,
                'orcamento_total': Decimal('500000.00'),
                'data_inicio': hoje,
                'data_fim_prevista': hoje + timedelta(days=365),
                'status': 'em_execucao',
                'prioridade': 'muito_alta'
            },
            {
                'nome': 'Transformação Digital Municipal',
                'codigo': 'PORT-002',
                'descricao': 'Portfólio de digitalização dos serviços municipais',
                'gestor_portfolio': User.objects.get(username='gerente2'),
                'patrocinador': User.objects.get(username='patrocinador1'),
                'unidade_organizacional': sectide,
                'categoria_estrategica': categoria_digital,
                'orcamento_total': Decimal('750000.00'),
                'data_inicio': hoje - timedelta(days=30),
                'data_fim_prevista': hoje + timedelta(days=540),
                'status': 'em_execucao',
                'prioridade': 'alta'
            }
        ]

        portfolios_criados = []
        for port_data in portfolios_data:
            portfolio, created = Portfolio.objects.get_or_create(
                codigo=port_data['codigo'],
                defaults=port_data
            )
            if created:
                self.stdout.write(f'Portfólio criado: {portfolio.nome}')
            portfolios_criados.append(portfolio)

        # Programas
        portfolio_inovacao = portfolios_criados[0]
        portfolio_digital = portfolios_criados[1]

        programas_data = [
            {
                'nome': 'Aceleração de Startups',
                'codigo': 'PROG-001',
                'descricao': 'Programa de aceleração para startups locais',
                'portfolio': portfolio_inovacao,
                'gerente_programa': User.objects.get(username='gerente1'),
                'objetivos': 'Acelerar o crescimento de startups de base tecnológica em Nova Friburgo',
                'beneficios_esperados': 'Geração de empregos qualificados e aumento da competitividade regional',
                'orcamento_total': Decimal('200000.00'),
                'data_inicio': hoje,
                'data_fim_prevista': hoje + timedelta(days=180),
                'status': 'em_execucao',
                'prioridade': 'alta'
            },
            {
                'nome': 'Governo Digital',
                'codigo': 'PROG-002',
                'descricao': 'Programa de digitalização dos serviços públicos',
                'portfolio': portfolio_digital,
                'gerente_programa': User.objects.get(username='gerente2'),
                'objetivos': 'Digitalizar 80% dos serviços públicos municipais',
                'beneficios_esperados': 'Melhoria da eficiência e satisfação dos cidadãos',
                'orcamento_total': Decimal('300000.00'),
                'data_inicio': hoje - timedelta(days=15),
                'data_fim_prevista': hoje + timedelta(days=270),
                'status': 'em_execucao',
                'prioridade': 'muito_alta'
            }
        ]

        programas_criados = []
        for prog_data in programas_data:
            programa, created = Programa.objects.get_or_create(
                codigo=prog_data['codigo'],
                defaults=prog_data
            )
            if created:
                self.stdout.write(f'Programa criado: {programa.nome}')
            programas_criados.append(programa)

        # Projetos
        programa_startups = programas_criados[0]
        programa_governo = programas_criados[1]
        tipo_dev = TipoProjeto.objects.get(prefixo='DEV')
        tipo_inf = TipoProjeto.objects.get(prefixo='INF')

        projetos_data = [
            {
                'nome': 'Plataforma de Conexão Startups',
                'codigo': 'DEV-001',
                'descricao': 'Desenvolvimento de plataforma web para conectar startups, investidores e mentores',
                'portfolio': portfolio_inovacao,
                'programa': programa_startups,
                'tipo_projeto': tipo_dev,
                'gerente_projeto': User.objects.get(username='analista1'),
                'patrocinador': User.objects.get(username='gerente1'),
                'objetivos': 'Criar uma plataforma digital que facilite a conexão entre os atores do ecossistema',
                'escopo_produto': 'Sistema web responsivo com funcionalidades de matching e networking',
                'escopo_trabalho': 'Levantamento de requisitos, desenvolvimento, testes e implantação',
                'orcamento_total': Decimal('80000.00'),
                'orcamento_consumido': Decimal('25000.00'),
                'data_inicio_prevista': hoje + timedelta(days=7),
                'data_inicio_real': hoje + timedelta(days=10),
                'data_fim_prevista': hoje + timedelta(days=120),
                'percentual_conclusao': 35,
                'status': 'em_execucao',
                'prioridade': 'alta',
                'metodologia': 'agil'
            },
            {
                'nome': 'Portal do Cidadão',
                'codigo': 'DEV-002',
                'descricao': 'Portal único para acesso aos serviços digitais municipais',
                'portfolio': portfolio_digital,
                'programa': programa_governo,
                'tipo_projeto': tipo_dev,
                'gerente_projeto': User.objects.get(username='gerente2'),
                'patrocinador': User.objects.get(username='patrocinador1'),
                'objetivos': 'Centralizar o acesso aos serviços digitais municipais',
                'escopo_produto': 'Portal web com integração aos sistemas municipais existentes',
                'escopo_trabalho': 'Análise, desenvolvimento, integração e treinamento',
                'orcamento_total': Decimal('120000.00'),
                'orcamento_consumido': Decimal('60000.00'),
                'data_inicio_prevista': hoje - timedelta(days=30),
                'data_inicio_real': hoje - timedelta(days=25),
                'data_fim_prevista': hoje + timedelta(days=90),
                'percentual_conclusao': 55,
                'status': 'em_execucao',
                'prioridade': 'muito_alta',
                'metodologia': 'tradicional'
            },
            {
                'nome': 'Infraestrutura Cloud',
                'codigo': 'INF-001',
                'descricao': 'Implementação de infraestrutura em nuvem para os sistemas municipais',
                'portfolio': portfolio_digital,
                'tipo_projeto': tipo_inf,
                'gerente_projeto': User.objects.get(username='analista1'),
                'patrocinador': User.objects.get(username='gerente2'),
                'objetivos': 'Modernizar a infraestrutura tecnológica municipal',
                'escopo_produto': 'Ambiente cloud com alta disponibilidade e segurança',
                'escopo_trabalho': 'Planejamento, migração, configuração e monitoramento',
                'orcamento_total': Decimal('150000.00'),
                'orcamento_consumido': Decimal('15000.00'),
                'data_inicio_prevista': hoje + timedelta(days=30),
                'data_fim_prevista': hoje + timedelta(days=180),
                'percentual_conclusao': 10,
                'status': 'em_planejamento',
                'prioridade': 'media',
                'metodologia': 'tradicional'
            }
        ]

        for proj_data in projetos_data:
            projeto, created = Projeto.objects.get_or_create(
                codigo=proj_data['codigo'],
                defaults=proj_data
            )
            if created:
                self.stdout.write(f'Projeto criado: {projeto.nome}')

                # Adicionar equipe ao projeto
                EquipeProjeto.objects.create(
                    projeto=projeto,
                    membro=projeto.gerente_projeto,
                    papel='gerente',
                    responsabilidades='Gerenciamento geral do projeto',
                    dedicacao_percentual=80,
                    data_entrada=projeto.data_inicio_real or projeto.data_inicio_prevista
                )

                # Adicionar algumas fases básicas
                fases = [
                    {'nome': 'Iniciação', 'ordem': 1, 'percentual': 100 if projeto.percentual_conclusao > 20 else 50},
                    {'nome': 'Planejamento', 'ordem': 2, 'percentual': 100 if projeto.percentual_conclusao > 40 else 30},
                    {'nome': 'Execução', 'ordem': 3, 'percentual': max(0, projeto.percentual_conclusao - 60)},
                    {'nome': 'Encerramento', 'ordem': 4, 'percentual': max(0, projeto.percentual_conclusao - 90)},
                ]

                for fase_data in fases:
                    FaseProjeto.objects.create(
                        projeto=projeto,
                        nome=fase_data['nome'],
                        ordem=fase_data['ordem'],
                        data_inicio_prevista=projeto.data_inicio_prevista + timedelta(days=(fase_data['ordem']-1)*30),
                        data_fim_prevista=projeto.data_inicio_prevista + timedelta(days=fase_data['ordem']*30),
                        percentual_conclusao=fase_data['percentual'],
                        status='concluido' if fase_data['percentual'] == 100 else 'em_execucao' if fase_data['percentual'] > 0 else 'nao_iniciado'
                    )

        self.stdout.write(self.style.SUCCESS('Dados iniciais criados com sucesso!'))
        self.stdout.write(self.style.WARNING('Usuários criados:'))
        self.stdout.write('- admin / admin123 (superusuário)')
        self.stdout.write('- gerente1 / 123456')
        self.stdout.write('- gerente2 / 123456')
        self.stdout.write('- patrocinador1 / 123456')
        self.stdout.write('- analista1 / 123456')