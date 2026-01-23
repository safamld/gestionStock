# 🔐 Système d'Authentification Fournisseur - Guide Complet

## 📋 Vue d'ensemble

Un système d'authentification sécurisé a été ajouté pour les fournisseurs, permettant à l'administrateur de configurer un mot de passe pour chaque fournisseur et à chaque fournisseur d'accéder à son dashboard personnel.

---

## 🚀 Accès au Portail Fournisseur

### **Option 1: Page d'Accueil (Recommandée)**
1. Allez à: **http://localhost:8000/stock/**
2. Cliquez sur **"Portail Fournisseur"** dans la section Fournisseur
3. Vous serez redirigé vers la page de login

### **Option 2: URL Directe**
Allez directement à: **http://localhost:8000/stock/fournisseur/login/**

---

## 🔑 Informations de Connexion

Pour se connecter, le fournisseur a besoin de:

1. **Code Fournisseur**: Identifiant unique (ex: `warda21`, `said`)
2. **Mot de Passe**: Défini par l'administrateur

---

## 👨‍💼 Guide pour l'Administrateur

### **1. Ajouter/Modifier un Fournisseur dans l'Admin**

1. Allez à: **http://localhost:8000/admin/stock/fournisseur/**
2. Cliquez sur **"Ajouter un fournisseur"** ou sélectionnez un existant
3. Remplissez les informations:
   - **Code Fournisseur**: (ex: `warda21`)
   - **Nom Fournisseur**: (ex: `Warda Factory`)
   - **Email**: (ex: `tatouma@gmail.com`)
   - **Téléphone**: (ex: `98520147`)
   - **Adresse**: (ex: `Louis Braille, Tunis`)

### **2. Configurer le Mot de Passe**

1. Dans la section **"Accès Dashboard"**, entrez un mot de passe
   - ✅ Peut être n'importe quelle chaîne de caractères (ex: `pass123`, `admin2024`)
   - ✅ N'est pas hashé (stocké en texte brut pour simplicité)
   
2. Cliquez sur **"Enregistrer"**

### **3. Communiquer les Identifiants**

Envoyez au fournisseur:
```
Code Fournisseur: warda21
Mot de Passe: [mot_de_passe_défini]
URL d'accès: http://localhost:8000/stock/fournisseur/login/
```

---

## 👥 Guide pour le Fournisseur

### **1. Se Connecter**

1. Allez à: **http://localhost:8000/stock/fournisseur/login/**
2. Entrez:
   - **Code Fournisseur**: `warda21`
   - **Mot de Passe**: `[mot_de_passe reçu]`
3. Cliquez sur **"Se Connecter"**

### **2. Accéder au Dashboard**

Une fois connecté, vous accédez à:

#### **📊 Statistiques**
- Total de produits proposés
- Nombre de commandes reçues
- Montant total des commandes
- Montant payé ✅
- Montant en attente ⏳

#### **📦 Gérer les Produits**
- Voir tous vos produits
- Ajouter un nouveau produit:
  - Nom du produit
  - Description
  - Prix unitaire
  - Quantité disponible
  - Photo (optionnel)
- Supprimer un produit (soft delete)

#### **📋 Voir les Commandes**
- Liste des commandes reçues des agents
- Détails: Produit, Quantité, Agent, Montant

#### **💰 Gérer les Factures**
- Voir toutes les factures
- **Marquer une facture comme PAYÉE**
  - Cliquez sur le bouton de paiement
  - Le statut passe à ✅ "Payée"
- Voir les montants payés vs en attente

### **3. Se Déconnecter**

Cliquez sur le bouton **"Déconnexion"** en haut du dashboard pour quitter.

---

## 📍 Structure des Routes

```
/stock/                          → Page d'accueil (home_view)
/stock/fournisseur/login/        → Page de login fournisseur (fournisseur_login_view)
/stock/fournisseur/logout/       → Déconnexion fournisseur (fournisseur_logout_view)
/stock/fournisseur/dashboard/    → Dashboard fournisseur (fournisseur_dashboard_view)
/stock/fournisseur/produit/ajouter/              → Ajouter produit
/stock/fournisseur/produit/<id>/supprimer/       → Supprimer produit
/stock/fournisseur/facture/<id>/payee/           → Marquer facture payée
```

---

## 🔒 Sécurité et Authentification

### **Deux Méthodes d'Authentification**

#### **Méthode 1: Session Fournisseur (Sans Django User)**
- L'utilisateur se connecte avec Code + Mot de Passe
- Une session est créée: `request.session['fournisseur_id']`
- Parfait pour les fournisseurs externes

#### **Méthode 2: Django User (Admin/Staff)**
- Si l'utilisateur est staff Django
- Son email doit correspondre à celui d'un fournisseur
- Accès direct sans login supplémentaire

---

## 💾 Base de Données

### **Champ Ajouté au Modèle Fournisseur**

```python
mot_de_passe = models.CharField(
    max_length=100, 
    blank=True, 
    null=True, 
    help_text="Mot de passe pour l'accès au dashboard"
)
```

### **Migration Appliquée**
```
Migration 0006: stock/migrations/0006_fournisseur_mot_de_passe.py
```

---

## 📊 Admin Django - Affichage des Mots de Passe

Dans la liste des fournisseurs, une colonne **"Mot de passe"** affiche:
- 🟢 **"Configuré"** si un mot de passe existe
- 🔴 **"Non configuré"** si aucun mot de passe n'est défini

---

## 🎯 Scénario d'Utilisation Complet

### **Scenario 1: Premier Login d'un Fournisseur**

1. **Admin ajoute le fournisseur**:
   - Code: `warda21`
   - Mot de passe: `warda@123`

2. **Admin envoie les identifiants** au fournisseur

3. **Fournisseur se connecte**:
   - URL: `http://localhost:8000/stock/fournisseur/login/`
   - Code: `warda21`
   - Mot de passe: `warda@123`
   - ✅ Accès au dashboard

4. **Fournisseur ajoute des produits** depuis le dashboard

5. **Agent commande** des produits du fournisseur

6. **Fournisseur valide le paiement** en marquant la facture comme payée

---

## ⚠️ Remarques Importantes

### **Points à Retenir**

✅ **Fait**: Chaque fournisseur a un mot de passe unique
✅ **Fait**: L'admin peut modifier le mot de passe n'importe quand
✅ **Fait**: La session persiste pendant la navigation
✅ **Fait**: Le logout efface la session

⚠️ **Attention**: Les mots de passe ne sont pas hashés (stockés en texte brut)
⚠️ **Attention**: Assurez-vous que le code fournisseur est correct lors de la connexion

---

## 🐛 Dépannage

### **"Aucun fournisseur trouvé"**
- Vérifiez que le code fournisseur est correct
- Vérifiez que le fournisseur existe dans l'admin

### **"Mot de passe incorrect"**
- Assurez-vous que le mot de passe est exactement comme défini
- Les majuscules/minuscules sont sensibles

### **Accès refusé au dashboard**
- Vérifiez que vous avez reçu une session valide après login
- Essayez de vous reconnecter

---

## 📞 Support

Pour toute question ou problème:
1. Contactez l'administrateur système
2. Vérifiez les logs Django (terminal)
3. Consultez la page d'aide dans le portail

---

**Version**: 1.0  
**Date**: Janvier 2026  
**Statut**: ✅ Productif
