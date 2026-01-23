#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_stock.settings')
django.setup()

from stock.models import Fournisseur

# Créer un fournisseur de test
try:
    fournisseur = Fournisseur.objects.create(
        code_fournisseur='test_supplier',
        nom_fournisseur='Test Supplier',
        email='test@supplier.com',
        telephone='+33612345678',
        mot_de_passe='password123'
    )
    print(f"✅ Fournisseur créé avec succès!")
    print(f"Nom: {fournisseur.nom_fournisseur}")
    print(f"Mot de passe: {fournisseur.mot_de_passe}")
except Exception as e:
    print(f"❌ Erreur: {e}")
