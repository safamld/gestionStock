# 🚀 DÉMARRAGE RAPIDE - Login & Dashboard

## ⏱️ 5 Minutes pour Commencer

### 1️⃣ Démarrer le Serveur
```bash
cd gestionStock/gestion_stock
python manage.py runserver
```

**Output attendu:**
```
Starting development server at http://127.0.0.1:8000/
```

### 2️⃣ Accéder à la Page de Login
Ouvrez votre navigateur:
```
http://localhost:8000/login/
```

Vous verrez une page avec:
- 🎨 Design moderne avec gradient violet
- 📝 Formulaire de connexion
- ✅ Champs: Identifiant, Mot de passe, Se souvenir de moi

### 3️⃣ Se Connecter comme Admin
**Identifiants par défaut:**
- Utilisateur: `admin`
- Mot de passe: `admin`

**Cliquez "Se connecter"**

**Résultat:** 
- ✅ Redirection automatique vers `/admin/`
- ✅ Vous voyez l'interface Django Grappelli
- ✅ Accès à tous les modules

### 4️⃣ Se Déconnecter
Cliquez **"Déconnexion"** en haut à droite

**Résultat:**
- ✅ Redirection vers `/login/`
- ✅ Message "Vous avez été déconnecté avec succès"
- ✅ Session invalidée

### 5️⃣ Créer un Agent (depuis Admin)
1. Allez sur `/admin/`
2. Dans le menu, cliquez **"Utilisateurs"**
3. Cliquez **"+ AJOUTER UN UTILISATEUR"**
4. Remplissez:
   - Nom d'utilisateur: `agent1`
   - Mot de passe: (générez un mot de passe fort)
5. Cliquez **"Enregistrer"**
6. Retournez à la page
7. Scrollez jusqu'à **"Groupe utilisateur"**
8. Cochez **"Gestionnaire Stock"** (accès complet)
9. Cliquez **"Enregistrer"**

### 6️⃣ Se Connecter comme Agent
1. Déconnectez-vous (`/logout/`)
2. Allez sur `/login/`
3. Connectez-vous avec:
   - Utilisateur: `agent1`
   - Mot de passe: (le mot de passe que vous avez défini)
4. Cliquez "Se connecter"

**Résultat:**
- ✅ Redirection automatique vers `/dashboard/`
- ✅ Vous voyez le dashboard personnalisé de l'agent
- ✅ Cartes d'accès: Produits, Commandes, Factures, Statistiques, Historique

---

## 📱 Test Mobile

Pour tester sur mobile (responsive):
1. Ouvrez `http://localhost:8000/login/` sur votre téléphone
2. La page s'adapte automatiquement en une colonne
3. Tous les boutons sont tactiles
4. Le formulaire est facile à remplir

---

## 🎯 Scénarios de Test

### Scénario 1: Admin Complet ✅
```
1. Login avec admin/admin
2. Accès à /admin/
3. Voir tous les modules
4. Pouvoir tout modifier
5. Logout
```

### Scénario 2: Agent Gestionnaire ✅
```
1. Login avec agent (groupe Gestionnaire Stock)
2. Redirection vers /dashboard/
3. Voir toutes les cartes (Produits, Commandes, etc.)
4. Pouvoir accéder à chaque module
5. Logout
```

### Scénario 3: Lecteur Stock ✅
```
1. Login avec lecteur (groupe Lecteur Stock)
2. Redirection vers /dashboard/
3. Voir les cartes (consultation uniquement)
4. Pouvoir voir les détails
5. Ne pas pouvoir créer/modifier/supprimer
6. Logout
```

### Scénario 4: Responsable Commandes ✅
```
1. Login avec responsable (groupe Responsable Commandes)
2. Redirection vers /dashboard/
3. Voir carte "Commandes" activée
4. Autres modules en lecture seule
5. Pouvoir créer/modifier/supprimer commandes
6. Logout
```

---

## 🔍 Vérifications Post-Installation

### ✅ Checklist
- [ ] Serveur démarre sans erreurs
- [ ] Page `/login/` charge correctement
- [ ] Design gradient s'affiche bien
- [ ] Login admin → redirection `/admin/`
- [ ] Login agent → redirection `/dashboard/`
- [ ] Logout invalide la session
- [ ] Message "Déconnecté" s'affiche
- [ ] Dashboard agent affiche les cartes
- [ ] Responsive design fonctionne (F12)
- [ ] CSRF token présent sur le formulaire

---

## 🐛 Dépannage Rapide

### Problème: 502 Bad Gateway
**Solution:**
```bash
# Redémarrez le serveur
pkill -f "python manage.py runserver"
python manage.py runserver
```

### Problème: Module not found (grappelli)
**Solution:**
```bash
pip install django-grappelli openpyxl Pillow
```

### Problème: Page de login vide
**Solution:**
- Vérifiez que `stock/templates/login.html` existe
- Vérifiez les logs du serveur
- Rafraîchissez la page (Ctrl+F5)

### Problème: Erreur 404 sur /dashboard/
**Solution:**
- Vérifiez que `stock/templates/dashboard.html` existe
- Vérifiez l'URL dans les logs
- Assurez-vous d'être connecté

---

## 📊 URLs Essentielles

| Page | URL | Accès |
|------|-----|-------|
| Login | `/login/` | Tous |
| Logout | `/logout/` | Connectés |
| Admin | `/admin/` | Admins uniquement |
| Dashboard | `/dashboard/` | Agents uniquement |
| Produits | `/stock/produits/` | Selon permissions |
| Commandes | `/stock/commandes/` | Selon permissions |
| Factures | `/stock/factures/` | Selon permissions |
| Statistiques | `/stock/statistiques/` | Tous connectés |
| Historique | `/stock/historique/` | Tous connectés |

---

## 📚 Documentation Complète

Pour plus de détails:

1. **`AUTHENTIFICATION.md`** - Documentation technique complète
2. **`GUIDE_UTILISATEUR.md`** - Guide d'utilisation détaillé
3. **`RESUME_IMPLEMENTATION.md`** - Résumé technique complet

---

## 💡 Conseil Pro

### Créez Plusieurs Agents de Test

Pour tester les différentes permissions:

```bash
# Dans /admin/auth/user/

Agent 1: "gestionnaire"
  - Groupe: Gestionnaire Stock (accès complet)

Agent 2: "responsable_cmd"
  - Groupe: Responsable Commandes

Agent 3: "responsable_fact"
  - Groupe: Responsable Factures

Agent 4: "lecteur"
  - Groupe: Lecteur Stock (lecture seule)
```

Testez avec chacun pour valider les permissions!

---

## 🎉 Vous Êtes Prêt!

Tout est configuré et prêt à l'emploi. 

**Accédez simplement à:**
```
http://localhost:8000/login/
```

Et commencez!

---

**✨ Bon utilisation! ✨**

Questions? Consultez les fichiers de documentation.
