"""
Migration: Associer les Users Django aux Fournisseurs existants
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_stock.settings')
django.setup()

from stock.models import Fournisseur
from django.contrib.auth.models import User, Group

print("\n" + "="*80)
print("MIGRATION: Associer Users aux Fournisseurs")
print("="*80 + "\n")

fournisseur_group, _ = Group.objects.get_or_create(name='Fournisseur')
created_users = 0
linked_users = 0

for fournisseur in Fournisseur.objects.all():
    if not fournisseur.user:
        # Créer un User pour ce fournisseur
        email = fournisseur.email if fournisseur.email else f"{fournisseur.code_fournisseur}@example.com"
        username = fournisseur.code_fournisseur.lower()
        
        # Vérifier que le username est unique
        if User.objects.filter(username=username).exists():
            counter = 1
            original_username = username
            while User.objects.filter(username=username).exists():
                username = f"{original_username}{counter}"
                counter += 1
        
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=fournisseur.nom_fournisseur,
            password='TempPassword123!',  # Mot de passe temporaire
            is_active=True
        )
        
        # Ajouter au groupe Fournisseur
        user.groups.add(fournisseur_group)
        
        # Associer au fournisseur
        fournisseur.user = user
        fournisseur.save()
        
        print(f"✓ Créé User: {username} ({email}) pour {fournisseur.nom_fournisseur}")
        created_users += 1
        linked_users += 1
    else:
        # Vérifier que l'utilisateur est dans le groupe
        if not fournisseur.user.groups.filter(name='Fournisseur').exists():
            fournisseur.user.groups.add(fournisseur_group)
            print(f"✓ Ajouté groupe Fournisseur à: {fournisseur.user.username}")
            linked_users += 1

print(f"\n" + "="*80)
print(f"Résumé: {created_users} Users créés, {linked_users} associés au groupe Fournisseur")
print("="*80 + "\n")

print("⚠️  IMPORTANT: Les Users créés ont un mot de passe temporaire!")
print("   Les fournisseurs doivent changer leur mot de passe via l'admin.\n")
