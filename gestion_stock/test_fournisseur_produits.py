#!/usr/bin/env python
"""
Script de test pour valider la gestion des produits par les fournisseurs.

Utilisation:
    python test_fournisseur_produits.py

Prérequis:
    - Django setup déjà configuré
    - Base de données peuplée avec un fournisseur et ses produits
"""

import os
import django
from django.contrib.auth.models import Group, User

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_stock.settings')
django.setup()

from stock.models import Fournisseur, Produit


def test_fournisseur_permissions():
    """Teste les permissions des fournisseurs"""
    print("\n" + "="*60)
    print("🧪 TEST: Permissions Fournisseur")
    print("="*60)
    
    # Vérifier qu'un groupe Fournisseur existe
    print("\n1️⃣ Vérification groupe Fournisseur...")
    try:
        fournisseur_group = Group.objects.get(name='Fournisseur')
        print(f"✅ Groupe 'Fournisseur' trouvé: {fournisseur_group}")
    except Group.DoesNotExist:
        print("❌ Groupe 'Fournisseur' NOT FOUND")
        print("   → Créer le groupe: python manage.py init_groups.py")
        return
    
    # Lister tous les fournisseurs
    print("\n2️⃣ Fournisseurs en base...")
    fournisseurs = Fournisseur.objects.all()
    if not fournisseurs:
        print("⚠️ Aucun fournisseur en base")
        print("   → Créer un fournisseur: python manage.py create_test_supplier.py")
        return
    
    for f in fournisseurs:
        print(f"   📦 {f.nom_fournisseur} (user: {f.user.username if f.user else 'N/A'})")
        if f.user:
            groups = f.user.groups.values_list('name', flat=True)
            print(f"      Groupes: {list(groups)}")


def test_produits():
    """Teste l'accès aux produits"""
    print("\n" + "="*60)
    print("🧪 TEST: Produits Fournisseur")
    print("="*60)
    
    fournisseurs = Fournisseur.objects.all()
    if not fournisseurs:
        print("❌ Aucun fournisseur trouvé")
        return
    
    for f in fournisseurs:
        print(f"\n📦 Fournisseur: {f.nom_fournisseur}")
        
        produits = Produit.objects.filter(fournisseur=f, is_deleted=False)
        print(f"   Produits actifs: {produits.count()}")
        
        for p in produits[:3]:  # Afficher les 3 premiers
            print(f"   ✓ {p.nom_prod} (Code: {p.code_prod}, Quantité: {p.quantite}, Prix: {p.prix_unit}€)")
        
        if produits.count() > 3:
            print(f"   ... et {produits.count() - 3} autres")
        
        # Vérifier soft delete
        produits_supprimes = Produit.objects.filter(fournisseur=f, is_deleted=True)
        if produits_supprimes.exists():
            print(f"   🗑️ Produits supprimés (soft delete): {produits_supprimes.count()}")


def test_soft_delete():
    """Teste le soft delete"""
    print("\n" + "="*60)
    print("🧪 TEST: Soft Delete")
    print("="*60)
    
    produits_total = Produit.objects.all().count()
    produits_actifs = Produit.objects.filter(is_deleted=False).count()
    produits_supprimes = Produit.objects.filter(is_deleted=True).count()
    
    print(f"\n📊 Statistiques Produits:")
    print(f"   Total en base: {produits_total}")
    print(f"   Actifs: {produits_actifs}")
    print(f"   Supprimés (soft): {produits_supprimes}")
    
    if produits_total == produits_actifs + produits_supprimes:
        print("\n✅ Soft delete fonctionne correctement")
    else:
        print("\n❌ Incohérence dans le compte des produits")


def test_relations():
    """Teste les relations entre User et Fournisseur"""
    print("\n" + "="*60)
    print("🧪 TEST: Relations User-Fournisseur")
    print("="*60)
    
    users = User.objects.filter(groups__name='Fournisseur')
    print(f"\n👥 Utilisateurs dans le groupe 'Fournisseur': {users.count()}")
    
    for user in users:
        print(f"\n   👤 {user.username} ({user.email})")
        
        # Vérifier OneToOne avec Fournisseur
        try:
            fournisseur = user.fournisseur
            print(f"      ✅ Lié à Fournisseur: {fournisseur.nom_fournisseur}")
            print(f"      Status: {fournisseur.get_statut_display() if hasattr(fournisseur, 'get_statut_display') else fournisseur.statut}")
        except Fournisseur.DoesNotExist:
            print(f"      ❌ Pas de Fournisseur associé")


def test_authentification():
    """Teste l'authentification"""
    print("\n" + "="*60)
    print("🧪 TEST: Authentification")
    print("="*60)
    
    print("\n⚠️ Ce test doit être exécuté avec Django test client")
    print("   Voir: test_auth.py")


def main():
    """Fonction principale"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "🧪 TEST FOURNISSEUR PRODUITS" + " "*14 + "║")
    print("╚" + "="*58 + "╝")
    
    test_fournisseur_permissions()
    test_produits()
    test_soft_delete()
    test_relations()
    test_authentification()
    
    print("\n" + "="*60)
    print("✅ Tests terminés")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
