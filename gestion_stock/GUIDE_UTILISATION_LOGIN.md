# 🎯 Guide d'Utilisation - Nouveau Système de Connexion

## 🚀 Démarrage Rapide

### Étape 1: Vérifier que Django est en cours d'exécution

```bash
# Terminal 1 - Démarrer Django
cd C:/Users/safaa/Desktop/gestionSt/gestionStock/gestion_stock
python manage.py runserver

# Vous devriez voir:
# Starting development server at http://127.0.0.1:8000/
```

### Étape 2: Accéder à la page de connexion

```
URL: http://localhost:8000/login/
```

**Vous devriez voir:**
- 🎨 Gradient bleu-violet en arrière-plan
- 📦 Icône "box" (boîte) au centre
- Titre "Gestion Stock"
- Sous-titre "Connexion à votre compte"
- Formulaire avec 2 champs: Utilisateur et Mot de passe
- Bouton "Se connecter"
- Checkbox "Se souvenir de moi"

### Étape 3: Tester la Connexion

#### Option A: Admin
```
Utilisateur: admin
Mot de passe: admin
Cliquez: "Se connecter"
```

**Résultat attendu:**
- ✅ Redirection vers `/stock/produit_list/`
- ✅ Message de bienvenue: "Bienvenue admin (Administrateur)"
- ✅ Menu latéral bleu visible
- ✅ Accès à Admin Django (lien en bas du menu)

#### Option B: Agent (Gestionnaire Stock)
```
Utilisateur: agent1
Mot de passe: agent123
Cliquez: "Se connecter"
```

**Résultat attendu:**
- ✅ Redirection vers `/stock/produit_list/`
- ✅ Message de bienvenue: "Bienvenue Agent Test 1 (Agent)"
- ✅ Menu latéral bleu visible
- ✅ **SANS** lien Admin Django

#### Option C: Fournisseur (Lecteur Stock)
```
Utilisateur: fournisseur1
Mot de passe: fournisseur123
Cliquez: "Se connecter"
```

**Résultat attendu:**
- ✅ Redirection vers `/stock/produit_list/`
- ✅ Menu latéral visible (mais avec permissions réduites)
- ✅ Peut seulement LIRE les produits

## 🔄 Scénarios de Test Complets

### Scénario 1: Première Connexion

```
1. Accéder à http://localhost:8000/login/
   ↓
2. Entrer: admin / admin
   ↓
3. Cliquer "Se connecter"
   ↓
4. Vérifier redirection vers /stock/produit_list/
   ↓
5. Voir le message "Bienvenue admin (Administrateur)"
   ↓
6. Vérifier la présence du menu latéral
```

### Scénario 2: Connexion échouée

```
1. Accéder à http://localhost:8000/login/
   ↓
2. Entrer: admin / wrongpassword
   ↓
3. Cliquer "Se connecter"
   ↓
4. Voir le message d'erreur: "Identifiant ou mot de passe incorrect."
   ↓
5. Rester sur /login/
```

### Scénario 3: Logout

```
1. Connecté en tant que admin
   ↓
2. Cliquer sur "Déconnexion" (dans le menu)
   ↓
3. Redirection vers /login/
   ↓
4. Message: "Vous avez été déconnecté avec succès."
```

### Scénario 4: Déjà Connecté

```
1. Connecté en tant que admin
   ↓
2. Accéder à http://localhost:8000/login/
   ↓
3. Redirection automatique vers /stock/produit_list/
   (Ne pas revenir à la page de login)
```

### Scénario 5: Refresh de la Session

```
1. Connecté en tant que agent1
   ↓
2. Onglet ouvert: http://localhost:8000/stock/produit_list/
   ↓
3. Rafraîchir la page (F5)
   ↓
4. Session reste active
   ↓
5. Rester sur /stock/produit_list/
```

## 📋 Vérification de Conformité

### Frontend (Page de Login)

- [ ] Gradient bleu-violet visible
- [ ] Icon Font Awesome charge correctement
- [ ] Champ "Utilisateur" has focus au chargement
- [ ] Champ "Mot de passe" masque le texte
- [ ] Bouton "Se connecter" clickable
- [ ] Checkbox "Se souvenir de moi" fonctionne
- [ ] Design responsive sur mobile
- [ ] Messages d'erreur/succès affichés correctement

### Backend (Vue & Authentification)

- [ ] Formulaire POST correctement traité
- [ ] Authentification contre la base de données
- [ ] Redirection vers /stock/produit_list/ après login
- [ ] Role détecté correctement (Admin vs Agent)
- [ ] Message de bienvenue personnalisé
- [ ] Logout fonctionne
- [ ] CSRF token validé
- [ ] Session management fonctionne

### Permissions (Après Login)

- [ ] Admin voit Admin Django link
- [ ] Agent ne voit pas Admin Django link
- [ ] Gestionnaire Stock voit tous les menus
- [ ] Responsable Commandes voit seulement Commandes
- [ ] Lecteur Stock voit seulement lecture
- [ ] Statistiques accessibles pour les agents

## 🐛 Troubleshooting

### Problème: Page de login blanche

**Cause**: Templates non trouvés
```bash
# Solution:
1. Vérifier que stock/templates/login_blank.html existe
2. Vérifier TEMPLATES dans settings.py
3. Redémarrer Django
```

### Problème: Gradient ne s'affiche pas

**Cause**: Tailwind CSS CDN non chargé
```bash
# Solution:
1. Vérifier connexion internet
2. Vérifier CDN link dans login_blank.html
3. Vérifier console browser (F12) pour les erreurs
```

### Problème: Icons Font Awesome ne s'affichent pas

**Cause**: Font Awesome CDN non accessible
```bash
# Solution:
1. Vérifier lien CDN dans login_blank.html
2. Vérifier connexion internet
3. Regarder la console browser pour CORS errors
```

### Problème: Connexion échoue avec message "CSRF token"

**Cause**: CSRF protection Django
```bash
# Solution:
1. Vérifier que {% csrf_token %} est dans le formulaire
2. Vérifier que CsrfViewMiddleware est dans MIDDLEWARE
3. Vérifier les cookies du navigateur
4. Supprimer les cookies et réessayer
```

### Problème: Redirection boucle infinie

**Cause**: LOGIN_REDIRECT_URL configuré incorrectement
```bash
# Solution dans settings.py:
LOGIN_REDIRECT_URL = 'produit_list'  # Pas de /stock/
# ou
LOGIN_REDIRECT_URL = 'stock:produit_list'  # Avec namespace
```

### Problème: Admin ne voit pas Admin Django link

**Cause**: La permission n'est pas chargée
```bash
# Solution:
1. Vérifier user.is_staff = True dans /admin/
2. Vérifier le template base.html inclut la condition
3. Vérifier que l'utilisateur est bien admin
```

## 📞 Support & Questions

### Questions Fréquentes

**Q: Pourquoi tous les utilisateurs vont vers /stock/?**
A: C'est le design demandé. Tous les utilisateurs accèdent à la même interface gestion de stock, mais avec des permissions différentes selon leur groupe.

**Q: Comment ajouter un nouvel utilisateur?**
A: Accédez à /admin/ et créez un nouvel utilisateur Django, puis assignez-le à un groupe.

**Q: Peut-on avoir une authentification par email?**
A: Pas dans cette version. Utilisez username/password. Une version future supportera OAuth.

**Q: Où stocker les mots de passe?**
A: Django hash les mots de passe en SHA256. Ils ne sont jamais stockés en clair.

## 📚 Fichiers de Référence

1. **login_blank.html** - Page de connexion (Frontend)
2. **views.py** - Logique d'authentification (Backend)
3. **base.html** - Layout principal avec menu
4. **settings.py** - Configuration Django
5. **ARCHITECTURE_LOGIN.md** - Diagrammes et architecture

## 🎓 Prochaines Leçons

1. **Ajouter 2FA**: Implémenter deux facteurs d'authentification
2. **OAuth**: Connecter avec Google/Microsoft
3. **Password Reset**: Permettre la réinitialisation de mot de passe
4. **Audit Trail**: Logger toutes les connexions
5. **Rate Limiting**: Limite les tentatives de connexion

---

**Dernière mise à jour**: 18 janvier 2026
**Version**: 2.1
