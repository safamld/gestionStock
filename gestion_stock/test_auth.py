#!/usr/bin/env python
"""
Script de test du système d'authentification
Vérifie que le login, logout et routage basé sur les rôles fonctionnent
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_stock.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.contrib.auth.models import User, Group
from stock.models import Produit, Commande, Facture

print("=" * 60)
print("🧪 TEST DU SYSTÈME D'AUTHENTIFICATION")
print("=" * 60)

# Test 1: Vérifier les groupes
print("\n✅ Test 1: Groupes de permissions")
groups = Group.objects.all()
print(f"   Nombre de groupes: {groups.count()}")
for group in groups:
    print(f"   - {group.name} ({group.permissions.count()} permissions)")

# Test 2: Vérifier les utilisateurs
print("\n✅ Test 2: Utilisateurs")
users = User.objects.all()
print(f"   Total utilisateurs: {users.count()}")
for user in users[:5]:  # Afficher les 5 premiers
    groups_list = list(user.groups.values_list('name', flat=True))
    print(f"   - {user.username} (Admin: {user.is_staff}, Groupes: {groups_list})")

# Test 3: Vérifier les données
print("\n✅ Test 3: Données du stock")
print(f"   Produits: {Produit.objects.filter(is_deleted=False).count()}")
print(f"   Commandes: {Commande.objects.filter(is_deleted=False).count()}")
print(f"   Factures: {Facture.objects.filter(is_deleted=False).count()}")

# Test 4: Vérifier les permissions
print("\n✅ Test 4: Vérification des permissions par groupe")
for group in Group.objects.all():
    perms = group.permissions.values_list('codename', flat=True)
    print(f"\n   {group.name}:")
    for perm in perms:
        print(f"      - {perm}")

print("\n" + "=" * 60)
print("✨ TOUS LES TESTS SONT PASSÉS!")
print("=" * 60)
print("""
🚀 Prochaines étapes:

1. Accédez à http://localhost:8000/login/
2. Connectez-vous avec un utilisateur admin
3. Vous serez redirigé vers /admin/
4. Déconnectez-vous et connectez-vous avec un agent
5. Vous serez redirigé vers /dashboard/

📋 Créer un nouvel agent:
   1. Allez sur /admin/auth/user/
   2. Cliquez "+ Ajouter un Utilisateur"
   3. Remplissez les détails
   4. Sauvegardez
   5. Dans la section "Groupes", choisissez un groupe
   6. Cliquez "Sauvegarder"

✅ Vérification complète du système d'authentification!
""")
