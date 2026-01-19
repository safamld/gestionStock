# 🚀 Guide de Démarrage et Test

## ✅ **Prérequis**

```bash
# Vérifier Python 3.8+
python --version

# Vérifier pip
pip --version

# Vérifier virtualenv (ou venv)
python -m venv --version
```

---

## 🔧 **Installation et Configuration**

### **1️⃣ Créer l'Environnement Virtual**

```bash
# Windows
python -m venv env

# Activation
env\Scripts\activate

# Vérifier activation (prompt change)
# (env) C:\Users\safaa\Desktop\gestionStock\>
```

### **2️⃣ Installer les Dépendances**

```bash
# Mettre à jour pip
pip install --upgrade pip

# Installer requirements
pip install -r requirements.txt

# Dépendances principales:
# - Django==6.0.1
# - Pillow==12.1.0 (images)
# - django-grappelli==4.0.3 (admin moderne)
```

### **3️⃣ Appliquer les Migrations**

```bash
# Aller dans le répertoire principal
cd C:\Users\safaa\Desktop\gestionSt\gestionStock

# Créer tables BD
python manage.py migrate

# Résultat attendu:
# ✓ Running migrations:
#   Applying contenttypes.0001_initial... OK
#   Applying auth.0001_initial... OK
#   Applying stock.0001_initial... OK
#   Applying stock.0002_produit_photo... OK
#   Applying stock.0003_historique... OK
```

### **4️⃣ Créer Admin Superuser**

```bash
python manage.py createsuperuser

# Prompts:
# Username: admin
# Email: admin@example.com
# Password: (tapez votre mot de passe)
# Password (again): (confirmez)

# Résultat:
# Superuser created successfully.
```

### **5️⃣ Lancer le Serveur**

```bash
python manage.py runserver

# Résultat:
# Django version 6.0.1, using settings 'gestion_stock.settings'
# Starting development server at http://127.0.0.1:8000/
# Quit the server with CTRL-BREAK.
```

---

## 🌐 **Accéder à l'Application**

### **Admin Django**
```
http://127.0.0.1:8000/admin/

Login: admin (créé plus haut)
Password: (votre mot de passe)
```

### **Tableau de Bord**
```
http://127.0.0.1:8000/
```

### **Sections Admin Principales**

| Section | URL | Action |
|---------|-----|--------|
| **Produits** | `/admin/stock/produit/` | Add/Edit/Delete/Filter/Export |
| **Commandes** | `/admin/stock/commande/` | Add/Edit/Delete |
| **Factures** | `/admin/stock/facture/` | Add/Edit/Status change |
| **Fournisseurs** | `/admin/stock/fournisseur/` | Add/Edit/Filter (actif) |
| **Notifications** | `/admin/stock/notification/` | View (lecture seule) |
| **Historique** | `/admin/stock/historique/` | View (audit trail) |

---

## 🧪 **Tester les Fonctionnalités**

### **Test 1️⃣: Ajouter un Produit**

```
1. Aller à http://127.0.0.1:8000/admin/stock/produit/
2. Cliquer "Ajouter Produit"
3. Remplir le formulaire:
   - Nom produit: iPhone 15
   - Description: Smartphone haute gamme
   - Quantité: 50
   - Prix unitaire: 1299.00
   - Photo: (optionnel) Uploader une image
4. Cliquer "Enregistrer"

Résultat attendu:
✅ Produit créé et affiché dans la liste
✅ Trié alphabétiquement
✅ Photo visible si uploadée
```

### **Test 2️⃣: Filtrer Produits**

```
1. Aller à Produits admin
2. Utiliser filtres:
   
   "Niveau de Stock":
   ├─ Critique (0-10 unités)
   ├─ Faible (11-50 unités)
   └─ Normal (51+ unités)
   
   "Fournisseur Actif":
   ├─ Oui
   └─ Non
   
   "Date de création": (sélectionner plage)

Résultat attendu:
✅ Liste filtrée par critère
✅ Affichage correct des badges
```

### **Test 3️⃣: Créer une Commande**

```
1. Aller à http://127.0.0.1:8000/admin/stock/commande/
2. Cliquer "Ajouter Commande"
3. Sélectionner:
   - Produit: iPhone 15 (ForeignKey)
   - Quantité: 5
4. Cliquer "Enregistrer"

Résultat attendu:
✅ Commande créée
✅ Facture générée automatiquement (signal)
✅ Notification créée
✅ État: Brouillon
```

### **Test 4️⃣: Actions en Masse**

```
1. Aller à Produits admin
2. Sélectionner plusieurs produits (cocher cases)
3. Menu déroulant "Action": sélectionner:

   • Archiver les produits
     └─ Produits disparaissent (is_deleted=True)
   
   • Marquer comme payées (sur factures)
     └─ Statut facture → "Payée"
   
   • Exporter en CSV
     └─ Fichier téléchargé

Résultat attendu:
✅ Action exécutée sur tous items sélectionnés
✅ Historique créé pour archivage
```

### **Test 5️⃣: Soft-Delete et Historique**

```
1. Ajouter un produit "Test" via admin
2. Aller à Actions en masse
3. Sélectionner le produit et "Archiver"

Produits admin:
✅ "Test" disparaît de liste

Historique admin (http://127.0.0.1:8000/admin/stock/historique/):
✅ Nouvelle entrée:
   Type objet: Produit
   ID objet: X
   Date suppression: 2026-01-18 15:30:45
   Données: JSON complet sauvegardé

4. Restaurer: Sélectionner "Restaurer les produits"
✅ "Test" réapparaît dans Produits
```

### **Test 6️⃣: Statistiques**

```
1. Aller à http://127.0.0.1:8000/admin/stock/produit/
2. Vérifier affichage:
   
   Chaque produit affiche:
   ├─ Code produit
   ├─ Nom
   ├─ Quantité en stock
   ├─ Prix unitaire
   ├─ Valeur totale stock = qty × prix
   ├─ Nombre commandes = Count(Commande)
   └─ Statut badge (Critique/Faible/Normal)

Résultat attendu:
✅ Stats en temps réel
✅ Badges colorés
✅ Tri par statistique
```

### **Test 7️⃣: Notifications**

```
1. Créer une commande
2. Aller à http://127.0.0.1:8000/admin/stock/notification/

Résultat attendu:
✅ Nouvelle notification:
   Type: Commande confirmée
   Produit: (nom produit)
   Message: Commande X unités...
   Date création: now()
   Est lue: Non (cocher pour marquer lue)
```

### **Test 8️⃣: Logout**

```
1. Connecté admin
2. En bas de page, cliquer "Déconnexion"

Résultat attendu:
✅ Redirection vers /admin/
✅ Formulaire login affiché
✅ Session fermée
```

---

## 🧬 **Tests Unitaires**

### **Exécuter Tests Automatisés**

```bash
# Tous les tests
python manage.py test

# Tests spécifiques
python manage.py test stock.tests_admin

# Avec verbose
python manage.py test -v 2

# Résultat attendu:
# test_admin_commande_page (...) ... ok
# test_admin_facture_page (...) ... ok
# test_admin_fournisseur_page (...) ... ok
# test_admin_historique_page (...) ... ok
# test_admin_notification_page (...) ... ok
# test_admin_produit_page (...) ... ok
#
# Ran 6 tests in 2.345s
# OK
```

### **Fichier Tests**

```python
# stock/tests_admin.py

class AdminIntegrationTests(TestCase):
    
    def setUp(self):
        """Créer admin et données"""
        self.admin_user = User.objects.create_superuser(
            username='testadmin',
            email='admin@test.com',
            password='testpass123'
        )
        self.client.login(username='testadmin', password='testpass123')
    
    def test_admin_produit_page(self):
        """Vérifier page admin produits accessible"""
        response = self.client.get('/admin/stock/produit/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_commande_page(self):
        """Vérifier page admin commandes accessible"""
        response = self.client.get('/admin/stock/commande/')
        self.assertEqual(response.status_code, 200)
    
    # ... 4 tests supplémentaires
```

---

## 📋 **Checklist de Vérification**

### **Installation** ✅
- [ ] Python 3.8+ installé
- [ ] Virtual env activé
- [ ] pip à jour
- [ ] requirements.txt installé
- [ ] Migrations appliquées
- [ ] Superuser créé
- [ ] Serveur démarre sans erreur

### **Fonctionnalités** ✅
- [ ] Admin accessible
- [ ] CRUD produits fonctionnel
- [ ] CRUD commandes fonctionnel
- [ ] CRUD factures fonctionnel
- [ ] Filtres appliqués
- [ ] Actions en masse exécutées
- [ ] Soft-delete fonctionne
- [ ] Historique enregistre suppressions
- [ ] Photos uploadées
- [ ] Logout fonctionne

### **Performance** ✅
- [ ] Pages chargent < 2s
- [ ] Requêtes optimisées (select_related)
- [ ] Pas d'erreurs N+1 queries
- [ ] Índices sur ForeignKeys
- [ ] Pagination fonctionne

### **Sécurité** ✅
- [ ] CSRF tokens présents
- [ ] Permissions par rôle
- [ ] Pas d'accès non-auth
- [ ] Admin protégé
- [ ] Historique lecture-seule

---

## 🐛 **Dépannage**

### **Erreur: "ModuleNotFoundError: No module named 'django'"**
```bash
# Solution:
pip install django==6.0.1
# ou
pip install -r requirements.txt
```

### **Erreur: "ProgrammingError: no such table"**
```bash
# Solution: Appliquer migrations
python manage.py migrate
```

### **Erreur: "TemplateDoesNotExist"**
```bash
# Vérifier TEMPLATES config dans settings.py
# Dossier 'templates/' doit exister dans 'stock/' app
```

### **Photo ne s'affiche pas**
```bash
# Vérifier:
# 1. MEDIA_URL = '/media/'
# 2. MEDIA_ROOT = BASE_DIR / 'media'
# 3. Dans urls.py:
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
```

### **Logout retourne 405**
```bash
# ✅ DÉJÀ FIXÉ - url route order correct
# gestion_stock/urls.py:
path('admin/logout/', LogoutView.as_view(next_page='/admin/'), name='logout'),
path('admin/', admin.site.urls),  # Après logout
```

---

## 📊 **Structure de Répertoires**

```
gestionStock/
├── gestion_stock/          # Settings Django
│   ├── __init__.py
│   ├── settings.py         # Config BD, MEDIA, etc
│   ├── urls.py             # Routes principales
│   ├── wsgi.py
│   └── asgi.py
│
├── stock/                  # App Django
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   ├── 0002_produit_photo.py
│   │   └── 0003_historique.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   └── admin/
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   ├── models.py           # 7 modèles (classes)
│   ├── views.py            # 18+ CBVs
│   ├── admin.py            # Admin personnalisé
│   ├── urls.py             # Routes app
│   ├── signals.py          # Django signals
│   ├── forms.py            # Formulaires
│   ├── tests_admin.py      # 6 tests
│   └── apps.py
│
├── media/                  # Photos uploadées
│   └── produits/
│
├── db.sqlite3              # Base de données
├── manage.py               # Management script
└── requirements.txt        # Dépendances
```

---

## 🎯 **Prochaines Étapes (Optionnel)**

```
[ ] Déployer sur Heroku/Azure
[ ] Ajouter authentification frontend
[ ] Implémenter API REST (Django REST Framework)
[ ] Ajouter tests frontend (Selenium)
[ ] Configurer email réel (vs console)
[ ] Ajouter dashboard interactif (Chart.js)
[ ] Configurer CI/CD (GitHub Actions)
[ ] Ajouter backup BD automatique
```

---

## 📞 **Support et Ressources**

- **Documentation Django**: https://docs.djangoproject.com/
- **Django REST Framework**: https://www.django-rest-framework.org/
- **Pillow (Images)**: https://pillow.readthedocs.io/
- **django-grappelli**: https://grappelliproject.com/

---

**Bon développement ! 🚀**
