#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_stock.settings')
django.setup()

from stock.models import Fournisseur

print("=== VÉRIFIER LE DERNIER FOURNISSEUR CRÉÉ ===\n")
try:
    fournisseur = Fournisseur.objects.latest('date_creation')
    print(f"Nom: {fournisseur.nom_fournisseur}")
    print(f"Code: {fournisseur.code_fournisseur}")
    print(f"Mot de passe en BD: '{fournisseur.mot_de_passe}'")
    print(f"Type mot_de_passe: {type(fournisseur.mot_de_passe)}")
    print(f"Longueur: {len(fournisseur.mot_de_passe) if fournisseur.mot_de_passe else 0}")
    print(f"Email: {fournisseur.email}")
    print(f"Téléphone: {fournisseur.telephone}")
    print(f"Statut: {fournisseur.statut}")
    print(f"Date création: {fournisseur.date_creation}")
except Exception as e:
    print(f"Erreur: {e}")
