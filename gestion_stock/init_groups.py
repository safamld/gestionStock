#!/usr/bin/env python
"""
Script pour initialiser les groupes d'utilisateurs (rôles) dans la base de données.
À exécuter une seule fois : python manage.py shell < init_groups.py
"""

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from stock.models import Produit, Commande, Facture

# Créer les groupes
groups_data = {
    'Gestionnaire Stock': {
        'description': 'Accès complet à tous les produits, commandes et factures',
        'permissions': ['add_produit', 'change_produit', 'delete_produit', 'view_produit',
                       'add_commande', 'change_commande', 'delete_commande', 'view_commande',
                       'add_facture', 'change_facture', 'delete_facture', 'view_facture']
    },
    'Responsable Commandes': {
        'description': 'Gestion complète des commandes',
        'permissions': ['view_produit', 'view_commande',
                       'add_commande', 'change_commande', 'delete_commande']
    },
    'Responsable Factures': {
        'description': 'Gestion complète des factures et des produits',
        'permissions': ['view_produit', 'view_facture',
                       'add_facture', 'change_facture', 'delete_facture']
    },
    'Lecteur Stock': {
        'description': 'Accès en lecture seule à tous les documents',
        'permissions': ['view_produit', 'view_commande', 'view_facture']
    }
}

for group_name, config in groups_data.items():
    group, created = Group.objects.get_or_create(name=group_name)
    if created:
        print(f"✓ Groupe '{group_name}' créé")
    else:
        print(f"→ Groupe '{group_name}' existe déjà")
    
    # Ajouter les permissions au groupe
    perms_to_add = []
    for perm_name in config['permissions']:
        try:
            # Trouver la permission
            if perm_name.split('_')[0] in ['add', 'change', 'delete', 'view']:
                action, model = perm_name.split('_', 1)
                if model == 'produit':
                    content_type = ContentType.objects.get_for_model(Produit)
                elif model == 'commande':
                    content_type = ContentType.objects.get_for_model(Commande)
                elif model == 'facture':
                    content_type = ContentType.objects.get_for_model(Facture)
                
                perm = Permission.objects.get(content_type=content_type, codename=perm_name)
                perms_to_add.append(perm)
        except Permission.DoesNotExist:
            print(f"  ⚠ Permission '{perm_name}' non trouvée")
    
    group.permissions.set(perms_to_add)
    print(f"  • {len(perms_to_add)} permissions assignées")

print("\n✓ Groupes initialisés avec succès!")
