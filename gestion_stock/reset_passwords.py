"""
Script pour réinitialiser les mots de passe des fournisseurs
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_stock.settings')
django.setup()

from django.contrib.auth.models import User

print("\n" + "="*80)
print("RÉINITIALISER MOTS DE PASSE FOURNISSEURS")
print("="*80 + "\n")

# Lister les Users des fournisseurs
users = User.objects.filter(groups__name='Fournisseur').order_by('username')

print("Fournisseurs disponibles pour réinitialiser le mot de passe:\n")

for i, user in enumerate(users, 1):
    print(f"{i:2}. {user.username:20} ({user.first_name})")

print("\n" + "="*80)
print("Pour changer le mot de passe d'un fournisseur:")
print("  python manage.py changepassword <username>")
print("  Exemple: python manage.py changepassword svr_tunisie")
print("="*80 + "\n")
