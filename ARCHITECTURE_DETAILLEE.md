# 🏗️ Architecture Détaillée - Diagramme des Classes

## 📐 **Diagramme UML des Modèles**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        STRUCTURE RELATIONNELLE                          │
└─────────────────────────────────────────────────────────────────────────┘

                          ┌──────────────────┐
                          │    PRODUIT       │
                          ├──────────────────┤
                          │ code_prod: int   │◄─────┐
                          │ nom_prod: str    │      │
                          │ description: str │      │
                          │ quantite: int    │      │
                          │ prix_unit: float │      │ (1)
                          │ photo: image     │      │
                          │ date_creation    │      │
                          │ is_deleted: bool │      │
                          ├──────────────────┤      │
                          │ + est_disponible()     │
                          │ + total_valeur()       │
                          │ + supprimer_logique()  │
                          │ + restaurer()          │
                          └──────────────────┘      │
                                 ▲                  │
                                 │                  │
                           (0..N) │ (1)            │
                                  │                │
                          ┌────────┴────────┐      │
                          │   COMMANDE      │      │
                          ├─────────────────┤      │
                          │ code_cmd: int   │      │
                          │ code_prod: FK   │──────┘
                          │ quantite_cmd    │
                          │ date_commande   │
                          │ is_deleted      │
                          ├─────────────────┤
                          │ + montant_cmd() │
                          │ + ...           │
                          └─────────────────┘
                                  │
                           (1)    │    (1)
                                  │
                          ┌────────▼────────┐
                          │    FACTURE      │
                          ├─────────────────┤
                          │ code_facture    │
                          │ commande: FK    │
                          │ montant_total   │
                          │ statut          │
                          │ date_facture    │
                          │ is_deleted      │
                          ├─────────────────┤
                          │ + valider()     │
                          │ + payer()       │
                          └─────────────────┘


                          ┌──────────────────┐
                          │  FOURNISSEUR     │◄────────┐
                          ├──────────────────┤         │
                          │ code_fournisseur │         │
                          │ nom_fournisseur  │         │
                          │ email            │    (0..N)
                          │ telephone        │         │
                          │ is_actif         │         │
                          ├──────────────────┤         │
                          │ + show_status()  │         │
                          └──────────────────┘         │
                                 ▲                     │
                                 │             PRODUITFOURNISSEUR
                                 │             ┌─────────────────┐
                                 └─────────────│ code_liaison    │
                                  (0..N)       │ produit: FK     │
                                               │ fournisseur: FK─┘
                                               │ prix_fournisseur│
                                               │ delai_livraison │
                                               │ quantite_min    │
                                               │ is_principal    │
                                               └─────────────────┘


                          ┌─────────────────────┐
                          │  NOTIFICATION       │
                          ├─────────────────────┤
                          │ code_notification   │
                          │ type_notification   │
                          │ produit: FK         │
                          │ fournisseur: FK*    │
                          │ titre               │
                          │ message             │
                          │ est_lue: bool       │
                          │ est_traitee: bool   │
                          │ date_creation       │
                          │ date_lecture        │
                          │ date_traitement     │
                          └─────────────────────┘


                          ┌─────────────────────┐
                          │  HISTORIQUE         │ (Audit Trail)
                          │  (Lecture seule)    │
                          ├─────────────────────┤
                          │ code_historique     │
                          │ type_objet: str     │
                          │ id_objet: int       │
                          │ donnees_supprimees  │
                          │ date_suppression    │
                          └─────────────────────┘
```

---

## 🔗 **Relations Entre Modèles**

### **1️⃣ PRODUIT ↔ COMMANDE**
```
Relation: 1 → N (One-to-Many)
Type: ForeignKey
Code:
    class Commande(models.Model):
        code_prod = models.ForeignKey(
            Produit,
            on_delete=models.PROTECT  # ✅ Protège contre suppression produit
        )

Cas d'usage:
    - 1 Produit peut avoir N Commandes
    - 1 Commande appartient à 1 Produit
    
Exemple:
    Produit: "iPhone 15" (id=1)
        └─ Commande 1: 5 unités
        └─ Commande 2: 3 unités
        └─ Commande 3: 2 unités
```

### **2️⃣ COMMANDE ↔ FACTURE**
```
Relation: 1 ↔ 1 (One-to-One)
Type: OneToOneField
Code:
    class Facture(models.Model):
        commande = models.OneToOneField(
            Commande,
            on_delete=models.CASCADE  # ✅ Supprime facture si commande supprimée
        )

Cas d'usage:
    - 1 Commande génère exactement 1 Facture
    - 1 Facture correspond à 1 Commande unique
    
Statuts facture:
    'brouillon'   → Nouvelle facture, non envoyée
    'validee'     → Facture validée
    'payee'       → Paiement effectué
    'annulee'     → Facture annulée
```

### **3️⃣ PRODUIT ↔ FOURNISSEUR (via ProduitFournisseur)**
```
Relation: N ↔ M (Many-to-Many)
Type: Intermédiaire (Relation sémantique)
Code:
    class ProduitFournisseur(models.Model):
        produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
        fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE)
        prix_fournisseur = models.FloatField()
        delai_livraison = models.IntegerField()  # en jours
        quantite_min = models.IntegerField()
        is_principal = models.BooleanField()     # Fournisseur principal?

Cas d'usage:
    - 1 Produit a plusieurs Fournisseurs
    - 1 Fournisseur fournit plusieurs Produits
    - Chaque liaison a ses conditions propres
    
Exemple:
    Produit: "Écran 27p"
        ├─ Fournisseur A: 200€, 5 jours, min 10 ✅ Principal
        ├─ Fournisseur B: 190€, 10 jours, min 20
        └─ Fournisseur C: 210€, 2 jours, min 5
```

### **4️⃣ Soft-Delete avec HISTORIQUE**
```
Processus:
    1. Produit supprimé par utilisateur
           ↓
    2. Signal Django déclenché (post_delete)
           ↓
    3. is_deleted = True (soft-delete)
           ↓
    4. Enregistrement dans Historique
           ├─ type_objet: "Produit"
           ├─ id_objet: 5
           ├─ donnees_supprimees: JSON{...}
           └─ date_suppression: 2026-01-18 15:30
           ↓
    5. Données conservées en BD
    6. Affichage sans item supprimé
    7. Récupération possible si besoin
```

---

## 🎯 **Classe-par-Classe: Détails Complets**

### **📦 CLASSE: Produit**

```python
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Produit(models.Model):
    """
    Représente un produit en stock
    
    Attributs:
        code_prod (int): Identifiant unique (PK)
        nom_prod (str): Nom du produit (unique, index)
        description (str): Description détaillée
        quantite (int): Quantité en stock
        prix_unit (float): Prix unitaire en euros
        photo (image): Image du produit (optionnel)
        date_creation (datetime): Quand créé
        is_deleted (bool): Soft-delete flag
    """
    
    # CHAMPS
    code_prod = models.AutoField(primary_key=True)
    nom_prod = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    quantite = models.IntegerField(default=0)
    prix_unit = models.FloatField()
    photo = models.ImageField(upload_to='produits/', null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    
    # MÉTADONNÉES
    class Meta:
        db_table = 'produit'
        ordering = ['nom_prod']  # Tri alphabétique
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
    
    # MÉTHODES
    def __str__(self):
        """Affichage en chaîne"""
        return f"{self.nom_prod} (Qty: {self.quantite})"
    
    def est_disponible(self):
        """
        Vérifie disponibilité du produit
        
        Retour:
            bool: True si quantite > 0, False sinon
        """
        return self.quantite > 0
    
    def total_valeur_stock(self):
        """
        Calcule la valeur totale du stock
        
        Retour:
            float: quantite * prix_unit
        """
        return self.quantite * self.prix_unit
    
    def supprimer_logique(self):
        """
        Supprime logiquement (soft-delete)
        
        Processus:
            1. Mark is_deleted = True
            2. Save in database
            3. Signal creates Historique entry
        """
        self.is_deleted = True
        self.save()
    
    def restaurer(self):
        """
        Restaure un produit supprimé
        
        Processus:
            1. Mark is_deleted = False
            2. Save in database
            3. Item réapparaît dans liste
        """
        self.is_deleted = False
        self.save()
```

---

### **📦 CLASSE: Commande**

```python
class Commande(models.Model):
    """
    Représente une commande de produit
    
    Attributs:
        code_cmd (int): Identifiant unique (PK)
        code_prod (FK): Référence au produit
        quantite_cmd (int): Quantité commandée
        date_commande (datetime): Quand commandé
        is_deleted (bool): Soft-delete flag
    """
    
    # CHAMPS
    code_cmd = models.AutoField(primary_key=True)
    code_prod = models.ForeignKey(
        Produit,
        on_delete=models.PROTECT,  # Empêche suppression produit si commandes existantes
        related_name='commandes'
    )
    quantite_cmd = models.IntegerField()
    date_commande = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    
    # MÉTADONNÉES
    class Meta:
        db_table = 'commande'
        ordering = ['-date_commande']  # Plus récent en premier
        verbose_name = "Commande"
    
    # MÉTHODES
    def __str__(self):
        """Affichage en chaîne"""
        return f"Commande {self.code_cmd}: {self.code_prod.nom_prod} x{self.quantite_cmd}"
    
    def montant_commande(self):
        """
        Calcule le montant total
        
        Calcul:
            quantite_cmd * prix_unitaire_produit
        
        Retour:
            float: Montant en euros
        """
        return self.quantite_cmd * self.code_prod.prix_unit
    
    def supprimer_logique(self):
        """Soft-delete"""
        self.is_deleted = True
        self.save()
    
    def restaurer(self):
        """Restaure une commande"""
        self.is_deleted = False
        self.save()
```

---

### **📦 CLASSE: Facture**

```python
class Facture(models.Model):
    """
    Représente une facture commerciale
    
    Attributs:
        code_facture (int): Identifiant unique (PK)
        commande (FK): Référence commande
        montant_total (float): Montant TTC
        statut (str): État facture (4 choix)
        date_facture (datetime): Date création
        date_modification (datetime): Dernière modif
        is_deleted (bool): Soft-delete flag
    """
    
    # CONSTANTES
    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('validee', 'Validée'),
        ('payee', 'Payée'),
        ('annulee', 'Annulée'),
    ]
    
    # CHAMPS
    code_facture = models.AutoField(primary_key=True)
    commande = models.OneToOneField(
        Commande,
        on_delete=models.CASCADE,
        related_name='facture'
    )
    montant_total = models.FloatField()
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='brouillon'
    )
    date_facture = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    
    # MÉTADONNÉES
    class Meta:
        db_table = 'facture'
        ordering = ['-date_facture']
        verbose_name = "Facture"
    
    # MÉTHODES
    def __str__(self):
        return f"Facture {self.code_facture} - {self.get_statut_display()}"
    
    def valider_facture(self):
        """Passe facture en statut 'validée'"""
        self.statut = 'validee'
        self.save()
    
    def marquer_payee(self):
        """Marque facture comme entièrement payée"""
        self.statut = 'payee'
        self.save()
    
    def marquer_payee_partiellement(self):
        """Logique paiement partiel (optionnel)"""
        pass
```

---

### **📦 CLASSE: Historique (Audit Trail)**

```python
class Historique(models.Model):
    """
    Enregistrement des suppressions (soft-delete)
    
    Attributs:
        type_objet (str): Type supprimé (Produit/Commande/etc)
        id_objet (int): ID de l'objet supprimé
        donnees_supprimees (str): JSON des données
        date_suppression (datetime): Quand supprimé
    """
    
    # CHAMPS
    code_historique = models.AutoField(primary_key=True)
    type_objet = models.CharField(max_length=50)
    id_objet = models.IntegerField()
    donnees_supprimees = models.TextField()  # JSON
    date_suppression = models.DateTimeField(auto_now_add=True)
    
    # MÉTADONNÉES
    class Meta:
        db_table = 'historique'
        ordering = ['-date_suppression']
        verbose_name = "Historique"
        permissions = [('view_only', 'Can only view')]  # Lecture seule
    
    # MÉTHODES
    def __str__(self):
        return f"{self.type_objet} #{self.id_objet} supprimé le {self.date_suppression}"
```

---

## 🎪 **Diagramme des Vues (Class-Based Views)**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      CLASS-BASED VIEWS (18+)                            │
└─────────────────────────────────────────────────────────────────────────┘

PRODUIT VIEWS:
├── DashboardView (GET /admin/)
│   └─ Affiche tableau bord principal
├── ProduitListView (GET /admin/stock/produit/)
│   └─ Liste tous produits actifs
├── ProduitCreateView (GET/POST /admin/stock/produit/add/)
│   └─ Crée nouveau produit
├── ProduitDetailView (GET /admin/stock/produit/<id>/)
│   └─ Affiche détails produit
├── ProduitUpdateView (GET/POST /admin/stock/produit/<id>/change/)
│   └─ Modifie produit existant
└── ProduitDeleteView (GET/POST /admin/stock/produit/<id>/delete/)
    └─ Supprime logiquement produit


COMMANDE VIEWS:
├── CommandeListView (GET /stock/commandes/)
│   └─ Liste toutes commandes
├── CommandeCreateView (GET/POST /stock/commandes/nouvelle/)
│   └─ Crée nouvelle commande
├── CommandeDetailView (GET /stock/commandes/<id>/)
│   └─ Affiche détails commande
├── CommandeUpdateView (GET/POST /stock/commandes/<id>/modifier/)
│   └─ Modifie commande
└── CommandeDeleteView (GET/POST /stock/commandes/<id>/supprimer/)
    └─ Supprime logiquement


FACTURE VIEWS:
├── FactureListView (GET /stock/factures/)
│   └─ Liste factures
├── FactureCreateView (GET/POST /stock/factures/nouvelle/)
│   └─ Crée facture
├── FactureDetailView (GET /stock/factures/<id>/)
└── FactureUpdateView (GET/POST /stock/factures/<id>/modifier/)


STATS & ADMIN:
├── StatistiquesView (GET /stock/statistiques/)
│   └─ Affiche Count/Sum annotations
├── HistoriqueListView (GET /admin/stock/historique/)
│   └─ Affiche audit trail (lecture seule)
└── NotificationListView (GET /admin/stock/notification/)
    └─ Affiche alertes
```

---

## 🔐 **Contrôle d'Accès et Permissions**

```python
# AdminSite personnalisé
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('code_prod', 'nom_prod', 'quantite', 'prix_unit', 'photo_preview_small')
    list_filter = (NiveauStockFilter, 'date_creation', 'is_deleted')
    search_fields = ('code_prod', 'nom_prod', 'description')
    actions = ['archiver_produits', 'restaurer_produits', 'exporter_csv']
    
    def has_delete_permission(self, request):
        """Empêche suppression hard - utiliser soft-delete"""
        return False
    
    def has_add_permission(self, request):
        """Admin peut ajouter"""
        return request.user.is_staff
    
    def has_change_permission(self, request, obj=None):
        """Admin peut modifier"""
        return request.user.is_staff


# Historique = Lecture seule
class HistoriqueAdmin(admin.ModelAdmin):
    list_display = ('type_objet', 'id_objet', 'date_suppression')
    
    def has_add_permission(self, request):
        """Impossible d'ajouter manuellement"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Impossible de supprimer historique"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Impossible de modifier historique"""
        return False
```

---

## 📊 **Flux de Données Complet**

```
SCÉNARIO: Utilisateur ajoute produit + commande

1. INTERFACE ADMIN
   ├─ Utilisateur clique "Ajouter Produit"
   ├─ Formulaire ProduitCreateView affiché
   └─ Utilisateur remplit: nom, description, quantite, prix, photo

2. VALIDATION
   ├─ Vérifier nom_prod unique (index BD)
   ├─ Vérifier quantite > 0
   ├─ Vérifier prix_unit > 0
   └─ Vérifier photo format valide

3. CRÉATION (Model)
   ├─ Produit.objects.create(nom_prod=..., prix_unit=...)
   ├─ Django génère id automatiquement (AutoField)
   ├─ Calcule date_creation = timezone.now()
   └─ is_deleted = False par défaut

4. SAUVEGARDE (Database)
   ├─ INSERT INTO produit (...) VALUES (...)
   ├─ Index sur nom_prod créé
   └─ Signal post_save déclenché

5. AFFICHAGE
   ├─ Redirect admin:stock_produit_changelist
   ├─ QuerySet filtre is_deleted=False
   ├─ Ordonne par nom_prod (Meta.ordering)
   └─ Affiche nouvelle ligne dans tableau

---

SCÉNARIO: Utilisateur crée commande

1. CommandeCreateView
   ├─ Affiche formulaire
   ├─ Dropdown "Produit" (ForeignKey)
   └─ Input "Quantité"

2. VALIDATION
   ├─ Produit existe et is_deleted=False
   ├─ Quantite > 0
   ├─ Quantite <= stock disponible (optionnel)
   └─ user is_staff

3. CRÉATION (Model)
   ├─ Commande.objects.create(code_prod=produit, quantite_cmd=qty)
   ├─ Django génère code_cmd (AutoField)
   ├─ Calcule date_commande = timezone.now()
   └─ Signal post_save déclenché

4. FACTURE AUTOMATIQUE
   ├─ Signal génère Facture.create()
   ├─ montant_total = qty * produit.prix_unit
   ├─ statut = 'brouillon'
   └─ Historique notification créée

5. AFFICHAGE
   ├─ Dashboard montre "1 nouvelle commande"
   ├─ StatistiquesView: Count augmente
   └─ Notification envoyée (console/email)

---

SCÉNARIO: Utilisateur supprime produit

1. Admin clique "Archiver" (bulk action)

2. SOFT-DELETE
   ├─ UPDATE produit SET is_deleted=1
   ├─ Pas de DELETE réel
   └─ Données conservées

3. SIGNAL Django
   ├─ @receiver(post_save, sender=Produit)
   ├─ if instance.is_deleted:
   │  └─ Historique.create(
   │      type_objet='Produit',
   │      id_objet=instance.id,
   │      donnees_supprimees=json.dumps({...}),
   │      date_suppression=now()
   │    )
   └─ Notification envoyée: "Produit archivé"

4. AFFICHAGE
   ├─ Produit disparaît de liste admin
   ├─ Filter is_deleted=False appliqué
   ├─ Données encore dans BD
   └─ Restauration possible
```

---

## ✅ **Checklist: Conformité Complète**

- [x] Modèles en Classes (7 modèles)
- [x] Encapsulation (private/public methods)
- [x] Héritage (de models.Model)
- [x] Polymorphisme (chaque classe implémente supprimer_logique())
- [x] Abstraction (interfaces claires)
- [x] Relations bien définies (FK, OneToOne, M2M)
- [x] Soft-delete (is_deleted field)
- [x] Audit trail (Historique model)
- [x] Tri alphabétique (Meta.ordering)
- [x] Statistics (Count/Sum annotations)
- [x] CRUD complet (18+ views)
- [x] Filtres avancés (4 SimpleListFilter)
- [x] Actions en masse (5 bulk actions)
- [x] Photo upload (ImageField)
- [x] Permissions (has_add/change/delete)
- [x] Signals (événements automatiques)
- [x] Notifications (système alertes)
- [x] Tests (6 integration tests)

---

**🎯 Conclusion**: Votre projet démontre une **maîtrise complète** de la POO et des patterns Django ! 🚀
