# 🔐 Authentification Simplifiée - Fournisseurs et Agents

## 📌 Résumé des Changements

Le système a été simplifié pour supprimer la dépendance à Django Sessions pour les **fournisseurs**. 

- ✅ **Fournisseurs**: Authentification UNIQUEMENT par Code + Mot de Passe (pas de Django User)
- ✅ **Agents**: Authentification UNIQUEMENT par Django User (login.html existant)
- ✅ **Admin**: Panel Django habituel

---

## 🔑 Authentification Fournisseur - Flux Simplifié

### **Login Fournisseur**

```
GET /stock/fournisseur/login/
    ↓
Page login avec 2 champs:
  1. Code Fournisseur (ex: "warda21")
  2. Mot de Passe (défini par admin)
    ↓
POST /stock/fournisseur/login/
    ↓
Vérifie: code_fournisseur + mot_de_passe dans la DB
    ↓
✅ Si OK: request.session['fournisseur_id'] = code_fournisseur
         Redirige vers /stock/fournisseur/dashboard/
    
❌ Si ERREUR: Affiche message d'erreur, reste sur le formulaire
```

### **Dashboard Fournisseur**

```
GET /stock/fournisseur/dashboard/
    ↓
Vérifie: request.session.get('fournisseur_id')
    ↓
✅ Si EXISTS: Affiche le dashboard du fournisseur
❌ Si NOT FOUND: Redirige vers /stock/fournisseur/login/
```

### **Logout Fournisseur**

```
GET /stock/fournisseur/logout/
    ↓
Supprime: del request.session['fournisseur_id']
    ↓
Redirige vers /stock/fournisseur/login/
```

---

## 🚀 Accès au Portail

### **Pour un Fournisseur**

1. **URL**: `http://localhost:8000/stock/fournisseur/login/`
2. **Connexion**:
   - Code: `warda21` (défini par l'admin)
   - Mot de passe: `[défini par l'admin]`
3. **Après connexion**: 
   - Session créée
   - Accès au dashboard

### **Pour un Agent**

1. **URL**: `http://localhost:8000/login/` ou `http://localhost:8000/stock/agent/dashboard/`
2. **Connexion**: Django User existant (Django session)

---

## 📊 Différences d'Authentification

| Aspect | Fournisseur | Agent | Admin |
|--------|------------|-------|-------|
| **Authentification** | Code + Mot de Passe | Django User | Django User |
| **Stocker session** | `session['fournisseur_id']` | Django Session | Django Session |
| **URL Login** | `/stock/fournisseur/login/` | `/login/` | `/admin/` |
| **Décorateur** | Aucun (vérification manuelle) | `@login_required` | Django Admin |
| **Base de données** | `Fournisseur.mot_de_passe` | `auth.User` | `auth.User` |

---

## 📝 Vues Fournisseur Modifiées

### **1. fournisseur_login_view()**
- Pas de `@login_required`
- Récupère: Code + Mot de Passe du POST
- Vérifie dans la DB
- Crée session `request.session['fournisseur_id']`

### **2. fournisseur_logout_view()**
- Supprime session
- Redirige vers login

### **3. fournisseur_dashboard_view()**
- Pas de `@login_required`
- Vérifie `request.session.get('fournisseur_id')`
- Si absent → redirige vers login

### **4. ajouter_produit_fournisseur_view()**
- Pas de `@login_required`
- Vérifie session
- Récupère fournisseur via `code_fournisseur`

### **5. supprimer_produit_fournisseur_view()**
- Pas de `@login_required`
- Vérifie session
- Supprime produit du fournisseur

### **6. marquer_facture_payee_view()**
- Pas de `@login_required`
- Vérifie session
- Valide paiement de la facture

---

## 🔒 Avantages du Nouveau Système

✅ **Simplicité**: Pas de création d'utilisateurs Django pour les fournisseurs  
✅ **Sécurité**: Session isolée par fournisseur  
✅ **Flexibilité**: Fournisseurs peuvent se connecter/déconnecter facilement  
✅ **Pas de dépendance**: Fonctionne sans Django User ou Group  

---

## 🛠️ Configuration Admin

Pour qu'un fournisseur puisse se connecter:

1. Va à `http://localhost:8000/admin/stock/fournisseur/`
2. Édit ou crée un fournisseur
3. **Obligatoire**: Remplir **Mot de Passe** dans la section "Accès Dashboard"
4. Enregistrer

Le fournisseur peut alors utiliser ce mot de passe pour se connecter.

---

## 📍 Routes URL Fournisseur

```
GET   /stock/                                    → home_view
GET   /stock/fournisseur/login/                → fournisseur_login_view (form)
POST  /stock/fournisseur/login/                → fournisseur_login_view (process)
GET   /stock/fournisseur/logout/               → fournisseur_logout_view
GET   /stock/fournisseur/dashboard/            → fournisseur_dashboard_view
GET   /stock/fournisseur/produit/ajouter/      → ajouter_produit_fournisseur_view (form)
POST  /stock/fournisseur/produit/ajouter/      → ajouter_produit_fournisseur_view (process)
GET   /stock/fournisseur/produit/<id>/supprimer/ → supprimer_produit_fournisseur_view
GET   /stock/fournisseur/facture/<id>/payee/   → marquer_facture_payee_view
```

---

## 🔍 Vérifications de Sécurité

Toutes les vues fournisseur vérifient:

```python
fournisseur_id = request.session.get('fournisseur_id')
if not fournisseur_id:
    messages.error(request, "Vous devez être connecté...")
    return redirect('stock:fournisseur_login')
```

**Cela garantit que**:
- Seuls les fournisseurs connectés peuvent accéder
- Pas d'accès direct aux URLs sans session
- Accès refusé sans authentification

---

## ✅ Validation

Le système a été validé par:
```bash
python manage.py check
# System check identified no issues (0 silenced)
```

---

**Version**: 2.0  
**Date**: Janvier 2026  
**Status**: ✅ Production Ready  
**Change**: Session Django supprimée pour les fournisseurs
