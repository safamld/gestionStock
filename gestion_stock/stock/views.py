"""
Vues pour la gestion de stock.

Ce module contient toutes les Class-Based Views pour le CRUD complet
des produits, commandes et factures.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.base import View, TemplateView
from django.urls import reverse_lazy
from django.db.models import Sum, Count, Q
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction

from .models import Produit, Commande, Facture, Historique


# ==================== VUES POUR LES PRODUITS ====================

class ProduitListView(ListView):
    """
    Liste tous les produits non supprimés, triés alphabétiquement.
    """
    model = Produit
    template_name = 'stock/produit_list.html'
    context_object_name = 'produits'
    paginate_by = 10
    
    def get_queryset(self):
        """Retourne les produits non supprimés, triés par nom."""
        return Produit.objects.filter(is_deleted=False).order_by('nom_prod')


class ProduitDetailView(DetailView):
    """
    Affiche les détails d'un produit spécifique.
    """
    model = Produit
    template_name = 'stock/produit_detail.html'
    context_object_name = 'produit'
    pk_url_kwarg = 'pk'
    
    def get_context_data(self, **kwargs):
        """Ajoute les commandes associées au contexte."""
        context = super().get_context_data(**kwargs)
        produit = self.get_object()
        # Récupère les commandes non supprimées pour ce produit
        context['commandes'] = produit.commandes.filter(is_deleted=False).order_by('-date_commande')
        context['nombre_commandes'] = context['commandes'].count()
        context['quantite_totale_commandee'] = context['commandes'].aggregate(
            total=Sum('quantite_cmd')
        )['total'] or 0
        return context


class ProduitCreateView(CreateView):
    """
    Crée un nouveau produit.
    """
    model = Produit
    template_name = 'stock/produit_form.html'
    fields = ['nom_prod', 'description', 'quantite', 'prix_unit']
    success_url = reverse_lazy('stock:produit_list')
    
    def form_valid(self, form):
        """Affiche un message de succès."""
        messages.success(self.request, f"Produit '{form.cleaned_data['nom_prod']}' créé avec succès !")
        return super().form_valid(form)


class ProduitUpdateView(UpdateView):
    """
    Modifie un produit existant.
    """
    model = Produit
    template_name = 'stock/produit_form.html'
    fields = ['nom_prod', 'description', 'quantite', 'prix_unit']
    success_url = reverse_lazy('stock:produit_list')
    
    def form_valid(self, form):
        """Affiche un message de succès."""
        messages.success(self.request, f"Produit '{form.cleaned_data['nom_prod']}' modifié avec succès !")
        return super().form_valid(form)


class ProduitDeleteView(DeleteView):
    """
    Supprime un produit (soft delete) avec historique.
    """
    model = Produit
    template_name = 'stock/produit_confirm_delete.html'
    success_url = reverse_lazy('stock:produit_list')
    
    def delete(self, request, *args, **kwargs):
        """Effectue la suppression logique au lieu de supprimer physiquement."""
        self.object = self.get_object()
        nom_produit = self.object.nom_prod
        
        # Enregistrement dans l'historique
        Historique.objects.create(
            type_objet='produit',
            id_objet=self.object.code_prod,
            donnees_supprimees={
                'nom_prod': self.object.nom_prod,
                'quantite': self.object.quantite,
                'prix_unit': self.object.prix_unit,
                'description': self.object.description,
            }
        )
        
        # Suppression logique
        self.object.supprimer_logique()
        messages.success(request, f"Produit '{nom_produit}' supprimé et enregistré dans l'historique !")
        return redirect(self.success_url)


# ==================== VUES POUR LES COMMANDES ====================

class CommandeListView(ListView):
    """
    Liste toutes les commandes non supprimées.
    """
    model = Commande
    template_name = 'stock/commande_list.html'
    context_object_name = 'commandes'
    paginate_by = 15
    
    def get_queryset(self):
        """Retourne les commandes non supprimées, les plus récentes d'abord."""
        return Commande.objects.filter(is_deleted=False).select_related('code_prod').order_by('-date_commande')
    
    def get_context_data(self, **kwargs):
        """Ajoute les statistiques au contexte."""
        context = super().get_context_data(**kwargs)
        commandes = self.get_queryset()
        context['total_commandes'] = commandes.count()
        context['montant_total'] = sum(cmd.montant_commande() for cmd in commandes)
        return context


class CommandeDetailView(DetailView):
    """
    Affiche les détails d'une commande spécifique.
    """
    model = Commande
    template_name = 'stock/commande_detail.html'
    context_object_name = 'commande'
    pk_url_kwarg = 'pk'
    
    def get_context_data(self, **kwargs):
        """Ajoute la facture associée au contexte."""
        context = super().get_context_data(**kwargs)
        commande = self.get_object()
        try:
            context['facture'] = commande.facture
        except Facture.DoesNotExist:
            context['facture'] = None
        return context


class CommandeCreateView(CreateView):
    """
    Crée une nouvelle commande.
    """
    model = Commande
    template_name = 'stock/commande_form.html'
    fields = ['code_prod', 'quantite_cmd']
    success_url = reverse_lazy('stock:commande_list')
    
    def get_context_data(self, **kwargs):
        """Ajoute les produits disponibles au contexte."""
        context = super().get_context_data(**kwargs)
        context['produits'] = Produit.objects.filter(is_deleted=False, quantite__gt=0).order_by('nom_prod')
        return context
    
    @transaction.atomic
    def form_valid(self, form):
        """
        Valide la commande et déduit la quantité du stock.
        """
        response = super().form_valid(form)
        produit = form.cleaned_data['code_prod']
        quantite = form.cleaned_data['quantite_cmd']
        
        # Vérification du stock disponible
        if quantite > produit.quantite:
            messages.error(self.request, f"Stock insuffisant ! Disponible: {produit.quantite}")
            self.object.delete()
            return redirect('stock:commande_create')
        
        # Déduction du stock
        produit.quantite -= quantite
        produit.save()
        
        messages.success(self.request, f"Commande créée avec succès ! Stock de '{produit.nom_prod}' mis à jour.")
        return response


class CommandeUpdateView(UpdateView):
    """
    Modifie une commande existante.
    """
    model = Commande
    template_name = 'stock/commande_form.html'
    fields = ['code_prod', 'quantite_cmd']
    success_url = reverse_lazy('stock:commande_list')
    
    def form_valid(self, form):
        """Affiche un message de succès."""
        messages.success(self.request, f"Commande #{self.object.code_cmd} modifiée avec succès !")
        return super().form_valid(form)


class CommandeDeleteView(DeleteView):
    """
    Supprime une commande (soft delete) avec historique et restaure le stock.
    """
    model = Commande
    template_name = 'stock/commande_confirm_delete.html'
    success_url = reverse_lazy('stock:commande_list')
    
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        """Effectue la suppression logique et restaure le stock."""
        self.object = self.get_object()
        produit = self.object.code_prod
        quantite_cmd = self.object.quantite_cmd
        code_cmd = self.object.code_cmd
        
        # Restauration du stock
        produit.quantite += quantite_cmd
        produit.save()
        
        # Enregistrement dans l'historique
        Historique.objects.create(
            type_objet='commande',
            id_objet=code_cmd,
            donnees_supprimees={
                'produit': produit.nom_prod,
                'quantite_cmd': quantite_cmd,
                'montant': self.object.montant_commande(),
            }
        )
        
        # Suppression logique
        self.object.supprimer_logique()
        messages.success(request, f"Commande #{code_cmd} supprimée et stock restauré !")
        return redirect(self.success_url)


# ==================== VUES POUR LES FACTURES ====================

class FactureListView(ListView):
    """
    Liste toutes les factures non supprimées.
    """
    model = Facture
    template_name = 'stock/facture_list.html'
    context_object_name = 'factures'
    paginate_by = 15
    
    def get_queryset(self):
        """Retourne les factures non supprimées, les plus récentes d'abord."""
        return Facture.objects.filter(is_deleted=False).select_related('commande').order_by('-date_facture')
    
    def get_context_data(self, **kwargs):
        """Ajoute les statistiques au contexte."""
        context = super().get_context_data(**kwargs)
        factures = self.get_queryset()
        context['total_factures'] = factures.count()
        context['montant_total'] = factures.aggregate(Sum('montant_total'))['montant_total__sum'] or 0
        context['payees'] = factures.filter(statut='payee').count()
        return context


class FactureDetailView(DetailView):
    """
    Affiche les détails d'une facture spécifique.
    """
    model = Facture
    template_name = 'stock/facture_detail.html'
    context_object_name = 'facture'
    pk_url_kwarg = 'pk'


class FactureCreateView(CreateView):
    """
    Crée une nouvelle facture à partir d'une commande.
    """
    model = Facture
    template_name = 'stock/facture_form.html'
    fields = ['commande', 'statut']
    success_url = reverse_lazy('stock:facture_list')
    
    def get_context_data(self, **kwargs):
        """Ajoute les commandes sans facture au contexte."""
        context = super().get_context_data(**kwargs)
        # Commandes qui n'ont pas encore de facture
        commandes_disponibles = Commande.objects.filter(
            is_deleted=False,
            facture__isnull=True
        ).select_related('code_prod')
        context['commandes_disponibles'] = commandes_disponibles
        return context
    
    def form_valid(self, form):
        """Calcule automatiquement le montant total de la facture."""
        commande = form.cleaned_data['commande']
        form.instance.montant_total = commande.montant_commande()
        messages.success(self.request, f"Facture créée avec succès pour la commande #{commande.code_cmd} !")
        return super().form_valid(form)


class FactureUpdateView(UpdateView):
    """
    Modifie une facture existante (statut notamment).
    """
    model = Facture
    template_name = 'stock/facture_form.html'
    fields = ['statut']
    success_url = reverse_lazy('stock:facture_list')
    
    def form_valid(self, form):
        """Affiche un message de succès."""
        messages.success(self.request, f"Facture #{self.object.code_facture} modifiée avec succès !")
        return super().form_valid(form)


class FactureDeleteView(DeleteView):
    """
    Supprime une facture (soft delete) avec historique.
    """
    model = Facture
    template_name = 'stock/facture_confirm_delete.html'
    success_url = reverse_lazy('stock:facture_list')
    
    def delete(self, request, *args, **kwargs):
        """Effectue la suppression logique."""
        self.object = self.get_object()
        code_facture = self.object.code_facture
        
        # Enregistrement dans l'historique
        Historique.objects.create(
            type_objet='facture',
            id_objet=code_facture,
            donnees_supprimees={
                'montant_total': self.object.montant_total,
                'statut': self.object.statut,
                'commande_id': self.object.commande.code_cmd,
            }
        )
        
        # Suppression logique
        self.object.supprimer_logique()
        messages.success(request, f"Facture #{code_facture} supprimée et enregistrée dans l'historique !")
        return redirect(self.success_url)


# ==================== VUES POUR L'HISTORIQUE ====================

class HistoriqueListView(ListView):
    """
    Liste tout l'historique des suppressions.
    """
    model = Historique
    template_name = 'stock/historique_list.html'
    context_object_name = 'historiques'
    paginate_by = 20
    
    def get_queryset(self):
        """Retourne les historiques, les plus récents d'abord."""
        return Historique.objects.all().order_by('-date_suppression')
    
    def get_context_data(self, **kwargs):
        """Ajoute les statistiques au contexte."""
        context = super().get_context_data(**kwargs)
        historiques = self.get_queryset()
        context['total_historiques'] = historiques.count()
        context['stats'] = historiques.values('type_objet').annotate(count=Count('id'))
        return context


# ==================== VUES POUR LES STATISTIQUES ====================

class StatistiquesView(TemplateView):
    """
    Dashboard affichant les statistiques globales et les produits les plus commandés.
    """
    template_name = 'stock/statistiques.html'
    
    def get_context_data(self, **kwargs):
        """Prépare toutes les statistiques."""
        context = super().get_context_data(**kwargs)
        
        # Statistiques générales
        context['total_produits'] = Produit.objects.filter(is_deleted=False).count()
        context['total_commandes'] = Commande.objects.filter(is_deleted=False).count()
        context['total_factures'] = Facture.objects.filter(is_deleted=False).count()
        
        # Valeur du stock
        produits = Produit.objects.filter(is_deleted=False)
        context['valeur_stock_totale'] = sum(p.total_valeur_stock() for p in produits)
        
        # Montant total des factures
        factures = Facture.objects.filter(is_deleted=False)
        context['montant_total_factures'] = factures.aggregate(Sum('montant_total'))['montant_total__sum'] or 0
        
        # Produits les plus commandés
        produits_top = (
            Produit.objects
            .filter(is_deleted=False, commandes__is_deleted=False)
            .annotate(
                nombre_commandes=Count('commandes'),
                quantite_totale=Sum('commandes__quantite_cmd')
            )
            .order_by('-nombre_commandes')[:5]
        )
        context['produits_top'] = produits_top
        
        # Factures par statut
        context['factures_par_statut'] = (
            Facture.objects
            .filter(is_deleted=False)
            .values('statut')
            .annotate(count=Count('code_facture'))
        )
        
        # Stock critique (quantité < 10)
        context['stock_critique'] = Produit.objects.filter(
            is_deleted=False,
            quantite__lt=10
        ).order_by('quantite')
        
        return context


# ==================== VUES POUR LE DASHBOARD ====================

class DashboardView(TemplateView):
    """
    Page d'accueil avec vue d'ensemble générale.
    """
    template_name = 'stock/dashboard.html'
    
    def get_context_data(self, **kwargs):
        """Prépare les données pour le dashboard."""
        context = super().get_context_data(**kwargs)
        
        # Nombre d'éléments
        context['total_produits'] = Produit.objects.filter(is_deleted=False).count()
        context['total_commandes'] = Commande.objects.filter(is_deleted=False).count()
        context['total_factures'] = Facture.objects.filter(is_deleted=False).count()
        
        # Dernières commandes
        context['dernieres_commandes'] = Commande.objects.filter(
            is_deleted=False
        ).select_related('code_prod').order_by('-date_commande')[:5]
        
        # Produits en rupture
        context['produits_rupture'] = Produit.objects.filter(
            is_deleted=False,
            quantite=0
        ).order_by('nom_prod')
        
        # Factures non payées
        context['factures_impayees'] = Facture.objects.filter(
            is_deleted=False
        ).exclude(statut='payee').count()
        
        return context
