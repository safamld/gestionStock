"""
Management command pour créer les groupes Agent et Fournisseur avec permissions.
Usage: python manage.py create_groups
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = 'Crée les groupes Agent et Fournisseur avec leurs permissions'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n🔧 Initialisation des groupes d\'utilisateurs...\n'))

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
                    self.stdout.write(self.style.WARNING(
                        f'⚠️  Permission non trouvée: {app_label}.{perm_codename}'
                    ))

            groupe.permissions.set(permissions)

            if created:
                self.stdout.write(self.style.SUCCESS(
                    f'✅ Créé: Groupe "{groupe_name}" avec {len(permissions)} permissions'
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    f'📝 Mis à jour: Groupe "{groupe_name}" avec {len(permissions)} permissions'
                ))

        self.stdout.write(self.style.SUCCESS('\n✅ Groupes configurés avec succès!\n'))
