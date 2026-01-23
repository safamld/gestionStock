"""
Script pour initialiser les groupes et permissions pour Agents et Fournisseurs.
À exécuter via: python manage.py shell < setup_groups.py
"""

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

def setup_groups():
    """Crée les groupes et assigne les permissions appropriées."""
    
    print("\n🔧 Initialisation des groupes d'utilisateurs...\n")
    
    # Configuration des groupes
    groupes_config = {
        'Agent': {
            'description': 'Agents: Peuvent voir les produits et passer des commandes',
            'permissions': [
                'view_produit',
                'view_commande', 'add_commande',
                'view_facture',
                'view_fournisseur',
            ]
        },
        'Fournisseur': {
            'description': 'Fournisseurs: Peuvent gérer leurs produits et voir les commandes',
            'permissions': [
                'view_produit', 'add_produit', 'change_produit', 'delete_produit',
                'view_commande',
                'view_facture', 'change_facture',
                'view_fournisseur',
            ]
        },
    }
    
    for groupe_name, config in groupes_config.items():
        groupe, created = Group.objects.get_or_create(name=groupe_name)
        
        # Ajouter les permissions
        permissions = []
        for perm_codename in config['permissions']:
            app_label = 'stock'  # Notre app
            try:
                perm = Permission.objects.get(
                    content_type__app_label=app_label,
                    codename=perm_codename
                )
                permissions.append(perm)
            except Permission.DoesNotExist:
                print(f'⚠️  Permission non trouvée: {app_label}.{perm_codename}')
        
        groupe.permissions.set(permissions)
        
        status = '✅ Créé' if created else '📝 Mis à jour'
        print(f'{status}: Groupe "{groupe_name}" avec {len(permissions)} permissions')
    
    print("\n✅ Groupes configurés avec succès!\n")
    return True


if __name__ == '__main__':
    setup_groups()
