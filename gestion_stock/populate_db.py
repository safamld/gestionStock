"""
Script de données de test pour remplir la base de données.

Usage: python manage.py shell < populate_db.py
"""

from stock.models import Produit, Commande, Facture

# Effacer les anciennes données (optionnel)
Produit.objects.all().delete()
Commande.objects.all().delete()
Facture.objects.all().delete()

# Créer des produits
produits_data = [
    {
        'nom_prod': 'Ordinateur Portable',
        'description': 'Ordinateur portable 15" avec processeur dernière génération',
        'quantite': 25,
        'prix_unit': 899.99
    },
    {
        'nom_prod': 'Souris Logitech',
        'description': 'Souris sans fil ergonomique',
        'quantite': 150,
        'prix_unit': 29.99
    },
    {
        'nom_prod': 'Clavier Mécanique',
        'description': 'Clavier mécanique RGB pour gaming',
        'quantite': 45,
        'prix_unit': 149.99
    },
    {
        'nom_prod': 'Écran 27"',
        'description': '4K Ultra HD 27 pouces',
        'quantite': 12,
        'prix_unit': 399.99
    },
    {
        'nom_prod': 'Casque Sans Fil',
        'description': 'Casque Bluetooth avec ANC',
        'quantite': 8,
        'prix_unit': 199.99
    },
    {
        'nom_prod': 'Hub USB',
        'description': 'Hub USB-C 7 ports',
        'quantite': 60,
        'prix_unit': 49.99
    },
    {
        'nom_prod': 'Webcam HD',
        'description': 'Webcam 1080p avec microphone',
        'quantite': 3,
        'prix_unit': 79.99
    },
    {
        'nom_prod': 'Support Bureau',
        'description': 'Support ajustable pour écran',
        'quantite': 18,
        'prix_unit': 59.99
    }
]

produits = []
for data in produits_data:
    produit = Produit.objects.create(**data)
    produits.append(produit)
    print(f"✓ Créé: {produit.nom_prod}")

print(f"\n✓ {len(produits)} produits créés avec succès!\n")

# Créer des commandes
print("Création des commandes...")
commandes_data = [
    {'code_prod': produits[0], 'quantite_cmd': 2},  # 2x Laptop
    {'code_prod': produits[1], 'quantite_cmd': 5},  # 5x Souris
    {'code_prod': produits[2], 'quantite_cmd': 3},  # 3x Clavier
    {'code_prod': produits[0], 'quantite_cmd': 1},  # 1x Laptop
    {'code_prod': produits[3], 'quantite_cmd': 2},  # 2x Écran
]

commandes = []
for data in commandes_data:
    produit = data['code_prod']
    quantite = data['quantite_cmd']
    
    # Vérifier le stock
    if quantite <= produit.quantite:
        commande = Commande.objects.create(**data)
        produit.quantite -= quantite
        produit.save()
        commandes.append(commande)
        print(f"✓ Commande #{commande.code_cmd}: {quantite}x {produit.nom_prod}")
    else:
        print(f"✗ Stock insuffisant pour {produit.nom_prod}")

print(f"\n✓ {len(commandes)} commandes créées!\n")

# Créer des factures
print("Création des factures...")
factures_data = [
    {'commande': commandes[0], 'statut': 'payee'},    # Payée
    {'commande': commandes[1], 'statut': 'validee'},  # Validée
    {'commande': commandes[2], 'statut': 'brouillon'}, # Brouillon
]

factures = []
for data in factures_data:
    commande = data['commande']
    facture = Facture.objects.create(
        commande=commande,
        montant_total=commande.montant_commande(),
        statut=data['statut']
    )
    factures.append(facture)
    print(f"✓ Facture #{facture.code_facture}: {facture.get_statut_display()}")

print(f"\n✓ {len(factures)} factures créées!\n")

print("=" * 50)
print("✓ Base de données remplie avec succès!")
print("=" * 50)
print(f"Produits: {Produit.objects.filter(is_deleted=False).count()}")
print(f"Commandes: {Commande.objects.filter(is_deleted=False).count()}")
print(f"Factures: {Facture.objects.filter(is_deleted=False).count()}")
