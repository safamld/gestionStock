# 🔐 Système d'Authentification et Dashboard - Gestion Stock

## 📋 Vue d'ensemble

Un système de login moderne avec **routage basé sur les rôles** a été implémenté :

- **Admins** → Accès au dashboard admin Django
- **Agents de Stock** → Accès au dashboard gestion de stock (design préservé)
- **Seuls les admins** peuvent créer/modifier les permissions des utilisateurs

---

## 🎨 Fonctionnalités Principales

### 1. **Page de Login Moderne**
- URL: `http://localhost:8000/login/`
- Design avec gradient (violet: #667eea → #764ba2)
- Layout deux colonnes: Branding + Formulaire
- Responsive (mobile-friendly)
- Gestion des messages d'erreur
- Checkbox "Se souvenir de moi"

### 2. **Dashboard Admin**
- Accès automatique pour les utilisateurs avec `is_staff=True`
- Redirection vers `/admin/`
- Conserve l'interface Grappelli

### 3. **Dashboard Agent**
- URL: `http://localhost:8000/dashboard/`
- Affichage des permiss ions de l'utilisateur
- Cartes d'accès rapide aux modules (Produits, Commandes, Factures)
- Actions rapides pour créer/ajouter
- Affichage du rôle (Gestionnaire Stock, Responsable Commandes, etc.)

### 4. **Déconnexion**
- URL: `http://localhost:8000/logout/`
- Redirection vers la page de login
- Message de confirmation

---

## 🔑 Flux d'Authentification

```
1. Utilisateur non connecté → Visite http://localhost:8000/
   ↓
2. Redirection vers /login/
   ↓
3. Saisie identifiant + mot de passe
   ↓
4. Vérification:
   - Si is_staff=True → Redirection /admin/
   - Si groupe agent → Redirection /dashboard/
   ↓
5. Accès aux vues protégées par @login_required
```

---

## 👥 Groupes de Permissions

4 groupes prédéfinis auto-créés au démarrage:

### 1. **Gestionnaire Stock** (Full Access)
- ✅ Accès complet à tous les modules
- ✅ Créer/modifier/supprimer produits, commandes, factures
- ✅ Consulter statistiques et historique

### 2. **Responsable Commandes**
- ✅ Gestion complète des commandes
- ❌ Accès limité aux factures (lecture seule)
- ✅ Consulter produits

### 3. **Responsable Factures**
- ✅ Gestion complète des factures
- ❌ Accès limité aux commandes (lecture seule)
- ✅ Consulter produits

### 4. **Lecteur Stock** (Read-Only)
- ✅ Consultation uniquement
- ❌ Aucune création/modification

---

## 🚀 Routes URL

### Routes d'Authentification
| Route | Vue | Description |
|-------|-----|-------------|
| `/` | `login_view` | Redirection vers login si non connecté |
| `/login/` | `login_view` | Page de login |
| `/logout/` | `logout_view` | Déconnexion |
| `/dashboard/` | `agent_dashboard` | Dashboard agent |

### Routes Protégées (nécessitent login)
| Route | Vue | Permission |
|-------|-----|-----------|
| `/stock/produits/` | `ProduitListView` | view_produit |
| `/stock/commandes/` | `CommandeListView` | view_commande |
| `/stock/factures/` | `FactureListView` | view_facture |
| `/stock/statistiques/` | `StatistiquesView` | Tous |
| `/stock/historique/` | `HistoriqueListView` | Tous |

---

## 🔧 Configuration

### settings.py
```python
# Modèle d'authentification par défaut
AUTH_USER_MODEL = 'auth.User'

# Login URL (par défaut)
LOGIN_URL = 'login'

# Après login
LOGIN_REDIRECT_URL = '/dashboard/'
```

### Décorateurs utilisés
```python
# Vues functions
@login_required(login_url='login')
def agent_dashboard(request):
    ...

# Class-Based Views
@method_decorator(login_required(login_url='login'), name='dispatch')
class ProduitListView(ListView):
    ...
```

---

## 📝 Utilisation

### Créer un Agent
1. Aller sur `/admin/`
2. Authentifier comme admin
3. Aller sur "Utilisateurs"
4. Cliquer "+ Ajouter un Utilisateur"
5. Remplir le formulaire
6. Assigner un groupe dans la section "Groupe utilisateur"
7. Sauvegarder

### Connexion Agent
1. Visiter `http://localhost:8000/login/`
2. Saisir nom d'utilisateur et mot de passe
3. Cliquer "Se connecter"
4. Redirection automatique vers `/dashboard/`

### Connexion Admin
1. Visiter `http://localhost:8000/login/`
2. Saisir identifiant admin
3. Cliquer "Se connecter"
4. Redirection automatique vers `/admin/`

---

## 🛡️ Sécurité

✅ **Implémentée:**
- Vérification CSRF sur formulaire de login
- Hachage des mots de passe Django
- Sessions sécurisées
- Redirection forcée des non-connectés
- Vérification des permissions par groupe
- Déconnexion complète des sessions

---

## ⚠️ Troubleshooting

### Q: La page de login est vide
**R:** Vérifier que `stock/templates/login.html` existe

### Q: Erreur 404 sur /dashboard/
**R:** Vérifier que `stock/templates/dashboard.html` existe et que les URLs sont correctes

### Q: Utilisateur redirigé vers /admin/ au lieu de /dashboard/
**R:** Vérifier que `is_staff=False` pour l'utilisateur

### Q: Permissions ne s'appliquent pas
**R:** Vérifier que l'utilisateur est assigné au bon groupe dans `/admin/auth/user/`

---

## 📊 Fichiers Modifiés

- ✅ `stock/views.py` - Ajout login_view, logout_view, agent_dashboard + protections
- ✅ `gestion_stock/urls.py` - Routes d'authentification
- ✅ `stock/urls.py` - Routes stock + noms simplifiés
- ✅ `stock/templates/login.html` - Page de login moderne (NEW)
- ✅ `stock/templates/dashboard.html` - Dashboard agent (NEW)
- ✅ `stock/templates/stock/historique.html` - Template historique
- ✅ `stock/admin.py` - User/Group management (déjà fait)

---

## 🎯 Points Clés

1. **Design du gestion de stock préservé** - Aucune modification du design existant
2. **Routage automatique** - Admin/Agent détecté automatiquement
3. **Permissions granulaires** - Par groupe d'utilisateurs
4. **Sessions sécurisées** - CSRF, hachage, cookies sécurisés
5. **Responsive** - Fonctionne sur mobile et desktop

---

**Dernière mise à jour**: 18 Janvier 2026
**Version**: 1.0 (Production Ready)
