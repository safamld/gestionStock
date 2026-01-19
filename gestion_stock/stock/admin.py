"""
Configuration de l'interface d'administration Django.

Enregistre les modèles Produit, Commande, Facture et Historique dans l'admin.
Amélioration v2.0 : Filtres avancés, actions étendues, affichages optimisés.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.admin import SimpleListFilter, TabularInline
from django.db.models import Count, Sum, F, DecimalField, Case, When, Q
from django.db.models.functions import Coalesce
from datetime import datetime, timedelta
import json
import csv
from django.http import HttpResponse
from io import BytesIO
# import openpyxl  # À installer: pip install openpyxl
# from openpyxl.styles import PatternFill, Font, Alignment  # À installer: pip install openpyxl

# ==================== PERSONNALISATION DU SITE ADMIN ====================

# Personnalisation de l'interface admin
admin.site.site_header = "⚙️ Gestion de Stock - Administration v2.0"
admin.site.site_title = "Gestion Stock Admin"
admin.site.index_title = "Bienvenue dans l'administration"

# Personnalisation CSS du site
admin.site.enable_nav_sidebar = True
from .models import Produit, Commande, Facture, Historique, Fournisseur, ProduitFournisseur, Notification


# ==================== FILTRES PERSONNALISES ====================

class NiveauStockFilter(SimpleListFilter):
    """Filtre personnalisé pour le niveau de stock des produits."""
    title = '📊 Niveau de stock'
    parameter_name = 'niveau_stock'
    
    def lookups(self, request, model_admin):
        return (
            ('critique', '🔴 Critique (0-10)'),
            ('faible', '🟠 Faible (11-50)'),
            ('normal', '🟢 Normal (51+)'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'critique':
            return queryset.filter(quantite__lte=10)
        elif self.value() == 'faible':
            return queryset.filter(quantite__gt=10, quantite__lte=50)
        elif self.value() == 'normal':
            return queryset.filter(quantite__gt=50)


class DateRangeFilter(SimpleListFilter):
    """Filtre personnalisé pour les plages de dates."""
    title = '📅 Période'
    parameter_name = 'periode'
    
    def lookups(self, request, model_admin):
        return (
            ('today', "Aujourd'hui"),
            ('last_7', '7 derniers jours'),
            ('last_30', '30 derniers jours'),
            ('last_90', '90 derniers jours'),
            ('this_year', 'Cette année'),
        )
    
    def queryset(self, request, queryset):
        now = datetime.now()
        if self.value() == 'today':
            return queryset.filter(date_creation__date=now.date())
        elif self.value() == 'last_7':
            return queryset.filter(date_creation__gte=now - timedelta(days=7))
        elif self.value() == 'last_30':
            return queryset.filter(date_creation__gte=now - timedelta(days=30))
        elif self.value() == 'last_90':
            return queryset.filter(date_creation__gte=now - timedelta(days=90))
        elif self.value() == 'this_year':
            return queryset.filter(date_creation__year=now.year)


class StockCritiqueFilter(SimpleListFilter):
    """Filtre pour les produits avec stock critique."""
    title = '🚨 Alerte Stock'
    parameter_name = 'alerte_stock'
    
    def lookups(self, request, model_admin):
        return (
            ('critique', '🚨 Critique (< 5)'),
            ('faible', '⚠️ Faible (5-20)'),
            ('ok', '✅ OK (> 20)'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'critique':
            return queryset.filter(quantite__lt=5)
        elif self.value() == 'faible':
            return queryset.filter(quantite__gte=5, quantite__lte=20)
        elif self.value() == 'ok':
            return queryset.filter(quantite__gt=20)


class PriceRangeFilter(SimpleListFilter):
    """Filtre pour les gammes de prix."""
    title = '💰 Gamme de Prix'
    parameter_name = 'price_range'
    
    def lookups(self, request, model_admin):
        return (
            ('cheap', '💰 < 50€'),
            ('medium', '💵 50-200€'),
            ('expensive', '💎 > 200€'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'cheap':
            return queryset.filter(prix_unit__lt=50)
        elif self.value() == 'medium':
            return queryset.filter(prix_unit__gte=50, prix_unit__lte=200)
        elif self.value() == 'expensive':
            return queryset.filter(prix_unit__gt=200)


class StatutPaiementFilter(SimpleListFilter):
    """Filtre personnalisé pour le statut de paiement des factures."""
    title = '💳 Statut de paiement'
    parameter_name = 'statut_paiement'
    
    def lookups(self, request, model_admin):
        return (
            ('payee', '✅ Payée'),
            ('partielle', '⚠️ Partiellement payée'),
            ('impayee', '❌ Impayée'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'payee':
            return queryset.filter(montant_paye__gte=F('montant_total'))
        elif self.value() == 'partielle':
            return queryset.exclude(montant_paye=0).exclude(montant_paye__gte=F('montant_total'))
        elif self.value() == 'impayee':
            return queryset.filter(montant_paye=0)


class FournisseurActifFilter(SimpleListFilter):
    """Filtre pour les fournisseurs actifs/inactifs."""
    title = '🏢 Statut du fournisseur'
    parameter_name = 'fournisseur_actif'
    
    def lookups(self, request, model_admin):
        return (
            ('actif', '✅ Actif'),
            ('inactif', '❌ Inactif'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'actif':
            return queryset.filter(is_actif=True)
        elif self.value() == 'inactif':
            return queryset.filter(is_actif=False)


class NotificationLueFilter(SimpleListFilter):
    """Filtre pour les notifications lues/non-lues."""
    title = '📬 Statut de lecture'
    parameter_name = 'notification_lue'
    
    def lookups(self, request, model_admin):
        return (
            ('non_lue', '🔔 Non-lues'),
            ('lue', '✅ Lues'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'non_lue':
            return queryset.filter(est_lue=False)
        elif self.value() == 'lue':
            return queryset.filter(est_lue=True)




# ==================== INLINES POUR EDITION RAPIDE ====================

class CommandeInline(TabularInline):
    """Inline pour éditer les commandes directement dans la fiche produit."""
    model = Commande
    fields = ('code_cmd', 'quantite_cmd', 'date_commande', 'is_deleted')
    readonly_fields = ('code_cmd', 'date_commande')
    extra = 0
    can_delete = True
    max_num = 10


class ProduitFournisseurInline(TabularInline):
    """Inline pour éditer les liaisons fournisseur directement dans la fiche produit."""
    model = ProduitFournisseur
    fields = ('fournisseur', 'prix_fournisseur', 'delai_livraison', 'quantite_min', 'is_principal')
    extra = 0
    can_delete = True
    max_num = 15


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    """
    Configuration de l'administration des produits.
    Version 2.0 : Inlines, optimisation, affichages avancés.
    """
    list_display = ('code_prod', 'nom_prod', 'photo_preview', 'stock_progress_bar', 'prix_unit_badge', 'total_valeur_stock', 'statut_produit')
    list_filter = (NiveauStockFilter, StockCritiqueFilter, PriceRangeFilter, DateRangeFilter, 'is_deleted')
    search_fields = ('code_prod', 'nom_prod', 'description')
    readonly_fields = ('code_prod', 'date_creation', 'total_valeur_stock', 'photo_preview_large', 'stock_alert')
    fieldsets = (
        ('Informations Générales', {
            'fields': ('code_prod', 'nom_prod', 'description'),
            'classes': ('wide',)
        }),
        ('Photo du Produit', {
            'fields': ('photo', 'photo_preview_large'),
            'classes': ('wide',)
        }),
        ('Stock et Prix', {
            'fields': ('quantite', 'prix_unit', 'total_valeur_stock', 'stock_alert'),
            'classes': ('wide',)
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'is_deleted'),
            'classes': ('collapse',)
        }),
    )
    inlines = [CommandeInline, ProduitFournisseurInline]
    
    def get_queryset(self, request):
        """Optimisation des requêtes avec select_related et prefetch_related."""
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('commandes', 'fournisseurs')
    
    def photo_preview(self, obj):
        """Affiche une miniature de la photo."""
        if obj.photo:
            return format_html(
                f'<img src="{obj.photo.url}" width="50" height="50" style="border-radius: 4px; object-fit: cover;" />'
            )
        return format_html('<span style="color: #999; font-size: 12px;">Pas de photo</span>')
    photo_preview.short_description = 'Photo'
    
    def photo_preview_large(self, obj):
        """Affiche un aperçu plus grand de la photo."""
        if obj.photo:
            html = '<div style="margin: 10px 0;"><img src="{}" width="300" style="border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" /></div>'.format(obj.photo.url)
            return mark_safe(html)
        return mark_safe('<p style="color: #999;">Aucune photo téléchargée. Téléchargez une image ci-dessus.</p>')
    photo_preview_large.short_description = 'Aperçu'
    
    def stock_progress_bar(self, obj):
        """Affiche une barre de progression du stock avec emojis."""
        max_stock = 100
        percentage = min((obj.quantite / max_stock) * 100, 100)
        
        if percentage >= 75:
            color = '#10b981'  # Vert
            emoji = '✅'
        elif percentage >= 40:
            color = '#f59e0b'  # Orange
            emoji = '⚠️'
        elif percentage > 0:
            color = '#ef4444'  # Rouge
            emoji = '🔴'
        else:
            color = '#991b1b'  # Rouge foncé
            emoji = '🚨'
        
        bar_width = max(percentage, 5)
        html = f'''
        <div style="width: 100px; margin: 0 auto;">
            <div style="background-color: #e5e7eb; border-radius: 4px; height: 20px; overflow: hidden; position: relative;">
                <div style="background-color: {color}; height: 100%; width: {bar_width}%; transition: width 0.3s;"></div>
                <div style="position: absolute; top: 2px; right: 5px; color: black; font-size: 12px; font-weight: 600;">{obj.quantite}u</div>
            </div>
            <div style="text-align: center; margin-top: 4px; font-size: 12px;">{emoji} {int(percentage)}%</div>
        </div>
        '''
        return format_html(html)
    stock_progress_bar.short_description = 'Stock %'
    
    def stock_alert(self, obj):
        """Affiche une alerte si le stock est critique."""
        if obj.quantite < 5:
            return format_html('<span style="background-color: #dc2626; color: white; padding: 8px 12px; border-radius: 4px; font-weight: 600;">🚨 CRITIQUE : Stock < 5</span>')
        elif obj.quantite < 20:
            return format_html('<span style="background-color: #f59e0b; color: white; padding: 8px 12px; border-radius: 4px; font-weight: 600;">⚠️ FAIBLE : Stock < 20</span>')
        return format_html('<span style="background-color: #10b981; color: white; padding: 8px 12px; border-radius: 4px; font-weight: 600;">✅ OK : Stock suffisant</span>')
    stock_alert.short_description = 'Alerte Stock'
    
    def prix_unit_badge(self, obj):
        """Affiche le prix avec format couleur."""
        return format_html(
            f'<span style="background-color: #3b82f6; color: white; padding: 6px 12px; border-radius: 4px; font-weight: 600;">{obj.prix_unit:.2f}€</span>'
        )
    prix_unit_badge.short_description = 'Prix Unitaire'
    
    def total_valeur_stock(self, obj):
        """Affiche la valeur totale du stock."""
        valeur = obj.total_valeur_stock()
        return format_html(
            f'<strong style="color: #2563eb; font-size: 16px;">{valeur:.2f}€</strong>'
        )
    total_valeur_stock.short_description = 'Valeur Stock'
    
    def statut_produit(self, obj):
        """Affiche le statut du produit."""
        if obj.is_deleted:
            return format_html('<span style="color: #dc2626; font-weight: 600;">🗑️ Supprimé</span>')
        return format_html('<span style="color: #16a34a; font-weight: 600;">✅ Actif</span>')
    statut_produit.short_description = 'Statut'


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    """
    Configuration de l'administration des commandes.
    Version 2.0 : Optimisation requêtes, filtres avancés.
    """
    list_display = ('code_cmd', 'code_prod', 'quantite_cmd_badge', 'montant_badge', 'date_commande', 'statut_cmd')
    list_filter = (DateRangeFilter, 'is_deleted', 'code_prod')
    search_fields = ('code_prod__nom_prod', 'code_cmd')
    readonly_fields = ('code_cmd', 'date_commande', 'montant_commande_display')
    fieldsets = (
        ('Informations Générales', {
            'fields': ('code_cmd', 'code_prod', 'quantite_cmd')
        }),
        ('Montant', {
            'fields': ('montant_commande_display',),
            'classes': ('wide',)
        }),
        ('Dates', {
            'fields': ('date_commande',)
        }),
        ('Statut', {
            'fields': ('is_deleted',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimisation des requêtes avec select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related('code_prod')
    
    def quantite_cmd_badge(self, obj):
        """Affiche la quantité avec couleur."""
        return format_html(
            f'<span style="background-color: #06b6d4; color: white; padding: 6px 12px; border-radius: 4px; font-weight: 600;">{obj.quantite_cmd} u</span>'
        )
    quantite_cmd_badge.short_description = 'Quantité'
    
    def montant_badge(self, obj):
        """Affiche le montant avec format couleur."""
        montant = obj.montant_commande()
        return format_html(
            f'<span style="background-color: #8b5cf6; color: white; padding: 6px 12px; border-radius: 4px; font-weight: 600;">{montant:.2f}€</span>'
        )
    montant_badge.short_description = 'Montant'
    
    def montant_commande_display(self, obj):
        """Affiche le montant total de la commande."""
        montant = obj.montant_commande()
        return format_html(
            f'<strong style="color: #2563eb; font-size: 16px;">{montant:.2f}€</strong>'
        )
    montant_commande_display.short_description = 'Montant Total'
    
    def statut_cmd(self, obj):
        """Affiche le statut de la commande."""
        if obj.is_deleted:
            return format_html('<span style="color: #dc2626; font-weight: 600;">🗑️ Supprimée</span>')
        return format_html('<span style="color: #16a34a; font-weight: 600;">✅ Active</span>')
    statut_cmd.short_description = 'Statut'


@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    """
    Configuration de l'administration des factures.
    Version 2.0 : Optimisation requêtes, nouveaux filtres.
    """
    list_display = ('code_facture', 'commande', 'montant_badge', 'statut_badge', 'paiement_badge', 'date_facture')
    list_filter = (StatutPaiementFilter, DateRangeFilter, 'statut', 'date_facture')
    search_fields = ('code_facture', 'commande__code_cmd')
    readonly_fields = ('code_facture', 'date_facture', 'date_modification', 'montant_restant')
    fieldsets = (
        ('Informations Générales', {
            'fields': ('code_facture', 'commande', 'montant_total')
        }),
        ('Paiement', {
            'fields': ('montant_paye', 'montant_restant'),
            'classes': ('wide',)
        }),
        ('Statut', {
            'fields': ('statut',)
        }),
        ('Dates', {
            'fields': ('date_facture', 'date_modification')
        }),
    )
    
    def get_queryset(self, request):
        """Optimisation des requêtes avec select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related('commande', 'commande__code_prod')
    
    def montant_badge(self, obj):
        """Affiche le montant avec couleur."""
        return format_html(
            f'<span style="background-color: #3b82f6; color: white; padding: 6px 12px; border-radius: 4px; font-weight: 600;">{obj.montant_total:.2f}€</span>'
        )
    montant_badge.short_description = 'Montant'
    
    def statut_badge(self, obj):
        """Affiche le statut avec couleur."""
        statuts = {
            'brouillon': ('#9ca3af', '📝 Brouillon'),
            'envoyee': ('#3b82f6', '📤 Envoyée'),
            'payee': ('#16a34a', '✅ Payée'),
            'annulee': ('#dc2626', '❌ Annulée')
        }
        color, label = statuts.get(obj.statut, ('#9ca3af', 'Inconnu'))
        return format_html(
            f'<span style="background-color: {color}; color: white; padding: 6px 12px; border-radius: 4px; font-weight: 600;">{label}</span>'
        )
    statut_badge.short_description = 'Statut'
    
    def paiement_badge(self, obj):
        """Affiche l'état du paiement."""
        if obj.montant_paye >= obj.montant_total:
            return format_html('<span style="color: #16a34a; font-weight: 600;">✅ Payée Intégralement</span>')
        elif obj.montant_paye > 0:
            restant = obj.montant_total - obj.montant_paye
            pourcentage = (obj.montant_paye / obj.montant_total * 100) if obj.montant_total > 0 else 0
            return format_html(
                f'<span style="color: #f59e0b; font-weight: 600;">⏳ {restant:.2f}€ restants ({pourcentage:.0f}%)</span>'
            )
        return format_html('<span style="color: #dc2626; font-weight: 600;">❌ Non Payée</span>')
    paiement_badge.short_description = 'Paiement'
    
    def montant_restant(self, obj):
        """Affiche le montant restant."""
        restant = obj.montant_total - obj.montant_paye
        color = '#16a34a' if restant <= 0 else '#dc2626'
        return format_html(
            f'<strong style="color: {color}; font-size: 16px;">{restant:.2f}€</strong>'
        )
    montant_restant.short_description = 'Montant Restant'


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
    Version 2.0 : Optimisation, nouveaux filtres.
    """
    list_display = ('code_fournisseur', 'nom_fournisseur', 'email', 'telephone', 'fournisseur_score', 'statut_badge')
    list_filter = (FournisseurActifFilter, DateRangeFilter, 'date_creation')
    search_fields = ('code_fournisseur', 'nom_fournisseur', 'email', 'telephone')
    readonly_fields = ('code_fournisseur', 'date_creation', 'fournisseur_score')
    fieldsets = (
        ('Informations Générales', {
            'fields': ('code_fournisseur', 'nom_fournisseur', 'email')
        }),
        ('Contact', {
            'fields': ('telephone', 'adresse')
        }),
        ('Performance', {
            'fields': ('fournisseur_score',)
        }),
        ('Statut', {
            'fields': ('is_actif',)
        }),
        ('Métadonnées', {
            'fields': ('date_creation',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimisation des requêtes."""
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('produits')
    
    def fournisseur_score(self, obj):
        """Affiche un score du fournisseur."""
        # Nombre de produits fournis
        nb_produits = obj.produits.count()
        
        if nb_produits >= 20:
            score = '⭐⭐⭐⭐⭐'
            color = '#16a34a'
        elif nb_produits >= 10:
            score = '⭐⭐⭐⭐'
            color = '#3b82f6'
        elif nb_produits >= 5:
            score = '⭐⭐⭐'
            color = '#f59e0b'
        elif nb_produits > 0:
            score = '⭐⭐'
            color = '#ec4899'
        else:
            score = '⭐'
            color = '#dc2626'
        
        return format_html(
            f'<span style="color: {color}; font-weight: bold; font-size: 14px;">{score} ({nb_produits} pdts)</span>'
        )
    fournisseur_score.short_description = 'Score'
    
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
    Version 2.0 : Optimisation requêtes.
    """
    list_display = ('produit', 'fournisseur', 'prix_fournisseur_badge', 'delai_livraison_badge', 'quantite_min', 'principal_badge')
    list_filter = ('is_principal', 'fournisseur', 'delai_livraison')
    search_fields = ('produit__nom_prod', 'fournisseur__nom_fournisseur', 'code_liaison')
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
    
    def get_queryset(self, request):
        """Optimisation des requêtes avec select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related('produit', 'fournisseur')
    
    def prix_fournisseur_badge(self, obj):
        """Affiche le prix avec couleur selon le niveau."""
        if obj.prix_fournisseur < 50:
            color = '#10b981'  # Vert
            label = '💚 Économique'
        elif obj.prix_fournisseur < 200:
            color = '#3b82f6'  # Bleu
            label = '💙 Moyen'
        else:
            color = '#f59e0b'  # Orange
            label = '💛 Premium'
        
        return format_html(
            f'<span style="background-color: {color}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: 600;">{obj.prix_fournisseur:.2f}€ {label}</span>'
        )
    prix_fournisseur_badge.short_description = 'Prix'
    
    def delai_livraison_badge(self, obj):
        """Affiche le délai avec couleur selon rapidité."""
        if obj.delai_livraison <= 2:
            color = '#10b981'  # Vert
            emoji = '⚡'
        elif obj.delai_livraison <= 7:
            color = '#3b82f6'  # Bleu
            emoji = '📦'
        else:
            color = '#f59e0b'  # Orange
            emoji = '🚚'
        
        return format_html(
            f'<span style="color: {color}; font-weight: 600;">{emoji} {obj.delai_livraison}j</span>'
        )
    delai_livraison_badge.short_description = 'Délai'
    
    def principal_badge(self, obj):
        """Indique le fournisseur principal."""
        if obj.is_principal:
            return format_html('<span style="color: gold; font-weight: bold;">⭐ Principal</span>')
        return format_html('<span style="color: #999; font-weight: 600;">• Secondaire</span>')
    principal_badge.short_description = 'Type'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Configuration de l'administration des notifications.
    """
    list_display = ('code_notification', 'type_badge', 'titre_court', 'produit', 'fournisseur', 'statut_badges', 'date_creation')
    list_filter = ('type_notification', NotificationLueFilter, 'est_traitee', 'date_creation')
    search_fields = ('code_notification', 'titre', 'message', 'produit__nom_prod')
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


# ==================== ACTIONS PERSONNALISEES GLOBALES ====================

def archiver_produits(modeladmin, request, queryset):
    """Action pour archiver les produits."""
    count = queryset.update(is_deleted=True)
    modeladmin.message_user(request, f'✅ {count} produit(s) archivé(s) avec succès.')
archiver_produits.short_description = '📦 Archiver les produits sélectionnés'


def restaurer_produits(modeladmin, request, queryset):
    """Action pour restaurer les produits archivés."""
    count = queryset.update(is_deleted=False)
    modeladmin.message_user(request, f'✅ {count} produit(s) restauré(s) avec succès.')
restaurer_produits.short_description = '♻️ Restaurer les produits sélectionnés'


def exporter_csv(modeladmin, request, queryset):
    """Action pour exporter les données en CSV."""
    meta = queryset.model._meta
    field_names = [field.name for field in meta.fields]
    
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{meta.verbose_name_plural}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(field_names)
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])
    
    return response
exporter_csv.short_description = '📊 Exporter en CSV'


def exporter_json(modeladmin, request, queryset):
    """Action pour exporter les données en JSON."""
    data = json.loads(serialize('json', queryset))
    
    response = HttpResponse(
        json.dumps(data, ensure_ascii=False, indent=2),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename="{queryset.model._meta.verbose_name_plural}.json"'
    return response
exporter_json.short_description = '📄 Exporter en JSON'


# Fonction exporter_excel commentée (openpyxl non installé)
# def exporter_excel(modeladmin, request, queryset):
#     """Action pour exporter les données en Excel."""
#     wb = openpyxl.Workbook()
#     ws = wb.active
#     ws.title = queryset.model._meta.verbose_name_plural[:31]
#     
#     # En-têtes
#     meta = queryset.model._meta
#     field_names = [field.name for field in meta.fields]
#     ws.append(field_names)
#     
#     # Style en-têtes
#     header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
#     header_font = Font(color="FFFFFF", bold=True)
#     
#     for cell in ws[1]:
#         cell.fill = header_fill
#         cell.font = header_font
#         cell.alignment = Alignment(horizontal="center", vertical="center")
#     
#     # Données
#     for obj in queryset:
#         ws.append([str(getattr(obj, field)) for field in field_names])
#     
#     # Ajuster la largeur des colonnes
#     for column in ws.columns:
#         max_length = 0
#         column_letter = column[0].column_letter
#         for cell in column:
#             try:
#                 if len(str(cell.value)) > max_length:
#                     max_length = len(str(cell.value))
#             except:
#                 pass
#         adjusted_width = min(max_length + 2, 50)
#         ws.column_dimensions[column_letter].width = adjusted_width
#     
#     # Réponse
#     response = HttpResponse(
#         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#     )
#     response['Content-Disposition'] = f'attachment; filename="{queryset.model._meta.verbose_name_plural}.xlsx"'
#     wb.save(response)
#     return response
# exporter_excel.short_description = '📈 Exporter en Excel'  # Commenté - openpyxl non installé


def marquer_comme_paye(modeladmin, request, queryset):
    """Action pour marquer les factures comme payées."""
    count = 0
    for facture in queryset:
        if facture.montant_paye < facture.montant_total:
            facture.montant_paye = facture.montant_total
            facture.statut = 'payee'
            facture.save()
            count += 1
    modeladmin.message_user(request, f'✅ {count} facture(s) marquée(s) comme payée(s).')
marquer_comme_paye.short_description = '💳 Marquer comme payées'


def marquer_comme_envoyee(modeladmin, request, queryset):
    """Action pour marquer les factures comme envoyées."""
    count = queryset.exclude(statut='payee').update(statut='envoyee')
    modeladmin.message_user(request, f'✅ {count} facture(s) marquée(s) comme envoyée(s).')
marquer_comme_envoyee.short_description = '📤 Marquer comme envoyées'


# ==================== ENREGISTREMENT DES ACTIONS ====================

# Ajouter les actions personnalisées aux ModelAdmin
ProduitAdmin.actions = [archiver_produits, restaurer_produits, exporter_csv, exporter_json]  # exporter_excel commenté
CommandeAdmin.actions = [exporter_csv, exporter_json]  # exporter_excel commenté
FactureAdmin.actions = [marquer_comme_paye, marquer_comme_envoyee, exporter_csv, exporter_json]  # exporter_excel commenté


# ==================== GESTION DES UTILISATEURS ====================

# ==================== GESTION DES UTILISATEURS ====================

from django.contrib.auth.models import User, Permission, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.contenttypes.models import ContentType

# Unregistrer l'admin User par défaut
admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """
    Admin personnalisé pour la gestion des utilisateurs de la gestion de stock.
    Permet de créer des utilisateurs avec permissions d'accès à l'app stock.
    """
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'groupe_utilisateur')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'groups', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    fieldsets = (
        ('Informations Personnelles', {
            'fields': ('username', 'password', 'email', 'first_name', 'last_name')
        }),
        ('Permissions', {
            'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions'),
            'description': '⚠️ Donnez des permissions pour accéder à la gestion de stock'
        }),
        ('Metadata', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name'),
        }),
        ('Permissions', {
            'classes': ('wide',),
            'fields': ('is_staff', 'is_active', 'groups'),
            'description': '✅ Sélectionnez les groupes pour les permissions'
        }),
    )
    
    def groupe_utilisateur(self, obj):
        """Affiche les groupes de l'utilisateur."""
        groupes = ', '.join([g.name for g in obj.groups.all()])
        if not groupes:
            return format_html('<span style="color: #999;">Pas de groupe</span>')
        
        # Couleurs par groupe
        couleurs = {
            'Gestionnaire Stock': '#28a745',  # Vert
            'Responsable Commandes': '#ffc107',  # Jaune
            'Responsable Factures': '#17a2b8',  # Bleu
            'Lecteur Stock': '#6c757d',  # Gris
        }
        
        badges = []
        for groupe in obj.groups.all():
            couleur = couleurs.get(groupe.name, '#007bff')
            badges.append(f'<span style="background-color: {couleur}; color: white; padding: 3px 8px; border-radius: 3px; margin-right: 5px; display: inline-block;">{groupe.name}</span>')
        
        return format_html(''.join(badges))
    groupe_utilisateur.short_description = '👥 Groupe(s)'
    
    def save_model(self, request, obj, form, change):
        """Sauvegarde le modèle utilisateur."""
        if not change:
            # Nouvel utilisateur : définir le mot de passe
            obj.set_password(form.cleaned_data.get('password1'))
        super().save_model(request, obj, form, change)

# Unregistrer Group aussi (s'il est enregistré)
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """
    Admin pour gérer les groupes d'utilisateurs et leurs permissions.
    """
    list_display = ('name', 'nombre_utilisateurs', 'nombre_permissions')
    search_fields = ('name',)
    filter_horizontal = ('permissions',)
    
    def nombre_utilisateurs(self, obj):
        """Affiche le nombre d'utilisateurs dans le groupe."""
        count = obj.user_set.count()
        return format_html(f'<strong style="color: #007bff;">{count}</strong> utilisateur(s)')
    nombre_utilisateurs.short_description = '👥 Utilisateurs'
    
    def nombre_permissions(self, obj):
        """Affiche le nombre de permissions du groupe."""
        count = obj.permissions.count()
        couleur = '#28a745' if count > 0 else '#dc3545'
        return format_html(f'<strong style="color: {couleur};">{count}</strong> permission(s)')
    nombre_permissions.short_description = '🔐 Permissions'


# ==================== CRÉATION DES GROUPES PAR DÉFAUT ====================

def creer_groupes_par_defaut():
    """
    Crée les groupes d'utilisateurs par défaut avec permissions.
    À appeler une fois lors de l'installation.
    """
    from django.core.management import call_command
    
    # Groupes disponibles avec description
    groupes_config = {
        'Gestionnaire Stock': {
            'description': 'Accès complet à la gestion de stock, produits, commandes, factures',
            'permissions': [
                'add_produit', 'change_produit', 'delete_produit', 'view_produit',
                'add_commande', 'change_commande', 'delete_commande', 'view_commande',
                'add_facture', 'change_facture', 'delete_facture', 'view_facture',
                'view_fournisseur', 'add_fournisseur',
                'view_produitfournisseur', 'add_produitfournisseur',
                'view_historique',
            ]
        },
        'Responsable Commandes': {
            'description': 'Peut créer, modifier et voir les commandes et produits',
            'permissions': [
                'view_produit',
                'add_commande', 'change_commande', 'view_commande',
                'view_facture',
                'view_fournisseur',
            ]
        },
        'Responsable Factures': {
            'description': 'Peut gérer les factures et voir les commandes/produits',
            'permissions': [
                'view_produit',
                'view_commande',
                'add_facture', 'change_facture', 'view_facture',
                'view_fournisseur',
            ]
        },
        'Lecteur Stock': {
            'description': 'Lecture seule - consultation des stocks et rapports',
            'permissions': [
                'view_produit',
                'view_commande',
                'view_facture',
                'view_fournisseur',
                'view_historique',
            ]
        }
    }
    
    for groupe_name, config in groupes_config.items():
        groupe, created = Group.objects.get_or_create(name=groupe_name)
        
        # Ajouter les permissions
        permissions = []
        for perm_codename in config['permissions']:
            app_label = 'stock'  # Notre app
            try:
                perm = Permission.objects.get(
                    content_type__app_label=app_label,
                    codename=perm_codename
                )
                permissions.append(perm)
            except Permission.DoesNotExist:
                print(f'⚠️ Permission non trouvée: {app_label}.{perm_codename}')
        
        groupe.permissions.set(permissions)
        
        status = '✅ Créé' if created else '📝 Mis à jour'
        print(f'{status}: Groupe "{groupe_name}" avec {len(permissions)} permissions')
    
    return True


# Créer les groupes au premier démarrage
try:
    if not Group.objects.filter(name='Gestionnaire Stock').exists():
        print('\n🔧 Création des groupes d\'utilisateurs...')
        creer_groupes_par_defaut()
        print('✅ Groupes créés avec succès!\n')
except Exception as e:
    print(f'⚠️ Erreur lors de la création des groupes: {e}')


