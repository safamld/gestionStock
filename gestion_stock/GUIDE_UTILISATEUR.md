# 📘 GUIDE D'UTILISATION - Gestion Stock avec Login Moderne

## 🎯 Résumé Rapide

Ce guide explique comment utiliser le nouveau système de login avec routage basé sur les rôles.

---

## 🔐 Première Connexion

### Pour l'Administrateur

1. Ouvrez `http://localhost:8000/login/`
2. Entrez vos identifiants administrateur
3. Cliquez **"Se connecter"**
4. ✅ Vous êtes automatiquement redirigé vers le **Dashboard Admin** (`/admin/`)

### Pour un Agent de Stock

1. Ouvrez `http://localhost:8000/login/`
2. Entrez les identifiants reçus de votre administrateur
3. Cliquez **"Se connecter"**
4. ✅ Vous êtes automatiquement redirigé vers votre **Dashboard Personnel** (`/dashboard/`)

---

## 👨‍💼 Dashboard Admin

### Accès
- URL: `http://localhost:8000/admin/`
- Après login avec compte administrateur

### Fonctionnalités
- ✅ Gestion complète de tous les modules
- ✅ Créer/modifier/supprimer produits, commandes, factures
- ✅ Gérer les utilisateurs et leurs permissions
- ✅ Consulter statistiques avancées
- ✅ Voir l'historique complet

---

## 👨‍💻 Dashboard Agent

### Accès
- URL: `http://localhost:8000/dashboard/`
- Après login avec compte agent

### Fonctionnalités Disponibles
En fonction de votre groupe:

#### **Gestionnaire Stock** 🟢
- Accès complet à tous les modules
- Créer, modifier, supprimer tous les éléments
- Consulter statistiques et historique

#### **Responsable Commandes** 🟡
- Gérer les commandes (CRUD complet)
- Consulter produits et factures (lecture seule)
- Voir statistiques

#### **Responsable Factures** 🔵
- Gérer les factures (CRUD complet)
- Consulter commandes et produits (lecture seule)
- Voir statistiques

#### **Lecteur Stock** ⚪
- Consultation uniquement
- Aucune création/modification/suppression
- Lecture seule sur tous les modules

---

## 📦 Modules Disponibles

### 1. Produits 📦
- **Gestionnaire Stock**: CRUD complet
- **Autres agents**: Voir les détails, consulter quantités
- Actions:
  - Ajouter un nouveau produit
  - Consulter les détails
  - Modifier les informations
  - Voir l'historique

### 2. Commandes 📋
- **Responsable Commandes**: CRUD complet
- **Gestionnaire Stock**: CRUD complet
- **Autres**: Consultation
- Actions:
  - Créer une nouvelle commande
  - Consulter les commandes en cours
  - Modifier le statut
  - Voir la facture associée

### 3. Factures 💳
- **Responsable Factures**: CRUD complet
- **Gestionnaire Stock**: CRUD complet
- **Autres**: Consultation
- Actions:
  - Créer facture depuis commande
  - Marquer comme payée
  - Consulter le détail
  - Exporter en PDF

### 4. Statistiques 📊
- **Tous les agents**: Accès en lecture
- Informations:
  - Total produits/commandes/factures
  - Valeur du stock
  - Produits en stock critique
  - Top 5 produits commandés
  - Factures par statut

### 5. Historique 📜
- **Gestionnaire Stock & Lecteur Stock**: Accès
- Affiche:
  - Toutes les modifications
  - Date et heure
  - Données avant suppression
  - Détails des changements

---

## 🔑 Gestion des Utilisateurs (Admin Seulement)

### Créer un Nouvel Agent

1. Allez sur `http://localhost:8000/admin/`
2. Dans le menu de gauche, cliquez **"Utilisateurs"**
3. Cliquez **"+ AJOUTER UN UTILISATEUR"**
4. Remplissez:
   - **Nom d'utilisateur** (sans espaces)
   - **Mot de passe** (2x pour confirmation)
5. Cliquez **"Enregistrer"**
6. Retournez à la page de l'utilisateur
7. Scrollez jusqu'à **"Groupe utilisateur"**
8. Cochez un groupe:
   - 🟢 Gestionnaire Stock (accès complet)
   - 🟡 Responsable Commandes
   - 🔵 Responsable Factures
   - ⚪ Lecteur Stock (lecture seule)
9. Cliquez **"Enregistrer et continuer"**

### Modifier les Permissions d'un Agent

1. Allez sur `http://localhost:8000/admin/`
2. Cliquez **"Utilisateurs"**
3. Cliquez sur le nom de l'utilisateur
4. Modifiez le groupe dans **"Groupe utilisateur"**
5. Cliquez **"Sauvegarder"**

### Désactiver un Utilisateur

1. Allez sur le profil de l'utilisateur
2. Décochez **"Actif"** dans la section "Permissions"
3. Cliquez **"Sauvegarder"**

---

## 🚪 Déconnexion

### Depuis le Dashboard Agent
1. Cliquez le bouton **"🚪 Déconnexion"** en haut à droite

### Depuis l'Admin
1. Cliquez **"Déconnexion"** en haut à droite

✅ Vous retournerez à la page de login

---

## ⚙️ Paramètres Personnels

### "Se souvenir de moi"
- Cochez cette option avant de vous connecter
- Votre session restera active plus longtemps
- Recommandé pour les ordinateurs personnels
- **Non recommandé** pour les ordinateurs partagés

---

## 🆘 Troubleshooting

### Q: Je vois une page blanche après login
**R:** 
- Vérifiez que JavaScript est activé
- Essayez de rafraîchir la page (F5)
- Vérifiez les erreurs dans la console (F12)

### Q: Le bouton de déconnexion ne fonctionne pas
**R:**
- Essayez `/logout/` directement
- Vérifiez les cookies du navigateur
- Essayez un autre navigateur

### Q: J'accède à /admin/ mais je ne peux pas voir certains modules
**R:**
- Vérifiez votre groupe dans `/admin/auth/user/`
- Demandez à un administrateur d'ajouter les permissions
- Déconnectez-vous et reconnectez-vous

### Q: Mon mot de passe ne fonctionne pas
**R:**
- Vérifiez les majuscules/minuscules
- Demandez à un admin de réinitialiser votre mot de passe
- Essayez `oubli de mot de passe` (placeholder)

### Q: Comment réinitialiser mon mot de passe?
**R:** Contactez votre administrateur qui peut:
1. Aller sur `/admin/auth/user/`
2. Cliquer sur votre profil
3. Cliquer **"Changer le mot de passe"**
4. Définir un nouveau mot de passe

---

## 📱 Utilisation sur Mobile

✅ L'interface de login est **totalement responsive**:
- Layout adapté pour petits écrans
- Boutons tactiles adaptés
- Formulaire facilement remplissable
- Compatible Android et iOS

### Conseils
- Utiliser un navigateur mobile récent
- L'application fonctionne mieux en portrait
- Utiliser WiFi pour meilleure performance

---

## 🔒 Bonnes Pratiques de Sécurité

✅ **À FAIRE:**
- ✅ Changer votre mot de passe régulièrement
- ✅ Ne pas partager vos identifiants
- ✅ Déconnecter-vous après chaque utilisation
- ✅ Utiliser des mots de passe forts (8+ caractères)
- ✅ Signaler tout accès non autorisé

❌ **À NE PAS FAIRE:**
- ❌ Partager votre mot de passe
- ❌ Écrire vos identifiants sur papier
- ❌ Rester connecté sur ordinateur partagé
- ❌ Cliquer sur liens de login d'emails suspects
- ❌ Utiliser le même mot de passe partout

---

## 📊 Exemple: Workflow Complet

### Responsable Commandes - Journée Type

**09:00** - Login
```
1. Ouvrir http://localhost:8000/login/
2. Entrer identifiants
3. Cliquer "Se connecter"
4. Redirection auto vers Dashboard
```

**09:05** - Consulter les commandes
```
1. Cliquer "Commandes" sur le dashboard
2. Voir la liste des commandes en cours
3. Cliquer sur une commande pour détails
```

**09:15** - Créer une nouvelle commande
```
1. Cliquer "+ Nouvelle Commande"
2. Sélectionner le produit
3. Entrer la quantité
4. Cliquer "Enregistrer"
```

**14:00** - Voir les statistiques
```
1. Cliquer "Statistiques" sur dashboard
2. Consulter les graphs
3. Voir top 5 produits
```

**17:00** - Déconnexion
```
1. Cliquer "🚪 Déconnexion"
2. Retour à page login
```

---

## 📞 Support

Pour toute question ou problème:
- Contactez votre administrateur système
- Vérifiez la documentation `AUTHENTIFICATION.md`
- Consultez les logs du serveur si erreur technique

---

**Dernière mise à jour**: 18 Janvier 2026
**Version**: 1.0
**Support**: Administrateur Système
