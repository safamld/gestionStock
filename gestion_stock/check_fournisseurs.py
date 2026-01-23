#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_stock.settings')
django.setup()

from stock.models import Fournisseur

print("=== FOURNISSEURS EXISTANTS ===")
fournisseurs = Fournisseur.objects.all()
if fournisseurs.exists():
    for f in fournisseurs:
        print(f"\nCode: {f.code_fournisseur}")
        print(f"Nom: {f.nom_fournisseur}")
        print(f"Mot de Passe: {f.mot_de_passe if f.mot_de_passe else 'VIDE'}")
        print(f"Email: {f.email}")
        print(f"Téléphone: {f.telephone}")
else:
    print("Aucun fournisseur trouvé!")
