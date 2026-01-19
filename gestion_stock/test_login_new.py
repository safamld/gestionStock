#!/usr/bin/env python
"""
Test script pour vérifier le nouveau flux de connexion
avec le template login_blank.html et redirection vers produit_list
"""

import os
import sys
import django

# Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_stock.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client

# Créer un client de test
client = Client()

print("=" * 60)
print("🧪 TEST DU NOUVEAU FLUX DE CONNEXION")
print("=" * 60)

# Test 1: Accès à la page de login sans authentification
print("\n1️⃣  Test accès page login...")
response = client.get('/login/')
if response.status_code == 200:
    if 'login_blank.html' in str(response.templates):
        print("   ✅ Page login accessible (template: login_blank.html)")
    else:
        print(f"   ⚠️  Page login accessible (templates utilisés: {[t.name for t in response.templates]})")
else:
    print(f"   ❌ Erreur: status code {response.status_code}")

# Test 2: Test de connexion admin
print("\n2️⃣  Test connexion Admin...")
try:
    admin_user = User.objects.get(username='admin')
    response = client.post('/login/', {
        'username': 'admin',
        'password': 'admin',
        'csrfmiddlewaretoken': client.get('/login/').cookies['csrftoken'].value
    })
    if response.status_code == 302:
        redirect_url = response.url
        print(f"   ✅ Connexion réussie")
        print(f"   Redirection: {redirect_url}")
        if 'produit' in redirect_url:
            print("   ✅ Redirection vers produit_list (admin dans gestion de stock)")
        else:
            print(f"   ⚠️  Redirection non vers produit_list")
    else:
        print(f"   ❌ Erreur: status code {response.status_code}")
except User.DoesNotExist:
    print("   ℹ️  Utilisateur 'admin' non trouvé")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# Test 3: Test de connexion agent
print("\n3️⃣  Test connexion Agent...")
try:
    agent_user = User.objects.filter(groups__name='Gestionnaire Stock').first()
    if agent_user:
        response = client.post('/login/', {
            'username': agent_user.username,
            'password': 'password123'  # À adapter selon votre setup
        })
        if response.status_code == 302:
            redirect_url = response.url
            print(f"   ✅ Connexion agent réussie")
            print(f"   Redirection: {redirect_url}")
            if 'produit' in redirect_url:
                print("   ✅ Agent redirigé vers produit_list")
        else:
            print(f"   ℹ️  Status code: {response.status_code} (password peut être différent)")
    else:
        print("   ℹ️  Aucun agent trouvé")
except Exception as e:
    print(f"   ⚠️  {e}")

# Test 4: Test de logout
print("\n4️⃣  Test logout...")
response = client.get('/logout/')
if response.status_code == 302:
    if '/login/' in response.url:
        print("   ✅ Logout réussie, redirection vers login")
    else:
        print(f"   Redirection: {response.url}")
else:
    print(f"   ❌ Erreur: status code {response.status_code}")

# Test 5: Vérification que /admin/ est toujours accessible
print("\n5️⃣  Vérification accès /admin/...")
response = client.get('/admin/')
if response.status_code == 302:  # Devrait rediriger vers login
    print("   ✅ /admin/ existe toujours et redirige vers login")
else:
    print(f"   Status: {response.status_code}")

print("\n" + "=" * 60)
print("✨ TESTS COMPLÉTÉS!")
print("=" * 60)
