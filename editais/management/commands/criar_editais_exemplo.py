from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from datetime import datetime, timedelta
from editais.models import CategoriaEdital, AreaInteresse, Edital


class Command(BaseCommand):
    help = 'Cria dados de exemplo para editais'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Remove todos os editais existentes antes de criar novos',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Removendo editais existentes...')
            Edital.objects.all().delete()
            CategoriaEdital.objects.all().delete()
            AreaInteresse.objects.all().delete()

        # Criar categorias
        self.stdout.write('Criando categorias...')
        categorias = {
            'Inovação': 'Projetos focados em inovação tecnológica e social',
            'Sustentabilidade': 'Iniciativas ambientais e desenvolvimento sustentável',
            'Tecnologia': 'Soluções tecnológicas e digitais',
            'Empreendedorismo': 'Fomento ao empreendedorismo e startups',
            'Pesquisa': 'Projetos de pesquisa científica e desenvolvimento',
            'Educação': 'Iniciativas educacionais e de capacitação',
            'Saúde': 'Projetos relacionados à saúde e bem-estar',
            'Cultura': 'Projetos culturais e criativos',
        }

        categorias_obj = {}
        for nome, desc in categorias.items():
            # Usar get_or_create com tratamento de erro de integridade
            try:
                categoria, created = CategoriaEdital.objects.get_or_create(
                    nome=nome,
                    defaults={'descricao': desc}
                )
                if created:
                    self.stdout.write(f'  ✓ Categoria criada: {nome}')
                else:
                    self.stdout.write(f'  - Categoria já existe: {nome}')
            except Exception as e:
                # Se houver erro, tentar buscar por slug
                # Se falhar, usar apenas a primeira categoria como fallback
                if categorias_obj:
                    categoria = list(categorias_obj.values())[0]
                    self.stdout.write(f'  - Usando categoria fallback para {nome}: {categoria.nome}')
                else:
                    self.stdout.write(f'  ❌ Erro ao criar categoria {nome}: {e}')
                    continue
            categorias_obj[nome] = categoria

        # Criar áreas de interesse
        self.stdout.write('Criando áreas de interesse...')
        areas = [
            'Inteligência Artificial',
            'Internet das Coisas (IoT)',
            'Blockchain',
            'Energia Renovável',
            'Biotecnologia',
            'Agtech',
            'Fintech',
            'Healthtech',
            'Edtech',
            'Mobilidade Urbana',
            'Economia Circular',
            'Indústria 4.0',
            'Cidades Inteligentes',
            'Segurança Cibernética',
            'Realidade Virtual/Aumentada',
        ]

        areas_obj = []
        for area in areas:
            try:
                area_obj, created = AreaInteresse.objects.get_or_create(nome=area)
                if created:
                    self.stdout.write(f'  ✓ Área criada: {area}')
                else:
                    self.stdout.write(f'  - Área já existe: {area}')
            except Exception as e:
                # Se houver erro, tentar buscar por slug
                try:
                    slug = slugify(area)
                    area_obj = AreaInteresse.objects.get(slug=slug)
                    self.stdout.write(f'  - Área encontrada por slug: {area}')
                except AreaInteresse.DoesNotExist:
                    self.stdout.write(f'  ❌ Erro ao criar área {area}: {e}')
                    continue
            areas_obj.append(area_obj)

        # Criar editais de exemplo
        self.stdout.write('Criando editais de exemplo...')
        
        hoje = timezone.now().date()
        
        editais_data = [
            {
                'titulo': 'Programa de Inovação Tecnológica 2024',
                'numero_edital': 'PONTI-001/2024',
                'subtitulo': 'Fomento para projetos inovadores em tecnologia digital',
                'descricao_completa': 'Edital para fomento de projetos inovadores em tecnologia digital, com foco em soluções para smart cities e transformação digital.',
                'categoria': 'Inovação',
                'valor_premio': 1500000.00,
                'numero_desafios': 25,
                'data_abertura': hoje + timedelta(days=-30),
                'data_encerramento': hoje + timedelta(days=45),
                'status': 'aberto',
                'modalidade': 'fomento',
                'areas': ['Inteligência Artificial', 'Cidades Inteligentes', 'Internet das Coisas (IoT)'],
            },
            {
                'titulo': 'Chamada Pública para Sustentabilidade Ambiental',
                'numero_edital': 'PONTI-002/2024',
                'subtitulo': 'Projetos para sustentabilidade ambiental e economia circular',
                'descricao_completa': 'Edital destinado a projetos que promovam a sustentabilidade ambiental e economia circular na região.',
                'categoria': 'Inovação',
                'valor_premio': 800000.00,
                'numero_desafios': 15,
                'data_abertura': hoje + timedelta(days=-20),
                'data_encerramento': hoje + timedelta(days=30),
                'status': 'aberto',
                'modalidade': 'chamada_publica',
                'areas': ['Energia Renovável', 'Economia Circular', 'Biotecnologia'],
            },
            {
                'titulo': 'Edital de Empreendedorismo Jovem',
                'numero_edital': 'PONTI-003/2024',
                'subtitulo': 'Apoio a jovens empreendedores em tecnologia',
                'descricao_completa': 'Programa de apoio a jovens empreendedores com ideias inovadoras para o mercado de tecnologia.',
                'categoria': 'Inovação',
                'valor_premio': 500000.00,
                'numero_desafios': 30,
                'data_abertura': hoje + timedelta(days=10),
                'data_encerramento': hoje + timedelta(days=60),
                'status': 'em_breve',
                'modalidade': 'aceleracao',
                'areas': ['Fintech', 'Healthtech', 'Edtech'],
            },
            {
                'titulo': 'Pesquisa e Desenvolvimento em Agtech',
                'numero_edital': 'PONTI-004/2024',
                'subtitulo': 'Pesquisa em tecnologias para agricultura sustentável',
                'descricao_completa': 'Edital para projetos de pesquisa aplicada em tecnologias para agricultura sustentável e produtividade rural.',
                'categoria': 'Inovação',
                'valor_premio': 1200000.00,
                'numero_desafios': 12,
                'data_abertura': hoje + timedelta(days=-60),
                'data_encerramento': hoje + timedelta(days=-10),
                'status': 'encerrado',
                'modalidade': 'fomento',
                'areas': ['Agtech', 'Biotecnologia', 'Internet das Coisas (IoT)'],
            },
            {
                'titulo': 'Inovação em Saúde Digital',
                'numero_edital': 'PONTI-005/2024',
                'subtitulo': 'Soluções digitais inovadoras na área da saúde',
                'descricao_completa': 'Chamada para soluções digitais inovadoras na área da saúde, incluindo telemedicina e dispositivos médicos.',
                'categoria': 'Inovação',
                'valor_premio': 900000.00,
                'numero_desafios': 18,
                'data_abertura': hoje + timedelta(days=5),
                'data_encerramento': hoje + timedelta(days=50),
                'status': 'em_breve',
                'modalidade': 'fomento',
                'areas': ['Healthtech', 'Inteligência Artificial', 'Internet das Coisas (IoT)'],
            },
            {
                'titulo': 'Transformação Digital na Educação',
                'numero_edital': 'PONTI-006/2024',
                'subtitulo': 'Plataformas e ferramentas educacionais digitais',
                'descricao_completa': 'Edital para desenvolvimento de plataformas e ferramentas educacionais digitais inovadoras.',
                'categoria': 'Inovação',
                'valor_premio': 700000.00,
                'numero_desafios': 20,
                'data_abertura': hoje + timedelta(days=-15),
                'data_encerramento': hoje + timedelta(days=35),
                'status': 'aberto',
                'modalidade': 'fomento',
                'areas': ['Edtech', 'Inteligência Artificial', 'Realidade Virtual/Aumentada'],
            },
            {
                'titulo': 'Economia Criativa e Cultura Digital',
                'numero_edital': 'PONTI-007/2024',
                'subtitulo': 'Projetos culturais com tecnologia digital',
                'descricao_completa': 'Fomento a projetos culturais que utilizem tecnologia digital e promovam a economia criativa local.',
                'categoria': 'Inovação',
                'valor_premio': 400000.00,
                'numero_desafios': 22,
                'data_abertura': hoje + timedelta(days=15),
                'data_encerramento': hoje + timedelta(days=70),
                'status': 'em_breve',
                'modalidade': 'premio',
                'areas': ['Realidade Virtual/Aumentada', 'Blockchain', 'Edtech'],
            },
            {
                'titulo': 'Segurança Cibernética para PMEs',
                'numero_edital': 'PONTI-008/2024',
                'subtitulo': 'Soluções de segurança para pequenas e médias empresas',
                'descricao_completa': 'Programa de apoio ao desenvolvimento de soluções de segurança cibernética para pequenas e médias empresas.',
                'categoria': 'Inovação',
                'valor_premio': 600000.00,
                'numero_desafios': 16,
                'data_abertura': hoje + timedelta(days=-5),
                'data_encerramento': hoje + timedelta(days=40),
                'status': 'aberto',
                'modalidade': 'aceleracao',
                'areas': ['Segurança Cibernética', 'Inteligência Artificial', 'Blockchain'],
            },
        ]

        for edital_info in editais_data:
            areas_edital = edital_info.pop('areas')
            categoria_nome = edital_info.pop('categoria')
            
            # Usar a primeira categoria disponível se a solicitada não existir
            if categoria_nome in categorias_obj:
                edital_info['categoria'] = categorias_obj[categoria_nome]
            else:
                # Usar a primeira categoria disponível
                if categorias_obj:
                    edital_info['categoria'] = list(categorias_obj.values())[0]
                    self.stdout.write(f'  - Usando categoria fallback para edital: {edital_info["titulo"]}')
                else:
                    self.stdout.write(f'  ❌ Nenhuma categoria disponível para: {edital_info["titulo"]}')
                    continue
            
            try:
                edital = Edital.objects.get(titulo=edital_info['titulo'])
                self.stdout.write(f'  - Edital já existe: {edital.titulo}')
            except Edital.DoesNotExist:
                edital = Edital.objects.create(**edital_info)
                
                # Adicionar áreas de interesse
                for area_nome in areas_edital:
                    area_obj = next((a for a in areas_obj if a.nome == area_nome), None)
                    if area_obj:
                        edital.areas_interesse.add(area_obj)
                
                self.stdout.write(f'  ✓ Edital criado: {edital.titulo}')

        # Estatísticas finais
        total_editais = Edital.objects.count()
        editais_abertos = Edital.objects.filter(status='aberto').count()
        editais_em_breve = Edital.objects.filter(status='em_breve').count()
        editais_encerrados = Edital.objects.filter(status='encerrado').count()

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Dados de exemplo criados com sucesso!\n'
                f'📊 Estatísticas:\n'
                f'   • Total de editais: {total_editais}\n'
                f'   • Editais abertos: {editais_abertos}\n'
                f'   • Editais em breve: {editais_em_breve}\n'
                f'   • Editais encerrados: {editais_encerrados}\n'
                f'   • Categorias: {CategoriaEdital.objects.count()}\n'
                f'   • Áreas de interesse: {AreaInteresse.objects.count()}'
            )
        )