# 📊 Documentation - Système d'Administration Complet

## Vue d'ensemble
Ce document décrit tous les filtres, actions en masse et fonctionnalités du système d'administration complet.

---

## 1️⃣ FILTRES PERSONNALISÉS

### 📦 Niveau de Stock (Produits)
Filtrez les produits selon leur niveau de stock :
- **🔴 Critique (0-10)**: Produits avec stock faible, nécessitant un réapprovisionnement urgent
- **🟠 Faible (11-50)**: Produits avec stock modéré
- **🟢 Normal (51+)**: Produits avec stock suffisant

**Emplacement**: Admin > Produits > Liste > Filtre "Niveau de stock"

### 💳 Statut de Paiement (Factures)
Filtrez les factures selon leur état de paiement :
- **✅ Payée**: Facture entièrement payée
- **⚠️ Partiellement payée**: Facture avec paiement partiel
- **❌ Impayée**: Facture sans paiement

**Emplacement**: Admin > Factures > Liste > Filtre "Statut de paiement"

### 🏢 Statut du Fournisseur
Filtrez les fournisseurs selon leur activité :
- **✅ Actif**: Fournisseur actuellement actif
- **❌ Inactif**: Fournisseur archivé

**Emplacement**: Admin > Fournisseurs > Liste > Filtre "Statut du fournisseur"

### 📬 Statut de Lecture (Notifications)
Filtrez les notifications selon leur statut de lecture :
- **🔔 Non-lues**: Notifications non consultées
- **✅ Lues**: Notifications consultées

**Emplacement**: Admin > Notifications > Liste > Filtre "Statut de lecture"

---

## 2️⃣ ACTIONS EN MASSE

### 📦 Actions Produits
#### Archiver les produits
- **Icône**: 📦
- **Description**: Marque les produits sélectionnés comme supprimés (soft-delete)
- **Utilisation**: Cochez les produits > Sélectionnez "Archiver les produits" > Appliquez
- **Effet**: Les produits seront masqués de la liste principale (visible avec filtre is_deleted)

#### Restaurer les produits
- **Icône**: ♻️
- **Description**: Restaure les produits archivés
- **Utilisation**: Cochez les produits archivés > Sélectionnez "Restaurer les produits" > Appliquez
- **Effet**: Les produits réapparaissent dans la liste principale

#### Exporter en CSV
- **Icône**: 📊
- **Description**: Exporte les produits sélectionnés au format CSV
- **Utilisation**: Cochez les produits > Sélectionnez "Exporter en CSV" > Téléchargez
- **Contenu**: Tous les champs du produit (code, nom, description, quantité, prix, etc.)

### 📋 Actions Commandes
#### Exporter en CSV
- **Description**: Exporte les commandes sélectionnées au format CSV
- **Champs exportés**: code_cmd, code_prod, quantite_cmd, date_commande, is_deleted

### 🧾 Actions Factures
#### Marquer comme payées
- **Icône**: 💳
- **Description**: Marque les factures comme entièrement payées
- **Effet**: 
  - Statut passe à "payee"
  - montant_paye = montant_total
  
#### Marquer comme envoyées
- **Icône**: 📤
- **Description**: Marque les factures comme envoyées au client
- **Limitation**: N'affecte que les factures non encore payées

#### Exporter en CSV
- **Description**: Exporte les factures au format CSV

---

## 3️⃣ CHAMPS DE RECHERCHE AVANCÉE

### 🔎 Recherche Produits
Recherchez par:
- **code_prod**: Code produit unique
- **nom_prod**: Nom du produit
- **description**: Description du produit

### 🔎 Recherche Commandes
Recherchez par:
- **code_cmd**: Code commande
- **code_prod**: Code ou nom du produit associé

### 🔎 Recherche Factures
Recherchez par:
- **code_facture**: Numéro de facture
- **commande**: Code commande associée

### 🔎 Recherche Fournisseurs
Recherchez par:
- **code_fournisseur**: Code unique
- **nom_fournisseur**: Nom du fournisseur
- **email**: Email
- **telephone**: Numéro de téléphone

### 🔎 Recherche Notifications
Recherchez par:
- **code_notification**: ID unique
- **titre**: Titre de la notification
- **message**: Contenu du message
- **produit**: Nom du produit associé

---

## 4️⃣ AFFICHAGES EN COULEUR (BADGES)

### 📦 Produits
| Colonne | Affichage |
|---------|-----------|
| Photo | 50×50px thumbnail avec arrondi |
| Quantité | Badge **cyan** avec nombre d'unités |
| Prix | Badge **bleu** avec montant en €|
| Valeur Stock | Valeur totale calculée |
| Statut | ✅ Actif (vert) / 🗑️ Supprimé (rouge) |

### 📋 Commandes
| Colonne | Affichage |
|---------|-----------|
| Quantité | Badge **cyan** avec nombre d'unités |
| Montant | Badge **violet** avec montant en € |
| Statut | ✅ Active / 🗑️ Supprimée |

### 🧾 Factures
| Colonne | Affichage |
|---------|-----------|
| Montant | Badge **bleu** |
| Statut | 📝 Brouillon / 📤 Envoyée / ✅ Payée / ❌ Annulée |
| Paiement | Indicateur de paiement (complet/partiel/impayé) |
| Montant Restant | Montant à payer en € |

### 🏢 Fournisseurs
| Colonne | Affichage |
|---------|-----------|
| Statut | ✅ Actif (vert) / ❌ Inactif (rouge) |

### 📬 Notifications
| Colonne | Affichage |
|---------|-----------|
| Type | Badge avec couleur (rupture, commande, etc.) |
| Statut | Indicateur de lecture et traitement |

---

## 5️⃣ FONCTIONNALITÉS SUPPLÉMENTAIRES

### 📸 Gestion des Photos de Produit
- **Upload**: Téléchargez des images PNG, JPG, JPEG
- **Stockage**: Organisé par date (dossiers: produits/YYYY/MM/DD/)
- **Aperçu**: 
  - Vignette 50×50px dans la liste
  - Aperçu 300px dans le formulaire d'édition

### 📊 Interface Moderne
- **Thème**: Gradient bleu avec Tailwind CSS
- **Responsive**: Adaptée aux mobiles, tablettes et ordinateurs
- **Icons**: Font Awesome 6.4.0

### 🔒 Permissions
- **Historique**: Lecture seule, pas d'ajout/suppression possible
- **Notifications**: Créées automatiquement, pas d'ajout manuel
- **Soft-delete**: Les produits/commandes/factures supprimés restent en base

---

## 6️⃣ CAS D'UTILISATION

### 📊 Exemple 1: Gérer les ruptures de stock
1. Allez à Admin > Produits
2. Filtrez avec "Niveau de stock" = "Critique"
3. Les produits critiques s'affichent
4. Consultez les fournisseurs associés pour commander

### 💳 Exemple 2: Suivre les paiements
1. Allez à Admin > Factures
2. Filtrez avec "Statut de paiement" = "Impayée"
3. Sélectionnez les factures payées
4. Action: "Marquer comme payées"
5. Confirmez l'action

### 📥 Exemple 3: Exporter des données
1. Allez à Admin > [Produits/Commandes/Factures]
2. Sélectionnez les éléments à exporter
3. Action: "Exporter en CSV"
4. Téléchargez le fichier
5. Ouvrez avec Excel ou LibreOffice

### 🏢 Exemple 4: Gérer les fournisseurs
1. Allez à Admin > Fournisseurs
2. Filtrez avec "Statut du fournisseur" = "Actif"
3. Consultez les contacts pour commander
4. Utilisez les actions pour archiver les fournisseurs obsolètes

---

## 7️⃣ CONSEILS D'UTILISATION

### ⚡ Raccourcis clavier
- **Ctrl+A**: Sélectionner tous les éléments
- **Ctrl+F**: Rechercher dans la page
- **Échap**: Fermer les menus déroulants

### 💡 Bonnes pratiques
1. **Archivez au lieu de supprimer**: Utilisez "Archiver" pour conserver l'historique
2. **Exportez régulièrement**: Faites des sauvegardes CSV
3. **Consultez les notifications**: Allez à Admin > Notifications pour les alertes stock
4. **Filtrez avant les actions**: Pour éviter les modifications accidentelles

### 🔍 Dépannage
- **Erreur lors de l'export**: Vérifiez le navigateur et les permissions
- **Filtre ne fonctionne pas**: Rechargez la page
- **Montant incorrect**: Les factures se recalculent automatiquement

---

## 📞 Support
Pour toute question ou problème, consultez votre administrateur système.

---

**Version**: 1.0  
**Dernière mise à jour**: Janvier 2026  
**Système**: Django 6.0.1 + SQLite3
