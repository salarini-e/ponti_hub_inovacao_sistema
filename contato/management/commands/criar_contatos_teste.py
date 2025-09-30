from django.core.management.base import BaseCommand
from contato.models import Contato


class Command(BaseCommand):
    help = 'Cria contatos de teste para demonstração'

    def add_arguments(self, parser):
        parser.add_argument(
            '--quantidade',
            type=int,
            default=5,
            help='Quantidade de contatos de teste a criar'
        )

    def handle(self, *args, **options):
        quantidade = options['quantidade']
        
        contatos_teste = [
            {
                'nome': 'João Silva',
                'email': 'joao.silva@email.com',
                'telefone': '(22) 99999-1234',
                'assunto': 'projeto',
                'mensagem': 'Gostaria de apresentar uma proposta de projeto inovador para a cidade de Nova Friburgo. Temos uma startup focada em IoT para agricultura sustentável.'
            },
            {
                'nome': 'Maria Santos',
                'email': 'maria.santos@empresa.com.br',
                'telefone': '(22) 98888-5678',
                'assunto': 'parceria',
                'mensagem': 'Nossa empresa está interessada em estabelecer uma parceria com o PONTI para desenvolvimento de soluções tecnológicas para o setor público.'
            },
            {
                'nome': 'Pedro Oliveira',
                'email': 'pedro@startup.com',
                'telefone': '',
                'assunto': 'startup',
                'mensagem': 'Somos uma startup de fintech e gostaríamos de participar dos programas de aceleração do PONTI. Como podemos nos inscrever?'
            },
            {
                'nome': 'Ana Costa',
                'email': 'ana.costa@gmail.com',
                'telefone': '(22) 97777-9999',
                'assunto': 'tecnologia',
                'mensagem': 'Tenho interesse em conhecer mais sobre as iniciativas de transformação digital que estão sendo implementadas na cidade.'
            },
            {
                'nome': 'Carlos Ferreira',
                'email': 'carlos.ferreira@universidade.edu.br',
                'telefone': '(22) 96666-3333',
                'assunto': 'geral',
                'mensagem': 'Sou professor universitário e gostaria de estabelecer uma colaboração acadêmica com o PONTI para projetos de pesquisa e desenvolvimento.'
            }
        ]
        
        contatos_criados = 0
        
        for i in range(quantidade):
            dados = contatos_teste[i % len(contatos_teste)]
            
            # Modificar dados para evitar duplicatas
            if i >= len(contatos_teste):
                dados['nome'] = f"{dados['nome']} {i+1}"
                dados['email'] = f"teste{i+1}@{dados['email'].split('@')[1]}"
            
            contato = Contato.objects.create(**dados)
            contatos_criados += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'Contato criado: {contato.nome} ({contato.email})')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nTotal de {contatos_criados} contatos de teste criados com sucesso!')
        )