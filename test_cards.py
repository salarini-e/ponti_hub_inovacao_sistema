#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ponti_hub_inovacao.settings')
django.setup()

from core.models import CardQuemSomos

print('Cards existentes:', CardQuemSomos.objects.count())
for card in CardQuemSomos.objects.all():
    print(f'ID: {card.id}, Título: {card.titulo}')