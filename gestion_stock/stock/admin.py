"""
Configuration de l'interface d'administration Django.

Enregistre les modèles Produit, Commande, Facture et Historique dans l'admin.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Produit, Commande, Facture, Historique, Fournisseur, ProduitFournisseur, Notification


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    """
    Configuration de l'administration des produits.
    """
    list_display = ('code_prod', 'nom_prod', 'quantite', 'prix_unit', 'total_valeur_stock', 'is_deleted')
    list_filter = ('is_deleted', 'date_creation')
    search_fields = ('nom_prod', 'description')
    readonly_fields = ('code_prod', 'date_creation')
    fieldsets = (
        ('Informations Générales', {
            'fields': ('code_prod', 'nom_prod', 'description')
        }),
        ('Stock et Prix', {
            'fields': ('quantite', 'prix_unit')
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'is_deleted')
        }),
    )
    
    def total_valeur_stock(self, obj):
        """Affiche la valeur totale du stock."""
        return f"{obj.total_valeur_stock():.2f}€"
    total_valeur_stock.short_description = 'Valeur Stock'


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    """
    Configuration de l'administration des commandes.
    """
    list_display = ('code_cmd', 'code_prod', 'quantite_cmd', 'montant_commande', 'date_commande', 'is_deleted')
    list_filter = ('is_deleted', 'date_commande', 'code_prod')
    search_fields = ('code_prod__nom_prod',)
    readonly_fields = ('code_cmd', 'date_commande')
    fieldsets = (
        ('Informations Générales', {
            'fields': ('code_cmd', 'code_prod', 'quantite_cmd')
        }),
        ('Dates', {
            'fields': ('date_commande',)
        }),
        ('Statut', {
            'fields': ('is_deleted',)
        }),
    )
    
    def montant_commande(self, obj):
        """Affiche le montant total de la commande."""
        return f"{obj.montant_commande():.2f}€"
    montant_commande.short_description = 'Montant'


@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    """
    Configuration de l'administration des factures.
    """
    list_display = ('code_facture', 'commande', 'montant_total', 'statut', 'date_facture', 'is_deleted')
    list_filter = ('is_deleted', 'statut', 'date_facture')
    search_fields = ('commande__code_cmd',)
    readonly_fields = ('code_facture', 'date_facture', 'date_modification')
    fieldsets = (
        ('Informations Générales', {
            'fields': ('code_facture', 'commande', 'montant_total')
        }),
        ('Statut', {
            'fields': ('statut',)
        }),
        ('Dates', {
            'fields': ('date_facture', 'date_modification')
        }),
        ('Archivage', {
            'fields': ('is_deleted',)
        }),
    )
    
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        """Personnalise les champs de choix."""
        if db_field.name == 'statut':
            kwargs['initial'] = 'brouillon'
        return super().formfield_for_choice_field(db_field, request, **kwargs)


@admin.register(Historique)
class HistoriqueAdmin(admin.ModelAdmin):
    """
    Configuration de l'administration de l'historique.
    """
    list_display = ('type_objet', 'id_objet', 'date_suppression')
    list_filter = ('type_objet', 'date_suppression')
    search_fields = ('type_objet', 'id_objet')
    readonly_fields = ('type_objet', 'id_objet', 'donnees_supprimees', 'date_suppression')
    
    def has_add_permission(self, request):
        """Empêche l'ajout manuel d'entrées dans l'historique."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Empêche la suppression de l'historique."""
        return False


# ==================== ADMINISTRATION DES FOURNISSEURS ====================

@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    """
    Configuration de l'administration des fournisseurs.
    """
    list_display = ('code_fournisseur', 'nom_fournisseur', 'email', 'telephone', 'statut_badge')
    list_filter = ('is_actif', 'date_creation')
    search_fields = ('nom_fournisseur', 'email', 'telephone')
    readonly_fields = ('code_fournisseur', 'date_creation')
    fieldsets = (
        ('Informations Générales', {
            'fields': ('code_fournisseur', 'nom_fournisseur', 'email')
        }),
        ('Contact', {
            'fields': ('telephone', 'adresse')
        }),
        ('Statut', {
            'fields': ('is_actif',)
        }),
        ('Métadonnées', {
            'fields': ('date_creation',)
        }),
    )
    
    def statut_badge(self, obj):
        """Affiche le statut avec une couleur."""
        if obj.is_actif:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 5px 10px; border-radius: 3px;">✅ Actif</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 5px 10px; border-radius: 3px;">❌ Inactif</span>'
            )
    statut_badge.short_description = 'Statut'


@admin.register(ProduitFournisseur)
class ProduitFournisseurAdmin(admin.ModelAdmin):
    """
    Configuration de l'administration des liaisons Produit-Fournisseur.
    """
    list_display = ('produit', 'fournisseur', 'prix_fournisseur', 'delai_livraison', 'quantite_min', 'principal_badge')
    list_filter = ('is_principal', 'fournisseur', 'delai_livraison')
    search_fields = ('produit__nom_prod', 'fournisseur__nom_fournisseur')
    readonly_fields = ('code_liaison', 'date_ajout')
    fieldsets = (
        ('Produit et Fournisseur', {
            'fields': ('code_liaison', 'produit', 'fournisseur')
        }),
        ('Tarification et Délai', {
            'fields': ('prix_fournisseur', 'delai_livraison', 'quantite_min')
        }),
        ('Configuration', {
            'fields': ('is_principal',)
        }),
        ('Métadonnées', {
            'fields': ('date_ajout',)
        }),
    )
    
    def principal_badge(self, obj):
        """Indique le fournisseur principal."""
        if obj.is_principal:
            return format_html('<span style="color: gold; font-weight: bold;">⭐ Principal</span>')
        return "Secondaire"
    principal_badge.short_description = 'Type'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Configuration de l'administration des notifications.
    """
    list_display = ('code_notification', 'type_badge', 'titre_court', 'produit', 'fournisseur', 'statut_badges', 'date_creation')
    list_filter = ('type_notification', 'est_lue', 'est_traitee', 'date_creation')
    search_fields = ('titre', 'message', 'produit__nom_prod')
    readonly_fields = ('code_notification', 'date_creation', 'date_lecture', 'date_traitement')
    fieldsets = (
        ('Notification', {
            'fields': ('code_notification', 'type_notification', 'titre', 'message')
        }),
        ('Liaisons', {
            'fields': ('produit', 'fournisseur')
        }),
        ('Statut', {
            'fields': ('est_lue', 'est_traitee')
        }),
        ('Dates', {
            'fields': ('date_creation', 'date_lecture', 'date_traitement')
        }),
    )
    actions = ['marquer_comme_lue', 'marquer_comme_traitee']
    
    def type_badge(self, obj):
        """Affiche le type de notification avec couleur."""
        colors = {
            'rupture': '#dc3545',           # Rouge
            'alerte_basse': '#ffc107',      # Jaune
            'commande_confirmee': '#28a745',# Vert
            'facture_payee': '#007bff',     # Bleu
            'fournisseur_contact': '#6f42c1'# Violet
        }
        color = colors.get(obj.type_notification, '#gray')
        return format_html(
            f'<span style="background-color: {color}; color: white; padding: 5px 10px; border-radius: 3px;">{obj.get_type_notification_display()}</span>'
        )
    type_badge.short_description = 'Type'
    
    def titre_court(self, obj):
        """Affiche un titre raccourci."""
        return obj.titre[:50] + '...' if len(obj.titre) > 50 else obj.titre
    titre_court.short_description = 'Titre'
    
    def statut_badges(self, obj):
        """Affiche les statuts de lecture et traitement."""
        lue = '✅ Lue' if obj.est_lue else '⏳ Non lue'
        traitee = '✅ Traitée' if obj.est_traitee else '⏳ En attente'
        return format_html(f'{lue} | {traitee}')
    statut_badges.short_description = 'Statut'
    
    def marquer_comme_lue(self, request, queryset):
        """Action pour marquer les notifications comme lues."""
        updated = 0
        for notification in queryset:
            if not notification.est_lue:
                notification.marquer_comme_lue()
                updated += 1
        self.message_user(request, f'{updated} notification(s) marquée(s) comme lue(s).')
    marquer_comme_lue.short_description = '✅ Marquer comme lue(s)'
    
    def marquer_comme_traitee(self, request, queryset):
        """Action pour marquer les notifications comme traitées."""
        updated = 0
        for notification in queryset:
            if not notification.est_traitee:
                notification.marquer_comme_traitee()
                updated += 1
        self.message_user(request, f'{updated} notification(s) marquée(s) comme traitée(s).')
    marquer_comme_traitee.short_description = '✅ Marquer comme traitée(s)'
    
    def has_add_permission(self, request):
        """Les notifications sont créées automatiquement."""
        return False

