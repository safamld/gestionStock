#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script pour créer des utilisateurs de test pour agents et fournisseurs
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_stock.settings')
django.setup()

from django.contrib.auth.models import User, Group

print("\n" + "="*60)
print("CREATION DES UTILISATEURS DE TEST")
print("="*60)

# Utilisateurs à créer
test_users = [
    {
        'username': 'agent1',
        'email': 'agent1@example.com',
        'password': 'agent123',
        'first_name': 'Agent',
        'last_name': 'Test 1',
        'is_staff': False,
        'groups': ['Gestionnaire Stock']
    },
    {
        'username': 'agent2',
        'email': 'agent2@example.com',
        'password': 'agent123',
        'first_name': 'Agent',
        'last_name': 'Test 2',
        'is_staff': False,
        'groups': ['Responsable Commandes']
    },
    {
        'username': 'fournisseur1',
        'email': 'fournisseur1@example.com',
        'password': 'fournisseur123',
        'first_name': 'Fournisseur',
        'last_name': 'Test 1',
        'is_staff': False,
        'groups': ['Lecteur Stock']
    }
]

created_count = 0
skipped_count = 0

for user_data in test_users:
    username = user_data['username']
    
    # Vérifier si l'utilisateur existe déjà
    if User.objects.filter(username=username).exists():
        print("\n[SKIP] Utilisateur '{}' existe déjà".format(username))
        skipped_count += 1
        continue
    
    try:
        # Créer l'utilisateur
        user = User.objects.create_user(
            username=username,
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            is_staff=user_data['is_staff']
        )
        
        # Ajouter aux groupes
        for group_name in user_data['groups']:
            try:
                group = Group.objects.get(name=group_name)
                user.groups.add(group)
                print("\n[OK] Utilisateur '{}' créé et ajouté au groupe '{}'".format(username, group_name))
            except Group.DoesNotExist:
                print("\n[WARN] Groupe '{}' n'existe pas".format(group_name))
        
        created_count += 1
        
    except Exception as e:
        print("\n[ERROR] Erreur lors de la création de '{}': {}".format(username, str(e)))

print("\n" + "="*60)
print("RESULTAT DE LA CREATION")
print("="*60)
print("Utilisateurs créés: {}".format(created_count))
print("Utilisateurs ignorés (déjà existants): {}".format(skipped_count))

# Afficher tous les utilisateurs
print("\n" + "="*60)
print("TOUS LES UTILISATEURS")
print("="*60)

for user in User.objects.all():
    role = "ADMIN" if user.is_staff else "USER"
    groups = ', '.join([g.name for g in user.groups.all()]) if user.groups.exists() else "Aucun groupe"
    print("\n- Utilisateur: {}".format(user.username))
    print("  Email: {}".format(user.email))
    print("  Nom: {} {}".format(user.first_name, user.last_name))
    print("  Role: {}".format(role))
    print("  Groupes: {}".format(groups))

print("\n" + "="*60)
print("CREDENTIALS POUR TESTS")
print("="*60)
print("\nPour tester la connexion, utilisez:")
print("  URL: http://localhost:8000/login/")
print("  Admin: admin / admin")
print("  Agent 1: agent1 / agent123")
print("  Agent 2: agent2 / agent123")
print("  Fournisseur: fournisseur1 / fournisseur123")
print("\n" + "="*60 + "\n")
