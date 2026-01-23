"""
Modèles de données pour la gestion de stock.

Ce module définit les modèles pour gérer les produits, commandes, factures
et leur historique (soft delete avec is_deleted).
"""

from django.db import models
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth.models import User


class Produit(models.Model):
    """
    Modèle représentant un produit en stock.
    
    Attributs:
        code_prod (int): Identifiant unique du produit
        nom_prod (str): Nom du produit
        description (str): Description détaillée du produit
        quantite (int): Quantité disponible en stock
        prix_unit (float): Prix unitaire du produit
        photo (ImageField): Photo du produit
        date_creation (datetime): Date de création du produit
        is_deleted (bool): Marqueur pour soft delete (historique)
    """
    
    code_prod = models.AutoField(primary_key=True)
    nom_prod = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    quantite = models.IntegerField(default=0)
    prix_unit = models.FloatField()
    photo = models.ImageField(
        upload_to='produits/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name='Photo du produit',
        help_text='Téléchargez une image du produit (PNG, JPG, JPEG)'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)  # Soft delete pour historique
    fournisseur = models.ForeignKey('Fournisseur', on_delete=models.SET_NULL, null=True, blank=True, related_name='produits_fournis')
    
    class Meta:
        ordering = ['nom_prod']  # Affichage alphabétique
        verbose_name_plural = "Produits"
        unique_together = ('fournisseur', 'nom_prod')  # Même nom possible pour différents fournisseurs
    
    def __str__(self):
        return f"{self.nom_prod} (Quantité: {self.quantite})"
    
    def est_disponible(self):
        """Vérifie si le produit est en stock."""
        return self.quantite > 0
    
    def total_valeur_stock(self):
        """Calcule la valeur totale du stock pour ce produit."""
        return self.quantite * self.prix_unit
    
    def supprimer_logique(self):
        """Effectue une suppression logique (soft delete)."""
        self.is_deleted = True
        self.save()
    
    def restaurer(self):
        """Restaure un produit supprimé logiquement."""
        self.is_deleted = False
        self.save()


class Commande(models.Model):
    """
    Modèle représentant une commande de produit.
    
    Attributs:
        code_cmd (int): Identifiant unique de la commande
        code_prod (FK): Référence au produit commandé
        quantite_cmd (int): Quantité commandée
        agent_utilisateur (FK): Utilisateur qui a créé la commande
        statut_paiement (str): État du paiement (en attente, payée)
        paiement_confirme (bool): Si le fournisseur a confirmé le paiement
        date_paiement (datetime): Date du paiement confirmé
        date_commande (datetime): Date de création de la commande
        is_deleted (bool): Marqueur pour soft delete (historique)
    """
    
    STATUT_PAIEMENT_CHOICES = [
        ('en_attente', 'En Attente de Paiement'),
        ('payee', 'Payée'),
    ]
    
    code_cmd = models.AutoField(primary_key=True)
    code_prod = models.ForeignKey(Produit, on_delete=models.PROTECT, related_name='commandes')
    quantite_cmd = models.IntegerField(default=1)
    agent_utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='commandes')
    statut_paiement = models.CharField(max_length=20, choices=STATUT_PAIEMENT_CHOICES, default='en_attente')
    paiement_confirme = models.BooleanField(default=False, help_text="Confirmé par le fournisseur")
    date_paiement = models.DateTimeField(null=True, blank=True, help_text="Date du paiement confirmé")
    date_commande = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)  # Soft delete pour historique
    
    class Meta:
        ordering = ['-date_commande']  # Les plus récentes d'abord
        verbose_name_plural = "Commandes"
    
    def __str__(self):
        return f"Commande #{self.code_cmd} - {self.code_prod.nom_prod} (x{self.quantite_cmd})"
    
    def montant_commande(self):
        """Calcule le montant total de la commande."""
        return self.quantite_cmd * self.code_prod.prix_unit
    
    def supprimer_logique(self):
        """Effectue une suppression logique (soft delete)."""
        self.is_deleted = True
        self.save()
    
    def restaurer(self):
        """Restaure une commande supprimée logiquement."""
        self.is_deleted = False
        self.save()
    
    def confirmer_paiement(self):
        """Le fournisseur confirme que l'agent a payé."""
        from django.utils import timezone
        self.statut_paiement = 'payee'
        self.paiement_confirme = True
        self.date_paiement = timezone.now()
        self.save()


class Facture(models.Model):
    """
    Modèle représentant une facture.
    
    Attributs:
        code_facture (int): Identifiant unique de la facture
        commande (FK): Référence à la commande associée
        montant_total (float): Montant total de la facture
        agent_utilisateur (FK): Agent qui a créé la commande
        date_facture (datetime): Date de création de la facture
        statut (str): État de la facture (Brouillon, Validée, Payée, Annulée)
        is_deleted (bool): Marqueur pour soft delete (historique)
    """
    
    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('validee', 'Validée'),
        ('payee', 'Payée'),
        ('annulee', 'Annulée'),
    ]
    
    code_facture = models.AutoField(primary_key=True)
    commande = models.OneToOneField(Commande, on_delete=models.SET_NULL, null=True, blank=True, related_name='facture')
    montant_total = models.FloatField()
    agent_utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='factures')
    date_facture = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon')
    is_deleted = models.BooleanField(default=False)  # Soft delete pour historique
    
    class Meta:
        ordering = ['-date_facture']  # Les plus récentes d'abord
        verbose_name_plural = "Factures"
    
    def __str__(self):
        return f"Facture #{self.code_facture} - {self.montant_total}€ ({self.statut})"
    
    def valider_facture(self):
        """Change le statut de la facture à 'Validée'."""
        if self.statut == 'brouillon':
            self.statut = 'validee'
            self.save()
    
    def marquer_payee(self):
        """Change le statut de la facture à 'Payée'."""
        if self.statut == 'validee':
            self.statut = 'payee'
            self.save()
    
    def annuler_facture(self):
        """Annule la facture."""
        self.statut = 'annulee'
        self.save()
    
    def supprimer_logique(self):
        """Effectue une suppression logique (soft delete)."""
        self.is_deleted = True
        self.save()
    
    def restaurer(self):
        """Restaure une facture supprimée logiquement."""
        self.is_deleted = False
        self.save()


class Historique(models.Model):
    """
    Modèle pour tracer toutes les suppressions et modifications.
    
    Ce modèle enregistre automatiquement chaque suppression de Produit,
    Commande ou Facture via un signal Django.
    
    Attributs:
        type_objet (str): Type d'objet supprimé (Produit, Commande, Facture)
        id_objet (int): ID de l'objet supprimé
        donnees_supprimees (JSON): Données de l'objet supprimé
        date_suppression (datetime): Date de la suppression
    """
    
    TYPE_CHOICES = [
        ('produit', 'Produit'),
        ('commande', 'Commande'),
        ('facture', 'Facture'),
    ]
    
    type_objet = models.CharField(max_length=20, choices=TYPE_CHOICES)
    id_objet = models.IntegerField()
    donnees_supprimees = models.JSONField()
    date_suppression = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_suppression']
        verbose_name_plural = "Historiques"
        indexes = [
            models.Index(fields=['type_objet', 'date_suppression']),
        ]
    
    def __str__(self):
        return f"{self.type_objet.upper()} #{self.id_objet} supprimé le {self.date_suppression}"


# ==================== MODÈLES POUR FOURNISSEURS ET NOTIFICATIONS ====================

class Fournisseur(models.Model):
    """
    Modèle représentant un fournisseur.
    
    Attributs:
        user (FK): Utilisateur Django associé
        code_fournisseur (str): Identifiant unique (texte)
        nom_fournisseur (str): Nom du fournisseur
        email (str): Email du fournisseur pour les notifications
        telephone (str): Numéro de téléphone
        adresse (str): Adresse du fournisseur
        statut (str): Statut du fournisseur (actif/inactif)
        mot_de_passe (str): Mot de passe pour accéder au dashboard
        date_creation (datetime): Date d'ajout du fournisseur
    """
    
    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('inactif', 'Inactif'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='fournisseur')
    code_fournisseur = models.CharField(max_length=50, unique=True, primary_key=True)
    nom_fournisseur = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    telephone = models.CharField(max_length=20, blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='actif')
    mot_de_passe = models.CharField(max_length=100, blank=True, null=True, help_text="Mot de passe pour l'accès au dashboard")
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['nom_fournisseur']
        verbose_name_plural = "Fournisseurs"
    
    def __str__(self):
        return f"{self.nom_fournisseur} ({self.email})"


class ProduitFournisseur(models.Model):
    """
    Modèle de liaison entre Produit et Fournisseur.
    
    Un produit peut avoir plusieurs fournisseurs,
    et chaque relation a un prix et délai de livraison différents.
    """
    
    code_liaison = models.AutoField(primary_key=True)
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT, related_name='fournisseurs')
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.PROTECT, related_name='produits')
    prix_fournisseur = models.FloatField()  # Prix d'achat auprès du fournisseur
    delai_livraison = models.IntegerField(default=7)  # En jours
    quantite_min = models.IntegerField(default=10)  # Quantité minimale pour commander
    is_principal = models.BooleanField(default=False)  # Fournisseur principal
    date_ajout = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['produit', 'fournisseur']
        ordering = ['-is_principal', 'prix_fournisseur']
        verbose_name_plural = "Produits-Fournisseurs"
    
    def __str__(self):
        return f"{self.produit.nom_prod} - {self.fournisseur.nom_fournisseur}"


class Notification(models.Model):
    """
    Modèle pour enregistrer les notifications/alertes.
    
    Attributs:
        type_notification (str): Type d'alerte (rupture, commande, etc)
        produit (FK): Produit concerné
        fournisseur (FK): Fournisseur contacté (optionnel)
        titre (str): Titre de la notification
        message (str): Message détaillé
        est_lue (bool): Si la notification a été lue
        est_traitee (bool): Si l'alerte a été traitée
        date_creation (datetime): Quand l'alerte a été créée
        date_lecture (datetime): Quand elle a été lue
        date_traitement (datetime): Quand elle a été traitée
    """
    
    TYPE_CHOICES = [
        ('rupture', 'Rupture de Stock'),
        ('alerte_basse', 'Stock Bas'),
        ('commande_confirmee', 'Commande Confirmée'),
        ('facture_payee', 'Facture Payée'),
        ('fournisseur_contact', 'Fournisseur Contacté'),
    ]
    
    code_notification = models.AutoField(primary_key=True)
    type_notification = models.CharField(max_length=20, choices=TYPE_CHOICES)
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT, related_name='notifications')
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    titre = models.CharField(max_length=200)
    message = models.TextField()
    est_lue = models.BooleanField(default=False)
    est_traitee = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_lecture = models.DateTimeField(null=True, blank=True)
    date_traitement = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-date_creation']
        verbose_name_plural = "Notifications"
        indexes = [
            models.Index(fields=['est_lue', 'est_traitee']),
            models.Index(fields=['-date_creation']),
        ]
    
    def __str__(self):
        return f"[{self.type_notification.upper()}] {self.titre}"
    
    def marquer_comme_lue(self):
        """Marque la notification comme lue."""
        if not self.est_lue:
            self.est_lue = True
            self.date_lecture = timezone.now()
            self.save()
    
    def marquer_comme_traitee(self):
        """Marque la notification comme traitée."""
        if not self.est_traitee:
            self.est_traitee = True
            self.date_traitement = timezone.now()
            self.save()


class MontantAgent(models.Model):
    """
    Modèle pour tracker le montant total accumulé par agent.
    
    Attributs:
        agent_utilisateur (FK): L'agent (utilisateur Django)
        montant_total (float): Montant cumulé de toutes ses commandes payées
        date_mise_a_jour (datetime): Dernière mise à jour du montant
    """
    
    agent_utilisateur = models.OneToOneField(User, on_delete=models.CASCADE, related_name='montant_commandes')
    montant_total = models.FloatField(default=0.0)
    date_mise_a_jour = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Montants Agents"
    
    def __str__(self):
        return f"{self.agent_utilisateur.username} - {self.montant_total}€"
    
    def ajouter_montant(self, montant):
        """Ajoute un montant au total de l'agent."""
        self.montant_total += montant
        self.save()
    
    def retirer_montant(self, montant):
        """Retire un montant du total de l'agent."""
        self.montant_total = max(0, self.montant_total - montant)
        self.save()
