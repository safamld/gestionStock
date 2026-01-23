#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_stock.settings')
django.setup()

from django.contrib.auth.models import User, Group
from stock.models import Fournisseur

# Créer le groupe Fournisseur s'il n'existe pas
group, created = Group.objects.get_or_create(name='Fournisseur')
if created:
    print("✅ Groupe 'Fournisseur' créé")
else:
    print("ℹ️  Groupe 'Fournisseur' existe déjà")

# Créer un utilisateur fournisseur test
username = 'fournisseur_test'
try:
    user = User.objects.create_user(
        username=username,
        password='fournisseur123',
        email='fournisseur@test.com',
        first_name='Test',
        last_name='Fournisseur'
    )
    user.groups.add(group)
    print(f"\n✅ Utilisateur '{username}' créé")
    
    # Créer le fournisseur associé
    fournisseur = Fournisseur.objects.create(
        code_fournisseur='fournitest',
        nom_fournisseur='Fournisseur Test',
        email='fournisseur@test.com',
        telephone='+33612345678',
        user=user
    )
    print(f"✅ Fournisseur '{fournisseur.nom_fournisseur}' créé et lié à l'utilisateur")
    print(f"\n📝 Identifiants de connexion:")
    print(f"   Utilisateur: {username}")
    print(f"   Mot de passe: fournisseur123")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
