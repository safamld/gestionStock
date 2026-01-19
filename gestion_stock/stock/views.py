"""
Vues pour la gestion de stock.

Ce module contient toutes les Class-Based Views pour le CRUD complet
des produits, commandes et factures, ainsi que les vues d'authentification
et de dashboard avec routage basé sur les rôles.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.base import View, TemplateView
from django.urls import reverse_lazy
from django.db.models import Sum, Count, Q
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.auth.password_validation import get_password_validators
from django.http import JsonResponse
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils.crypto import get_random_string

from .models import Produit, Commande, Facture, Historique


# ==================== VUES D'AUTHENTIFICATION ====================

def login_view(request):
    """
    Vue de connexion avec routage basé sur les rôles.
    Tous les utilisateurs (admin, agents, fournisseurs) accèdent au dashboard gestion de stock.
    """
    if request.user.is_authenticated:
        # L'utilisateur est déjà connecté
        return redirect('stock:produit_list')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Paramètre "remember me"
            if not remember_me:
                request.session.set_expiry(0)
            
            # Tous les utilisateurs vont au dashboard gestion de stock
            role = "Administrateur" if user.is_staff else "Agent"
            messages.success(request, f'Bienvenue {user.get_full_name() or user.username} ({role})')
            return redirect('stock:produit_list')
        else:
            messages.error(request, 'Identifiant ou mot de passe incorrect.')
    
    return render(request, 'login_blank.html')


def logout_view(request):
    """
    Vue de déconnexion.
    """
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('login')


@login_required(login_url='login')
def agent_dashboard(request):
    """
    Dashboard pour les agents de gestion de stock.
    Affiche les statistiques et les actions rapides selon les permissions.
    """
    # Vérifier que l'utilisateur n'est pas admin
    if request.user.is_staff:
        return redirect('admin:index')
    
    # Récupérer les permissions de l'utilisateur
    user_permissions = set()
    for group in request.user.groups.all():
        for permission in group.permissions.all():
            user_permissions.add(permission.codename)
    
    # Déterminer le rôle de l'utilisateur
    if 'Gestionnaire Stock' in [g.name for g in request.user.groups.all()]:
        user_role = 'Gestionnaire Stock (Accès Complet)'
    elif 'Responsable Commandes' in [g.name for g in request.user.groups.all()]:
        user_role = 'Responsable Commandes'
    elif 'Responsable Factures' in [g.name for g in request.user.groups.all()]:
        user_role = 'Responsable Factures'
    elif 'Lecteur Stock' in [g.name for g in request.user.groups.all()]:
        user_role = 'Lecteur Stock (Lecture Seule)'
    else:
        user_role = 'Utilisateur'
    
    context = {
        'user_role': user_role,
        'permissions': user_permissions,
    }
    
    return render(request, 'dashboard.html', context)


# ==================== VUES POUR LES STATISTIQUES ====================

@login_required(login_url='login')
def statistiques_view(request):
    """
    Vue des statistiques générales du stock.
    """
    if request.user.is_staff:
        return redirect('admin:index')
    
    context = {
        'total_produits': Produit.objects.filter(is_deleted=False).count(),
        'produits_critiques': Produit.objects.filter(is_deleted=False, quantite__lt=10).count(),
        'total_commandes': Commande.objects.filter(is_deleted=False).count(),
        'total_factures': Facture.objects.filter(is_deleted=False).count(),
    }
    return render(request, 'stock/statistiques.html', context)


@login_required(login_url='login')
def historique_view(request):
    """
    Vue de l'historique des actions.
    """
    if request.user.is_staff:
        return redirect('admin:index')
    
    historique = Historique.objects.all().order_by('-date_action')[:50]
    context = {'historique': historique}
    return render(request, 'stock/historique.html', context)


# ==================== VUES POUR LES PRODUITS ====================

@method_decorator(login_required(login_url='login'), name='dispatch')
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


@method_decorator(login_required(login_url='login'), name='dispatch')
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

@method_decorator(login_required(login_url='login'), name='dispatch')
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


# ==================== GESTION DES AGENTS ====================

class AdminOnlyMixin(UserPassesTestMixin):
    """Mixin pour vérifier que l'utilisateur est admin"""
    def test_func(self):
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        messages.error(self.request, "Vous n'avez pas la permission d'accéder à cette page.")
        return redirect('stock:produit_list')


class AgentListView(AdminOnlyMixin, ListView):
    """Affiche la liste de tous les agents (non-admin)"""
    model = User
    template_name = 'stock/agent_list.html'
    context_object_name = 'agents'
    paginate_by = 10
    
    def get_queryset(self):
        # Afficher tous les utilisateurs sauf les admins
        return User.objects.filter(is_staff=False).order_by('username')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = Group.objects.all()
        
        # Ajouter les statistiques pour chaque agent
        # FORCE: Chaque agent commence à 0 pour ses propres données
        # On ne compte pas les commandes/factures, c'est juste pour afficher 0
        agents_list = list(context['agents'])
        
        for agent in agents_list:
            # Réinitialiser COMPLÈTEMENT à 0
            agent.commandes_count = 0
            agent.factures_count = 0
            agent.factures_payees = 0
            agent.factures_validees = 0
            agent.montant_total = 0.0
        
        context['agents'] = agents_list
        return context


class AgentCreateView(AdminOnlyMixin, CreateView):
    """Crée un nouvel agent"""
    model = User
    template_name = 'stock/agent_form.html'
    fields = ['username', 'first_name', 'last_name', 'email']
    success_url = reverse_lazy('stock:agent_list')
    
    def get_context_data(self, **kwargs):
        if not hasattr(self, 'object'):
            self.object = None
        context = super().get_context_data(**kwargs)
        context['show_password_field'] = True
        context['all_groups'] = Group.objects.all()
        return context
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        selected_groups = request.POST.getlist('groups')
        username = request.POST.get('username')
        
        # Vérifier l'unicité du username
        if username and User.objects.filter(username=username).exists():
            form.add_error('username', 'Ce nom d\'utilisateur existe déjà')
            return self.form_invalid(form)
        
        # Valider les mots de passe
        if not password:
            form.add_error(None, 'Le mot de passe est obligatoire')
            return self.form_invalid(form)
        
        if password != password_confirm:
            form.add_error(None, 'Les mots de passe ne correspondent pas')
            return self.form_invalid(form)
        
        if len(password) < 6:
            form.add_error(None, 'Le mot de passe doit contenir au moins 6 caractères')
            return self.form_invalid(form)
        
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = False
            user.set_password(password)
            user.save()
            
            # Ajouter les groupes sélectionnés
            if selected_groups:
                for group_id in selected_groups:
                    try:
                        group = Group.objects.get(id=group_id)
                        user.groups.add(group)
                    except Group.DoesNotExist:
                        pass
            else:
                # Si aucun groupe sélectionné, ajouter "Lecteur Stock" par défaut
                try:
                    lecteur_group = Group.objects.get(name='Lecteur Stock')
                    user.groups.add(lecteur_group)
                except Group.DoesNotExist:
                    pass
            
            messages.success(
                request,
                f"Agent '{user.username}' créé avec succès!"
            )
            return redirect(self.success_url)
        
        return self.form_invalid(form)


class AgentUpdateView(AdminOnlyMixin, UpdateView):
    """Modifie un agent et ses permissions"""
    model = User
    template_name = 'stock/agent_edit.html'
    fields = ['first_name', 'last_name', 'email']
    success_url = reverse_lazy('stock:agent_list')
    
    def get_queryset(self):
        # Permet seulement de modifier les non-admin
        return User.objects.filter(is_staff=False)
    
    def form_valid(self, form):
        """Valide le formulaire et traite les groupes et mot de passe"""
        self.object = form.save()
        
        # Récupérer les groupes sélectionnés
        selected_groups = self.request.POST.getlist('groups')
        
        # Mettre à jour les groupes
        self.object.groups.clear()
        for group_id in selected_groups:
            try:
                group = Group.objects.get(id=group_id)
                self.object.groups.add(group)
            except Group.DoesNotExist:
                pass
        
        # Réinitialiser le mot de passe si demandé
        if self.request.POST.get('reset_password'):
            new_password = get_random_string(length=8, allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            self.object.set_password(new_password)
            self.object.save()
            messages.warning(
                self.request,
                f"Mot de passe réinitialisé pour '{self.object.username}': {new_password}"
            )
        
        messages.success(self.request, f"Agent '{self.object.username}' mis à jour avec succès!")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_groups'] = Group.objects.all()
        if self.object:
            context['user_groups'] = self.object.groups.all()
        return context




class AgentDeleteView(AdminOnlyMixin, DeleteView):
    """Supprime un agent"""
    model = User
    template_name = 'stock/agent_confirm_delete.html'
    success_url = reverse_lazy('stock:agent_list')
    context_object_name = 'agent'
    
    def get_queryset(self):
        # Permet seulement de supprimer les non-admin
        return User.objects.filter(is_staff=False)
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        username = self.object.username
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f"Agent '{username}' supprimé avec succès!")
        return response


class AgentReportView(AdminOnlyMixin, TemplateView):
    """Affiche le rapport avec graphiques des agents"""
    template_name = 'stock/agent_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['agents'] = User.objects.filter(is_staff=False).order_by('username')
        context['groups'] = Group.objects.all()
        return context


@login_required
def agent_graphs_data(request, pk):
    """Retourne les données JSON pour les graphiques d'un agent"""
    from django.http import JsonResponse
    from stock.models import Commande, Facture
    from django.db.models import Sum
    
    # Vérifier que l'utilisateur est admin
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        agent = User.objects.get(pk=pk, is_staff=False)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Agent not found'}, status=404)
    
    # Données globales (on compte toutes les commandes/factures)
    commandes = Commande.objects.filter(is_deleted=False)
    factures = Facture.objects.filter(is_deleted=False)
    
    # Compter par statut de facture
    factures_stats = {
        'brouillon': factures.filter(statut='brouillon').count(),
        'validee': factures.filter(statut='validee').count(),
        'payee': factures.filter(statut='payee').count(),
        'annulee': factures.filter(statut='annulee').count(),
    }
    
    # Montants totaux par statut - avec gestion d'erreur
    try:
        factures_montants = {
            'brouillon': float(factures.filter(statut='brouillon').aggregate(Sum('montant_total'))['montant_total__sum'] or 0),
            'validee': float(factures.filter(statut='validee').aggregate(Sum('montant_total'))['montant_total__sum'] or 0),
            'payee': float(factures.filter(statut='payee').aggregate(Sum('montant_total'))['montant_total__sum'] or 0),
            'annulee': float(factures.filter(statut='annulee').aggregate(Sum('montant_total'))['montant_total__sum'] or 0),
        }
    except (TypeError, ValueError):
        factures_montants = {
            'brouillon': 0.0,
            'validee': 0.0,
            'payee': 0.0,
            'annulee': 0.0,
        }
    
    data = {
        'agent_username': agent.username,
        'agent_full_name': agent.get_full_name() or agent.username,
        'commandes_total': commandes.count(),
        'factures': {
            'total': factures.count(),
            'stats': factures_stats,
            'montants': factures_montants,
        },
        'chart_data': {
            'factures_by_status': {
                'labels': ['Brouillon', 'Validée', 'Payée', 'Annulée'],
                'data': [
                    factures_stats['brouillon'],
                    factures_stats['validee'],
                    factures_stats['payee'],
                    factures_stats['annulee'],
                ],
                'backgroundColor': ['#FCD34D', '#A78BFA', '#34D399', '#EF4444'],
            },
            'montants_by_status': {
                'labels': ['Brouillon', 'Validée', 'Payée', 'Annulée'],
                'data': [
                    factures_montants['brouillon'],
                    factures_montants['validee'],
                    factures_montants['payee'],
                    factures_montants['annulee'],
                ],
                'backgroundColor': ['#FCD34D', '#A78BFA', '#34D399', '#EF4444'],
            },
        }
    }
    
    return JsonResponse(data)
