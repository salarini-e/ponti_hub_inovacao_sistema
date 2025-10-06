from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import date, timedelta
from projetos.models import *

class Command(BaseCommand):
    help = 'Cria dados iniciais para o sistema de gestão de projetos'

    def handle(self, *args, **options):
        self.stdout.write('Criando dados iniciais do sistema de projetos...')
        
        # Criar usuários se não existirem
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'Administrador',
                'last_name': 'Sistema',
                'email': 'admin@ponti.com.br',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(f'✓ Usuário administrador criado: admin/admin123')
        
        # Criar gerentes
        gerente1, created = User.objects.get_or_create(
            username='joao.silva',
            defaults={
                'first_name': 'João',
                'last_name': 'Silva',
                'email': 'joao.silva@ponti.com.br',
                'is_staff': True,
            }
        )
        
        gerente2, created = User.objects.get_or_create(
            username='maria.santos',
            defaults={
                'first_name': 'Maria',
                'last_name': 'Santos',
                'email': 'maria.santos@ponti.com.br',
                'is_staff': True,
            }
        )
        
        # Criar categorias estratégicas
        categoria_inovacao, created = CategoriaEstrategica.objects.get_or_create(
            nome='Inovação Tecnológica',
            defaults={
                'descricao': 'Projetos focados em inovação e desenvolvimento tecnológico',
                'cor': '#1e40af',
                'icone': 'fa-solid fa-lightbulb',
                'peso_estrategico': 10,
            }
        )
        
        categoria_infraestrutura, created = CategoriaEstrategica.objects.get_or_create(
            nome='Infraestrutura',
            defaults={
                'descricao': 'Projetos de melhoria de infraestrutura e processos',
                'cor': '#059669',
                'icone': 'fa-solid fa-building',
                'peso_estrategico': 8,
            }
        )
        
        categoria_capacitacao, created = CategoriaEstrategica.objects.get_or_create(
            nome='Capacitação',
            defaults={
                'descricao': 'Projetos de capacitação e desenvolvimento humano',
                'cor': '#dc2626',
                'icone': 'fa-solid fa-graduation-cap',
                'peso_estrategico': 7,
            }
        )
        
        # Criar tipos de projeto
        tipo_software, created = TipoProjeto.objects.get_or_create(
            nome='Desenvolvimento de Software',
            defaults={
                'descricao': 'Projetos de desenvolvimento de sistemas e aplicações',
                'prefixo': 'SW',
                'metodologia_sugerida': 'agil',
            }
        )
        
        tipo_infraestrutura, created = TipoProjeto.objects.get_or_create(
            nome='Infraestrutura',
            defaults={
                'descricao': 'Projetos de infraestrutura física e tecnológica',
                'prefixo': 'INF',
                'metodologia_sugerida': 'tradicional',
            }
        )
        
        tipo_capacitacao, created = TipoProjeto.objects.get_or_create(
            nome='Capacitação',
            defaults={
                'descricao': 'Projetos de treinamento e capacitação',
                'prefixo': 'CAP',
                'metodologia_sugerida': 'hibrido',
            }
        )
        
        # Criar unidade organizacional
        unidade_ponti, created = UnidadeOrganizacional.objects.get_or_create(
            nome='PONTI - Hub de Inovação',
            defaults={
                'sigla': 'PONTI',
                'descricao': 'Hub de Inovação da SECTIDE Nova Friburgo',
                'responsavel': admin_user,
            }
        )
        
        # Criar portfólio
        portfolio_inovacao, created = Portfolio.objects.get_or_create(
            codigo='PF-INOV-2024',
            defaults={
                'nome': 'Portfólio de Inovação 2024',
                'descricao': 'Portfólio focado em projetos de inovação tecnológica e transformação digital para Nova Friburgo',
                'gestor_portfolio': admin_user,
                'patrocinador': admin_user,
                'unidade_organizacional': unidade_ponti,
                'categoria_estrategica': categoria_inovacao,
                'orcamento_total': 500000.00,
                'data_inicio': date.today(),
                'data_fim_prevista': date.today() + timedelta(days=365),
                'status': StatusChoices.EM_EXECUCAO,
                'prioridade': PrioridadeChoices.ALTA,
            }
        )
        
        # Criar programa
        programa_digital, created = Programa.objects.get_or_create(
            codigo='PG-DIGITAL-2024',
            defaults={
                'nome': 'Programa de Transformação Digital',
                'descricao': 'Programa para digitalização de processos e serviços da SECTIDE',
                'portfolio': portfolio_inovacao,
                'gerente_programa': gerente1,
                'objetivos': 'Modernizar processos, melhorar atendimento ao cidadão e aumentar eficiência operacional',
                'beneficios_esperados': 'Redução de tempo de atendimento, maior transparência e melhoria na qualidade dos serviços',
                'orcamento_total': 200000.00,
                'data_inicio': date.today(),
                'data_fim_prevista': date.today() + timedelta(days=270),
                'status': StatusChoices.EM_EXECUCAO,
                'prioridade': PrioridadeChoices.ALTA,
            }
        )
        
        # Criar projetos
        projeto1, created = Projeto.objects.get_or_create(
            codigo='SW-PORTAL-2024',
            defaults={
                'nome': 'Portal de Inovação PONTI',
                'descricao': 'Desenvolvimento de portal web para divulgação de projetos e serviços da PONTI',
                'portfolio': portfolio_inovacao,
                'programa': programa_digital,
                'tipo_projeto': tipo_software,
                'gerente_projeto': gerente1,
                'patrocinador': admin_user,
                'objetivos': 'Criar plataforma digital para divulgação e gestão de projetos de inovação',
                'escopo_produto': 'Portal web responsivo com funcionalidades de cadastro de projetos, editais e eventos',
                'escopo_trabalho': 'Análise, design, desenvolvimento, testes e implantação do portal',
                'premissas': 'Equipe técnica disponível, infraestrutura de hospedagem definida',
                'restricoes': 'Orçamento limitado, prazo de 6 meses',
                'orcamento_total': 80000.00,
                'orcamento_consumido': 25000.00,
                'data_inicio_prevista': date.today(),
                'data_inicio_real': date.today(),
                'data_fim_prevista': date.today() + timedelta(days=180),
                'percentual_conclusao': 35,
                'status': StatusChoices.EM_EXECUCAO,
                'prioridade': PrioridadeChoices.ALTA,
                'metodologia': 'agil',
            }
        )
        
        projeto2, created = Projeto.objects.get_or_create(
            codigo='SW-GESTAO-2024',
            defaults={
                'nome': 'Sistema de Gestão de Projetos',
                'descricao': 'Sistema para gestão completa de projetos, programas e portfólios',
                'portfolio': portfolio_inovacao,
                'programa': programa_digital,
                'tipo_projeto': tipo_software,
                'gerente_projeto': gerente2,
                'patrocinador': admin_user,
                'objetivos': 'Implementar sistema completo de gestão de projetos seguindo metodologias PMI',
                'escopo_produto': 'Sistema web com funcionalidades completas de gestão de PPP',
                'escopo_trabalho': 'Modelagem, desenvolvimento, testes e implantação do sistema',
                'premissas': 'Metodologia PMI como base, integração com sistemas existentes',
                'restricoes': 'Conformidade com LGPD, segurança da informação',
                'orcamento_total': 120000.00,
                'orcamento_consumido': 15000.00,
                'data_inicio_prevista': date.today() + timedelta(days=30),
                'data_fim_prevista': date.today() + timedelta(days=210),
                'percentual_conclusao': 15,
                'status': StatusChoices.EM_PLANEJAMENTO,
                'prioridade': PrioridadeChoices.MUITO_ALTA,
                'metodologia': 'hibrido',
            }
        )
        
        projeto3, created = Projeto.objects.get_or_create(
            codigo='CAP-GESTORES-2024',
            defaults={
                'nome': 'Capacitação em Gestão de Projetos',
                'descricao': 'Programa de capacitação para gestores públicos em metodologias de gestão de projetos',
                'portfolio': portfolio_inovacao,
                'tipo_projeto': tipo_capacitacao,
                'gerente_projeto': gerente1,
                'patrocinador': admin_user,
                'objetivos': 'Capacitar servidores em gestão de projetos seguindo padrões PMI',
                'escopo_produto': 'Curso completo de gestão de projetos com certificação',
                'escopo_trabalho': 'Desenvolvimento de conteúdo, ministração de aulas e avaliações',
                'premissas': 'Instrutores qualificados, sala de treinamento disponível',
                'restricoes': 'Disponibilidade dos servidores, agenda de treinamentos',
                'orcamento_total': 50000.00,
                'orcamento_consumido': 5000.00,
                'data_inicio_prevista': date.today() + timedelta(days=60),
                'data_fim_prevista': date.today() + timedelta(days=150),
                'percentual_conclusao': 10,
                'status': StatusChoices.NAO_INICIADO,
                'prioridade': PrioridadeChoices.MEDIA,
                'metodologia': 'tradicional',
            }
        )
        
        self.stdout.write('✓ Dados básicos criados com sucesso!')
        
        # Criar algumas entregas
        if projeto1:
            Entrega.objects.get_or_create(
                projeto=projeto1,
                nome='Protótipo do Portal',
                defaults={
                    'descricao': 'Protótipo navegável das principais funcionalidades',
                    'tipo': 'prototipo',
                    'responsavel': gerente1,
                    'data_prevista': date.today() + timedelta(days=30),
                    'status': 'em_desenvolvimento',
                    'criterios_aceitacao': 'Navegação funcional, design aprovado, principais telas implementadas',
                }
            )
            
            Entrega.objects.get_or_create(
                projeto=projeto1,
                nome='Documentação Técnica',
                defaults={
                    'descricao': 'Documentação completa da arquitetura e funcionalidades',
                    'tipo': 'documento',
                    'responsavel': gerente1,
                    'data_prevista': date.today() + timedelta(days=90),
                    'status': 'nao_iniciado',
                    'criterios_aceitacao': 'Documentação de arquitetura, manual de usuário, manual técnico',
                }
            )
        
        # Criar alguns riscos
        if projeto2:
            RiscoProjeto.objects.get_or_create(
                projeto=projeto2,
                titulo='Atraso na Definição de Requisitos',
                defaults={
                    'descricao': 'Possível atraso na definição completa dos requisitos do sistema',
                    'categoria': TipoRiscoChoices.CRONOGRAMA,
                    'probabilidade': ProbabilidadeChoices.MEDIA,
                    'impacto': ImpactoChoices.ALTO,
                    'estrategia_resposta': 'mitigar',
                    'plano_resposta': 'Reuniões semanais com stakeholders, prototipagem iterativa',
                    'responsavel': gerente2,
                    'data_identificacao': date.today(),
                    'status': 'em_tratamento',
                }
            )
        
        self.stdout.write('✓ Entregas e riscos de exemplo criados!')
        
        self.stdout.write(
            self.style.SUCCESS(
                'Dados iniciais criados com sucesso!\n'
                'Acesse /projetos/ para ver o dashboard.\n'
                'Use admin/admin123 para acessar a administração.'
            )
        )