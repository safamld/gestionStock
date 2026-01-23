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
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils.crypto import get_random_string

from .models import Produit, Commande, Facture, Historique, Fournisseur, MontantAgent


# ==================== MIXINS ====================

class AdminOnlyMixin(UserPassesTestMixin):
    """Mixin pour vérifier que l'utilisateur est admin"""
    def test_func(self):
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        messages.error(self.request, "Vous n'avez pas la permission d'accéder à cette page.")
        return redirect('stock:produit_list')


# ==================== VUES D'AUTHENTIFICATION ====================

def login_view(request):
    """
    Vue de connexion avec routage basé sur les rôles.
    - Admin / Agent → Dashboard gestion de stock
    - Fournisseur → Dashboard fournisseur
    """
    if request.user.is_authenticated:
        # L'utilisateur est déjà connecté - router selon le rôle
        user_groups = request.user.groups.values_list('name', flat=True)
        if 'Fournisseur' in user_groups:
            return redirect('stock:fournisseur_dashboard')
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
            
            # Router selon le rôle
            user_groups = user.groups.values_list('name', flat=True)
            
            if 'Fournisseur' in user_groups:
                # Fournisseur
                role = "Fournisseur"
                messages.success(request, f'Bienvenue {user.get_full_name() or user.username} ({role})')
                return redirect('stock:fournisseur_dashboard')
            else:
                # Admin ou Agent
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
@method_decorator(login_required(login_url='login'), name='dispatch')
class ProduitListView(ListView):
    """
    Liste les produits selon le rôle :
    - FOURNISSEUR: Voir SEULEMENT ses propres produits
    - AGENT/ADMIN: Voir TOUS les produits de tous les fournisseurs
    """
    model = Produit
    template_name = 'stock/produit_list.html'
    context_object_name = 'produits'
    paginate_by = 10
    
    def get_queryset(self):
        """Retourne les produits selon le rôle de l'utilisateur."""
        user_groups = self.request.user.groups.values_list('name', flat=True)
        
        # Si c'est un fournisseur, afficher SEULEMENT ses produits
        if 'Fournisseur' in user_groups:
            try:
                fournisseur = self.request.user.fournisseur
                return Produit.objects.filter(
                    fournisseur=fournisseur,
                    is_deleted=False
                ).order_by('nom_prod')
            except:
                return Produit.objects.none()
        
        # Sinon (agent/admin), afficher TOUS les produits
        return Produit.objects.filter(is_deleted=False).order_by('nom_prod')
    
    def get_context_data(self, **kwargs):
        """Ajoute les infos d'édition au contexte pour les fournisseurs."""
        context = super().get_context_data(**kwargs)
        user_groups = self.request.user.groups.values_list('name', flat=True)
        context['is_fournisseur'] = 'Fournisseur' in user_groups
        
        # Calculer le total de stock
        produits = self.get_queryset()
        context['total_stock'] = sum(p.quantite for p in produits) if produits else 0
        
        return context


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


class ProduitCreateView(AdminOnlyMixin, CreateView):
    """
    Crée un nouveau produit - SEULEMENT POUR L'ADMIN.
    Les fournisseurs ajoutent leurs produits via 'ajouter_produit_fournisseur'.
    """
    model = Produit
    template_name = 'stock/produit_form.html'
    fields = ['nom_prod', 'description', 'quantite', 'prix_unit']
    success_url = reverse_lazy('stock:produit_list')
    
    def form_valid(self, form):
        """Affiche un message de succès."""
        messages.success(self.request, f"Produit '{form.cleaned_data['nom_prod']}' créé avec succès !")
        return super().form_valid(form)


class ProduitUpdateView(AdminOnlyMixin, UpdateView):
    """
    Modifie un produit existant - SEULEMENT POUR L'ADMIN.
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
    - Fournisseur: Voir uniquement ses commandes (produits)
    - Agent: Voir uniquement LEURS commandes
    - Admin: Voir toutes les commandes
    """
    model = Commande
    template_name = 'stock/commande_list.html'
    context_object_name = 'commandes'
    paginate_by = 15
    
    def get_queryset(self):
        """Retourne les commandes non supprimées, les plus récentes d'abord."""
        user_groups = self.request.user.groups.values_list('name', flat=True)
        queryset = Commande.objects.filter(is_deleted=False).select_related('code_prod').order_by('-date_commande')
        
        # Si l'utilisateur est un fournisseur, filtrer par ses produits
        if 'Fournisseur' in user_groups:
            try:
                fournisseur = self.request.user.fournisseur
                queryset = queryset.filter(code_prod__fournisseur=fournisseur)
            except:
                queryset = Commande.objects.none()
        # Si l'utilisateur est un AGENT, filtrer par ses commandes uniquement
        elif 'Gestionnaire Stock' in user_groups or 'Responsable Commandes' in user_groups:
            queryset = queryset.filter(agent_utilisateur=self.request.user)
        
        return queryset
    
    def get_queryset(self):
        """Retourne les commandes non supprimées, les plus récentes d'abord."""
        user_groups = self.request.user.groups.values_list('name', flat=True)
        queryset = Commande.objects.filter(is_deleted=False).select_related('code_prod').order_by('-date_commande')
        
        # Si l'utilisateur est un fournisseur, filtrer par ses produits
        if 'Fournisseur' in user_groups:
            try:
                fournisseur = self.request.user.fournisseur
                # Récupérer les commandes contenant les produits de ce fournisseur
                queryset = queryset.filter(code_prod__fournisseur=fournisseur)
            except:
                queryset = Commande.objects.none()
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Ajoute les statistiques au contexte."""
        context = super().get_context_data(**kwargs)
        commandes = self.get_queryset()
        context['total_commandes'] = commandes.count()
        context['montant_total'] = sum(cmd.montant_commande() for cmd in commandes)
        
        # Statistiques par agent (si FOURNISSEUR)
        user_groups = self.request.user.groups.values_list('name', flat=True)
        if 'Fournisseur' in user_groups:
            # Récupérer les agents qui ont commandé les produits de ce fournisseur
            try:
                fournisseur = self.request.user.fournisseur
                # Récupérer tous les agents uniques qui ont commandé les produits de ce fournisseur
                agents_with_commandes = Commande.objects.filter(
                    code_prod__fournisseur=fournisseur,
                    is_deleted=False
                ).values_list('agent_utilisateur', flat=True).distinct()
                
                agents_stats = []
                for agent_id in agents_with_commandes:
                    agent = User.objects.get(id=agent_id)
                    
                    # Commandes de cet agent pour ce fournisseur
                    agent_commandes = Commande.objects.filter(
                        agent_utilisateur=agent,
                        code_prod__fournisseur=fournisseur,
                        is_deleted=False
                    )
                    agent_commandes_count = agent_commandes.count()
                    
                    # Factures de cet agent pour ce fournisseur
                    agent_factures = Facture.objects.filter(
                        commande__agent_utilisateur=agent,
                        commande__code_prod__fournisseur=fournisseur,
                        is_deleted=False
                    )
                    agent_factures_count = agent_factures.count()
                    
                    agents_stats.append({
                        'agent': agent,
                        'commandes_count': agent_commandes_count if agent_commandes_count > 0 else 0,
                        'factures_count': agent_factures_count if agent_factures_count > 0 else 0,
                        'montant_total': sum(cmd.montant_commande() for cmd in agent_commandes) if agent_commandes_count > 0 else 0
                    })
                
                context['agents_stats'] = agents_stats
            except:
                context['agents_stats'] = []
        
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
    Crée automatiquement une facture associée.
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
        La facture est créée automatiquement via le signal Django.
        """
        form.instance.agent_utilisateur = self.request.user
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
        
        messages.success(
            self.request, 
            f"Commande #{self.object.code_cmd} créée avec succès ! "
            f"Facture générée automatiquement ({quantite * produit.prix_unit}€)"
        )
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
    - Fournisseur: Voir uniquement les factures de ses produits
    - Agent: Voir uniquement LEURS factures
    - Admin: Voir toutes les factures
    """
    model = Facture
    template_name = 'stock/facture_list.html'
    context_object_name = 'factures'
    paginate_by = 15
    
    def get_queryset(self):
        """Retourne les factures non supprimées, les plus récentes d'abord."""
        user_groups = self.request.user.groups.values_list('name', flat=True)
        queryset = Facture.objects.filter(is_deleted=False).select_related('commande').order_by('-date_facture')
        
        # Si l'utilisateur est un fournisseur, filtrer par ses produits
        if 'Fournisseur' in user_groups:
            try:
                fournisseur = self.request.user.fournisseur
                queryset = queryset.filter(commande__code_prod__fournisseur=fournisseur)
            except:
                queryset = Facture.objects.none()
        # Si l'utilisateur est un AGENT, filtrer par ses factures uniquement
        elif 'Gestionnaire Stock' in user_groups or 'Responsable Commandes' in user_groups:
            queryset = queryset.filter(agent_utilisateur=self.request.user)
        # Sinon (Admin): voir toutes les factures
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Ajoute les statistiques au contexte."""
        context = super().get_context_data(**kwargs)
        factures = self.get_queryset()
        context['total_factures'] = factures.count()
        context['montant_total'] = factures.aggregate(Sum('montant_total'))['montant_total__sum'] or 0
        context['payees'] = factures.filter(statut='payee').count() if factures.count() > 0 else 0
        context['non_payees'] = factures.filter(statut='non_payee').count() if factures.count() > 0 else 0
        
        # Statistiques par agent (si FOURNISSEUR)
        user_groups = self.request.user.groups.values_list('name', flat=True)
        if 'Fournisseur' in user_groups:
            try:
                fournisseur = self.request.user.fournisseur
                agents_with_factures = Facture.objects.filter(
                    commande__code_prod__fournisseur=fournisseur,
                    is_deleted=False
                ).values_list('commande__agent_utilisateur', flat=True).distinct()
                
                agents_stats = []
                for agent_id in agents_with_factures:
                    if agent_id:
                        agent = User.objects.get(id=agent_id)
                        agent_factures = Facture.objects.filter(
                            commande__agent_utilisateur=agent,
                            commande__code_prod__fournisseur=fournisseur,
                            is_deleted=False
                        )
                        agent_factures_count = agent_factures.count()
                        agent_payees = agent_factures.filter(statut='payee').count() if agent_factures_count > 0 else 0
                        agent_non_payees = agent_factures.filter(statut='non_payee').count() if agent_factures_count > 0 else 0
                        
                        agents_stats.append({
                            'agent': agent,
                            'factures_count': agent_factures_count if agent_factures_count > 0 else 0,
                            'payees': agent_payees if agent_payees > 0 else 0,
                            'non_payees': agent_non_payees if agent_non_payees > 0 else 0,
                            'montant_total': agent_factures.aggregate(Sum('montant_total'))['montant_total__sum'] or 0
                        })
                
                context['agents_stats'] = agents_stats
            except:
                context['agents_stats'] = []
        
        return context


class FactureDetailView(DetailView):
    """
    Affiche les détails d'une facture spécifique.
    - Fournisseur: Voir les factures de ses produits
    - Agent: Voir uniquement LEURS factures
    - Admin: Voir toutes les factures
    """
    model = Facture
    template_name = 'stock/facture_detail.html'
    context_object_name = 'facture'
    pk_url_kwarg = 'pk'
    
    def get_queryset(self):
        """Filtrer les factures accessibles à l'utilisateur."""
        user_groups = self.request.user.groups.values_list('name', flat=True)
        queryset = Facture.objects.filter(is_deleted=False)
        
        # Si l'utilisateur est un fournisseur, filtrer par ses produits
        if 'Fournisseur' in user_groups:
            try:
                fournisseur = self.request.user.fournisseur
                queryset = queryset.filter(commande__code_prod__fournisseur=fournisseur)
            except:
                queryset = Facture.objects.none()
        # Si l'utilisateur est un AGENT, filtrer par ses factures uniquement
        elif 'Gestionnaire Stock' in user_groups or 'Responsable Commandes' in user_groups:
            queryset = queryset.filter(agent_utilisateur=self.request.user)
        
        return queryset


class FactureCreateView(AdminOnlyMixin, CreateView):
    """
    Crée une nouvelle facture à partir d'une commande.
    Réservé aux administrateurs uniquement.
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
    Réservé à l'ADMIN uniquement - Les agents ne peuvent pas modifier.
    """
    model = Facture
    template_name = 'stock/facture_form.html'
    fields = ['statut']
    success_url = reverse_lazy('stock:facture_list')
    
    def get(self, request, *args, **kwargs):
        """Vérifier les permissions avant d'afficher le formulaire."""
        user_groups = request.user.groups.values_list('name', flat=True)
        if 'Gestionnaire Stock' in user_groups or 'Responsable Commandes' in user_groups:
            messages.error(request, "Vous n'avez pas la permission de modifier les factures.")
            return redirect('stock:facture_list')
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """Vérifier les permissions avant de sauvegarder."""
        user_groups = request.user.groups.values_list('name', flat=True)
        if 'Gestionnaire Stock' in user_groups or 'Responsable Commandes' in user_groups:
            messages.error(request, "Vous n'avez pas la permission de modifier les factures.")
            return redirect('stock:facture_list')
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Affiche un message de succès."""
        messages.success(self.request, f"Facture #{self.object.code_facture} modifiée avec succès !")
        return super().form_valid(form)


class FactureDeleteView(DeleteView):
    """
    Supprime une facture (soft delete) avec historique.
    Réservé à l'ADMIN uniquement - Les agents ne peuvent pas supprimer.
    """
    model = Facture
    template_name = 'stock/facture_confirm_delete.html'
    success_url = reverse_lazy('stock:facture_list')
    
    def get(self, request, *args, **kwargs):
        """Vérifier les permissions avant d'afficher la page de confirmation."""
        user_groups = request.user.groups.values_list('name', flat=True)
        if 'Gestionnaire Stock' in user_groups or 'Responsable Commandes' in user_groups:
            messages.error(request, "Vous n'avez pas la permission de supprimer les factures.")
            return redirect('stock:facture_list')
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """Vérifier les permissions avant de supprimer."""
        user_groups = request.user.groups.values_list('name', flat=True)
        if 'Gestionnaire Stock' in user_groups or 'Responsable Commandes' in user_groups:
            messages.error(request, "Vous n'avez pas la permission de supprimer les factures.")
            return redirect('stock:facture_list')
        return super().post(request, *args, **kwargs)
    
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
                'commande_id': self.object.commande.code_cmd if self.object.commande else None,
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

# ==================== DASHBOARDS AGENT ET FOURNISSEUR ====================

@login_required(login_url='login')
def agent_dashboard_view(request):
    """
    Dashboard pour l'agent: voir les produits et passer des commandes.
    L'agent NE PEUT PAS ajouter de produits.
    """
    # Récupérer le groupe de l'utilisateur
    user_groups = request.user.groups.values_list('name', flat=True)
    
    # Vérifier que l'utilisateur est un agent (pas admin)
    if request.user.is_staff:
        return redirect('admin:index')
    
    # Récupérer les produits disponibles (pas supprimés)
    produits = Produit.objects.filter(is_deleted=False)
    
    # Récupérer les commandes de cet agent (avec relations optimisées)
    commandes_agent = Commande.objects.filter(
        agent_utilisateur=request.user, 
        is_deleted=False
    ).select_related('code_prod', 'code_prod__fournisseur').order_by('-date_cmd')
    
    # Récupérer les factures de cet agent (avec relations optimisées)
    factures_agent = Facture.objects.filter(
        agent_utilisateur=request.user, 
        is_deleted=False
    ).select_related('commande', 'commande__code_prod', 'commande__code_prod__fournisseur').order_by('-date_facture')
    
    # Calculer les statistiques
    montant_total_commandes = sum([cmd.montant_commande() for cmd in commandes_agent])
    montant_total_factures = factures_agent.aggregate(Sum('montant_total'))['montant_total__sum'] or 0
    
    # Récupérer ou créer le montant de l'agent
    try:
        montant_agent = MontantAgent.objects.get(agent_utilisateur=request.user)
    except MontantAgent.DoesNotExist:
        montant_agent = MontantAgent.objects.create(agent_utilisateur=request.user, montant_total=0.0)
    
    context = {
        'produits': produits,
        'commandes': commandes_agent,
        'factures': factures_agent,
        'montant_total_commandes': montant_total_commandes,
        'montant_total_factures': montant_total_factures,
        'montant_agent': montant_agent,
        'nombre_commandes': commandes_agent.count(),
        'nombre_factures': factures_agent.count(),
    }
    
    return render(request, 'stock/agent_dashboard.html', context)


@login_required(login_url='login')
def passer_commande_view(request, produit_id):
    """
    Vue pour passer une commande de produit.
    La facture est créée automatiquement via le signal Django.
    """
    if request.user.is_staff:
        return redirect('admin:index')
    
    produit = get_object_or_404(Produit, code_prod=produit_id, is_deleted=False)
    
    if request.method == 'POST':
        quantite = request.POST.get('quantite', 1)
        try:
            quantite = int(quantite)
            if quantite <= 0:
                raise ValueError("La quantité doit être positive")
        except (ValueError, TypeError):
            messages.error(request, "Quantité invalide")
            return redirect('stock:agent_dashboard')
        
        # Vérifier que la quantité demandée est disponible
        if quantite > produit.quantite:
            messages.error(request, f"Stock insuffisant. Disponible: {produit.quantite}")
            return redirect('stock:agent_dashboard')
        
        try:
            # Créer la commande (la facture sera créée automatiquement par le signal)
            with transaction.atomic():
                # 1. Créer la commande
                commande = Commande.objects.create(
                    code_prod=produit,
                    quantite_cmd=quantite,
                    agent_utilisateur=request.user
                )
                
                # 2. Réduire la quantité en stock
                produit.quantite -= quantite
                produit.save()
                
                # Succès
                messages.success(
                    request,
                    f'✓ Commande #{commande.code_cmd} créée avec succès! '
                    f'Facture générée automatiquement: {quantite * produit.prix_unit}€'
                )
        
        except Exception as e:
            messages.error(request, f"Erreur lors de la création de la commande: {str(e)}")
            return redirect('stock:agent_dashboard')
        
        return redirect('stock:agent_dashboard')
    
    return render(request, 'stock/passer_commande.html', {'produit': produit})


def home_view(request):
    """
    Vue d'accueil principale du portail.
    Affiche les options pour Admin, Agent et Fournisseur.
    """
    return render(request, 'stock/home.html')


def fournisseur_login_view(request):
    """
    Vue de login pour les fournisseurs (sans authentification Django requise).
    """
    print(f"\n=== FOURNISSEUR LOGIN REQUEST ===")
    print(f"Méthode: {request.method}")
    print(f"POST data: {request.POST}")
    
    if request.method == 'POST':
        nom_fournisseur = request.POST.get('nom_fournisseur', '').strip()
        mot_de_passe = request.POST.get('mot_de_passe', '').strip()
        
        print(f"\nDEBUG Login")
        print(f"  Nom reçu: '{nom_fournisseur}'")
        print(f"  Mdp reçu: '{mot_de_passe}'")
        print(f"  Longueur nom: {len(nom_fournisseur)}")
        print(f"  Longueur mdp: {len(mot_de_passe)}")
        
        try:
            # Chercher le fournisseur (case-insensitive)
            fournisseur = Fournisseur.objects.get(nom_fournisseur__iexact=nom_fournisseur)
            print(f"\n✓ Fournisseur trouvé: {fournisseur.nom_fournisseur}")
            print(f"  Code: {fournisseur.code_fournisseur}")
            print(f"  Mdp en BD: '{fournisseur.mot_de_passe}'")
            
            # Vérifier le mot de passe
            if fournisseur.mot_de_passe:
                mdp_bd = fournisseur.mot_de_passe.strip()
                print(f"  Comparaison: '{mot_de_passe}' == '{mdp_bd}'")
                print(f"  Match: {mot_de_passe == mdp_bd}")
                
                if mdp_bd == mot_de_passe:
                    # Stocker le code fournisseur dans la session
                    request.session['fournisseur_id'] = fournisseur.code_fournisseur
                    print(f"✓ LOGIN RÉUSSI")
                    messages.success(request, f"Bienvenue {fournisseur.nom_fournisseur}!")
                    return redirect('stock:fournisseur_dashboard')
                else:
                    print(f"✗ Mot de passe ne correspond pas")
                    messages.error(request, "Mot de passe incorrect.")
            else:
                print(f"✗ Mot de passe vide en BD")
                messages.error(request, "Mot de passe non configuré.")
        
        except Fournisseur.DoesNotExist:
            print(f"✗ Fournisseur '{nom_fournisseur}' non trouvé")
            # Afficher tous les noms disponibles
            noms = Fournisseur.objects.values_list('nom_fournisseur', flat=True)
            print(f"  Fournisseurs disponibles: {list(noms)}")
            messages.error(request, "Nom du fournisseur non trouvé.")
    
    print(f"=== FIN FOURNISSEUR LOGIN ===\n")
    return render(request, 'stock/fournisseur_login.html')
    
    return render(request, 'stock/fournisseur_login.html')


def fournisseur_logout_view(request):
    """
    Vue pour déconnecter le fournisseur.
    """
    if 'fournisseur_id' in request.session:
        del request.session['fournisseur_id']
    messages.success(request, "Vous êtes déconnecté.")
    return redirect('stock:fournisseur_login')


def fournisseur_dashboard_view(request):
    """
    Dashboard pour le fournisseur: voir et gérer ses produits,
    voir les commandes des agents, marquer les factures comme payées.
    """
    # Vérifier que l'utilisateur est authentifié et dans le groupe Fournisseur
    if not request.user.is_authenticated:
        messages.error(request, "Vous devez être connecté pour accéder au dashboard.")
        return redirect('login')
    
    user_groups = request.user.groups.values_list('name', flat=True)
    if 'Fournisseur' not in user_groups:
        messages.error(request, "Accès refusé. Vous n'êtes pas un fournisseur.")
        return redirect('login')
    
    # Récupérer le fournisseur associé à cet utilisateur
    try:
        fournisseur = request.user.fournisseur
    except:
        messages.error(request, "Fournisseur non trouvé.")
        return redirect('login')
    
    # Récupérer les produits du fournisseur
    produits_fournisseur = Produit.objects.filter(fournisseur=fournisseur, is_deleted=False)
    
    # Récupérer les commandes pour les produits du fournisseur
    commandes_fournisseur = Commande.objects.filter(
        code_prod__fournisseur=fournisseur,
        is_deleted=False
    ).select_related('code_prod', 'agent_utilisateur')
    
    # Récupérer les factures associées
    factures_fournisseur = Facture.objects.filter(
        commande__code_prod__fournisseur=fournisseur,
        is_deleted=False
    ).select_related('commande', 'agent_utilisateur')
    
    # Statistiques
    total_produits = produits_fournisseur.count()
    total_commandes = commandes_fournisseur.count()
    montant_total_commandes = sum([cmd.montant_commande() for cmd in commandes_fournisseur])
    montant_payees = factures_fournisseur.filter(statut='payee').aggregate(Sum('montant_total'))['montant_total__sum'] or 0
    montant_non_payees = factures_fournisseur.filter(statut__in=['brouillon', 'validee']).aggregate(Sum('montant_total'))['montant_total__sum'] or 0
    
    context = {
        'fournisseur': fournisseur,
        'produits': produits_fournisseur,
        'commandes': commandes_fournisseur,
        'factures': factures_fournisseur,
        'total_produits': total_produits,
        'total_commandes': total_commandes,
        'montant_total_commandes': montant_total_commandes,
        'montant_payees': montant_payees,
        'montant_non_payees': montant_non_payees,
    }
    
    return render(request, 'stock/fournisseur_dashboard.html', context)


@csrf_protect
def ajouter_produit_fournisseur_view(request):
    """
    Vue pour que le fournisseur ajoute un produit.
    """
    print(f"\n🔵 AJOUTER PRODUIT - DEBUG")
    print(f"  User: {request.user.username if request.user.is_authenticated else 'NOT AUTHENTICATED'}")
    print(f"  Is authenticated: {request.user.is_authenticated}")
    
    # Vérifier que l'utilisateur est authentifié et dans le groupe Fournisseur
    if not request.user.is_authenticated:
        print(f"❌ User NOT authenticated")
        messages.error(request, "Vous devez être connecté pour accéder à cette page.")
        return redirect('login')
    
    user_groups = request.user.groups.values_list('name', flat=True)
    print(f"  Groups: {list(user_groups)}")
    
    if 'Fournisseur' not in user_groups:
        print(f"❌ User NOT in Fournisseur group")
        messages.error(request, "Accès refusé. Vous n'êtes pas un fournisseur.")
        return redirect('login')
    
    # Récupérer le fournisseur associé à cet utilisateur
    try:
        fournisseur = request.user.fournisseur
        print(f"✓ Fournisseur trouvé: {fournisseur.nom_fournisseur}")
    except:
        print(f"❌ Fournisseur NOT found for user {request.user.username}")
        messages.error(request, "Fournisseur non trouvé.")
        return redirect('login')
    
    if request.method == 'POST':
        nom_prod = request.POST.get('nom_prod', '').strip()
        description = request.POST.get('description', '').strip()
        prix_unit = request.POST.get('prix_unit')
        quantite = request.POST.get('quantite', 0)
        photo = request.FILES.get('photo')
        
        # Vérifications
        if not nom_prod:
            messages.error(request, "Le nom du produit est obligatoire.")
            return render(request, 'stock/ajouter_produit_fournisseur.html', {'fournisseur': fournisseur})
        
        # Vérifier si le produit existe déjà pour ce fournisseur
        if Produit.objects.filter(fournisseur=fournisseur, nom_prod=nom_prod, is_deleted=False).exists():
            messages.error(request, f'Un produit "{nom_prod}" existe déjà pour ce fournisseur.')
            return render(request, 'stock/ajouter_produit_fournisseur.html', {'fournisseur': fournisseur})
        
        try:
            prix_unit = float(prix_unit)
            quantite = int(quantite)
            
            # Créer le produit
            produit = Produit.objects.create(
                nom_prod=nom_prod,
                description=description,
                prix_unit=prix_unit,
                quantite=quantite,
                fournisseur=fournisseur,
                photo=photo if photo else None
            )
            
            messages.success(request, f'Produit "{nom_prod}" ajouté avec succès!')
            return redirect('stock:fournisseur_dashboard')
        
        except ValueError as e:
            messages.error(request, f"Erreur: Prix ou quantité invalide. {e}")
            return render(request, 'stock/ajouter_produit_fournisseur.html', {'fournisseur': fournisseur})
    
    return render(request, 'stock/ajouter_produit_fournisseur.html', {'fournisseur': fournisseur})


@csrf_protect
def modifier_produit_fournisseur_view(request, produit_id):
    """
    Vue pour que le fournisseur modifie un de ses produits.
    """
    # Vérifier que l'utilisateur est un fournisseur connecté
    if not request.user.is_authenticated or not request.user.groups.filter(name='Fournisseur').exists():
        messages.error(request, "Vous devez être un fournisseur connecté pour accéder à cette page.")
        return redirect('stock:login')
    
    try:
        fournisseur = Fournisseur.objects.get(user=request.user)
        produit = Produit.objects.get(code_prod=produit_id, fournisseur=fournisseur, is_deleted=False)
    except (Fournisseur.DoesNotExist, Produit.DoesNotExist):
        messages.error(request, "Produit non trouvé ou accès refusé.")
        return redirect('stock:fournisseur_dashboard')
    
    if request.method == 'POST':
        nom_prod = request.POST.get('nom_prod')
        description = request.POST.get('description')
        prix_unit = request.POST.get('prix_unit')
        quantite = request.POST.get('quantite', 0)
        photo = request.FILES.get('photo')
        
        try:
            prix_unit = float(prix_unit)
            quantite = int(quantite)
            
            # Mettre à jour le produit
            produit.nom_prod = nom_prod
            produit.description = description
            produit.prix_unit = prix_unit
            produit.quantite = quantite
            
            if photo:
                produit.photo = photo
            
            produit.save()
            
            messages.success(request, f'Produit "{nom_prod}" modifié avec succès!')
            return redirect('stock:fournisseur_dashboard')
        
        except (ValueError, TypeError) as e:
            messages.error(request, f"Erreur: {e}")
    
    return render(request, 'stock/modifier_produit_fournisseur.html', {
        'fournisseur': fournisseur,
        'produit': produit
    })


def supprimer_produit_fournisseur_view(request, produit_id):
    """
    Vue pour que le fournisseur supprime un produit (soft delete).
    """
    # Vérifier que l'utilisateur est un fournisseur connecté
    if not request.user.is_authenticated or not request.user.groups.filter(name='Fournisseur').exists():
        messages.error(request, "Vous devez être un fournisseur connecté pour accéder à cette page.")
        return redirect('stock:login')
    
    try:
        fournisseur = Fournisseur.objects.get(user=request.user)
        produit = Produit.objects.get(code_prod=produit_id, fournisseur=fournisseur, is_deleted=False)
        
        # Soft delete du produit
        produit.supprimer_logique()
        messages.success(request, f'Produit "{produit.nom_prod}" supprimé avec succès.')
    
    except (Fournisseur.DoesNotExist, Produit.DoesNotExist):
        messages.error(request, "Produit non trouvé ou accès refusé.")
    
    return redirect('stock:fournisseur_dashboard')


def marquer_facture_payee_view(request, facture_id):
    """
    Vue pour que le fournisseur marque une facture comme payée.
    """
    # Vérifier que l'utilisateur est authentifié et dans le groupe Fournisseur
    if not request.user.is_authenticated:
        messages.error(request, "Vous devez être connecté pour accéder à cette page.")
        return redirect('login')
    
    user_groups = request.user.groups.values_list('name', flat=True)
    if 'Fournisseur' not in user_groups:
        messages.error(request, "Accès refusé. Vous n'êtes pas un fournisseur.")
        return redirect('login')
    
    try:
        fournisseur = request.user.fournisseur
        facture = Facture.objects.get(code_facture=facture_id, commande__code_prod__fournisseur=fournisseur)
        
        # Vérifier que la facture n'est pas déjà payée
        if facture.statut == 'payee':
            messages.warning(request, f'Cette facture est déjà marquée comme payée.')
        else:
            # Marquer comme payée
            facture.statut = 'payee'
            facture.save()
            messages.success(request, f'Facture #{facture.code_facture} marquée comme payée avec succès!')
    
    except Facture.DoesNotExist:
        messages.error(request, "Facture non trouvée ou accès refusé.")
    except Exception as e:
        messages.error(request, f"Erreur lors du traitement: {e}")
    
    return redirect('stock:fournisseur_dashboard')


def detailler_facture_fournisseur_view(request, facture_id):
    """
    Vue pour afficher les détails d'une facture depuis le dashboard fournisseur.
    """
    # Vérifier que l'utilisateur est authentifié et dans le groupe Fournisseur
    if not request.user.is_authenticated:
        messages.error(request, "Vous devez être connecté pour accéder à cette page.")
        return redirect('login')
    
    user_groups = request.user.groups.values_list('name', flat=True)
    if 'Fournisseur' not in user_groups:
        messages.error(request, "Accès refusé. Vous n'êtes pas un fournisseur.")
        return redirect('login')
    
    try:
        fournisseur = request.user.fournisseur
        facture = Facture.objects.get(code_facture=facture_id, commande__code_prod__fournisseur=fournisseur)
        commande = facture.commande
        
        context = {
            'facture': facture,
            'commande': commande,
            'fournisseur': fournisseur,
        }
        
        return render(request, 'stock/detailler_facture_fournisseur.html', context)
    
    except Facture.DoesNotExist:
        messages.error(request, "Facture non trouvée ou accès refusé.")
        return redirect('stock:fournisseur_dashboard')


def marquer_commande_payee_view(request, commande_id):
    """
    Vue pour que le fournisseur confirme que l'agent a payé une commande.
    """
    # Vérifier que l'utilisateur est authentifié et dans le groupe Fournisseur
    if not request.user.is_authenticated:
        messages.error(request, "Vous devez être connecté pour accéder à cette page.")
        return redirect('login')
    
    user_groups = request.user.groups.values_list('name', flat=True)
    if 'Fournisseur' not in user_groups:
        messages.error(request, "Accès refusé. Vous n'êtes pas un fournisseur.")
        return redirect('login')
    
    try:
        fournisseur = request.user.fournisseur
        commande = Commande.objects.get(code_cmd=commande_id, code_prod__fournisseur=fournisseur)
        
        # Vérifier que la commande n'est pas déjà confirmée
        if commande.paiement_confirme:
            messages.warning(request, f'Le paiement de cette commande a déjà été confirmé le {commande.date_paiement|date:"d/m/Y à H:i"}.')
        else:
            # Confirmer le paiement
            commande.confirmer_paiement()
            messages.success(request, f'✅ Paiement de la commande #{commande.code_cmd} confirmé avec succès!')
    
    except Commande.DoesNotExist:
        messages.error(request, "Commande non trouvée ou accès refusé.")
    except Exception as e:
        messages.error(request, f"Erreur lors du traitement: {e}")
    
    return redirect('stock:fournisseur_dashboard')


# ==================== GESTION ANCIENNE (À GARDER POUR COMPATIBILITÉ) ====================

def marquer_facture_payee_view_old(request, facture_id):
    """
    Vue ANCIENNE pour que le fournisseur marque une facture comme payée.
    """
    # Vérifier que le fournisseur est connecté via session
    fournisseur_id = request.session.get('fournisseur_id')
    if not fournisseur_id:
        messages.error(request, "Vous devez être connecté pour accéder à cette page.")
        return redirect('stock:fournisseur_login')
    
    try:
        fournisseur = Fournisseur.objects.get(code_fournisseur=fournisseur_id)
        facture = Facture.objects.get(code_facture=facture_id, commande__code_prod__fournisseur=fournisseur)
        
        # Marquer comme payée
        facture.marquer_payee()
        messages.success(request, f'Facture #{facture.code_facture} marquée comme payée.')
    
    except (Fournisseur.DoesNotExist, Facture.DoesNotExist):
        messages.error(request, "Facture non trouvée ou accès refusé.")
    
    return redirect('stock:fournisseur_dashboard')


# ==================== GESTION DES FOURNISSEURS (ADMIN) ====================

class FournisseurListView(AdminOnlyMixin, ListView):
    """Affiche la liste de tous les fournisseurs"""
    model = Fournisseur
    template_name = 'stock/fournisseur_list.html'
    context_object_name = 'fournisseurs'
    paginate_by = 10
    
    def get_queryset(self):
        return Fournisseur.objects.all().order_by('code_fournisseur')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Ajouter les statistiques pour chaque fournisseur
        fournisseurs_list = list(context['fournisseurs'])
        
        for fournisseur in fournisseurs_list:
            fournisseur.produits_count = Produit.objects.filter(
                fournisseur=fournisseur,
                is_deleted=False
            ).count()
            fournisseur.commandes_count = Commande.objects.filter(
                code_prod__fournisseur=fournisseur
            ).count()
            fournisseur.factures_count = Facture.objects.filter(
                commande__code_prod__fournisseur=fournisseur
            ).count()
            fournisseur.factures_payees = Facture.objects.filter(
                commande__code_prod__fournisseur=fournisseur,
                statut='payee'
            ).count()
            fournisseur.montant_total = Facture.objects.filter(
                commande__code_prod__fournisseur=fournisseur
            ).aggregate(Sum('montant_total'))['montant_total__sum'] or 0.0
        
        context['fournisseurs'] = fournisseurs_list
        return context


class FournisseurCreateView(AdminOnlyMixin, CreateView):
    """Crée un nouveau fournisseur"""
    model = Fournisseur
    template_name = 'stock/fournisseur_form.html'
    fields = ['code_fournisseur', 'nom_fournisseur', 'mot_de_passe', 'telephone', 'email']
    success_url = reverse_lazy('stock:fournisseur_list')
    
    def get_context_data(self, **kwargs):
        """Retourne le contexte du formulaire"""
        context = super().get_context_data(**kwargs)
        # Ne pas inclure self.object pour les vues de création
        return context
    
    def form_invalid(self, form):
        """Traite un formulaire invalide"""
        # Rendre le formulaire sans accéder à self.object
        return self.render_to_response({'form': form})
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        code_fournisseur = request.POST.get('code_fournisseur')
        nom_fournisseur = request.POST.get('nom_fournisseur')
        email = request.POST.get('email')
        mot_de_passe = request.POST.get('mot_de_passe')
        
        # Vérifier l'unicité du code
        if code_fournisseur and Fournisseur.objects.filter(code_fournisseur=code_fournisseur).exists():
            form.add_error('code_fournisseur', 'Ce code fournisseur existe déjà')
            return self.form_invalid(form)
        
        if form.is_valid():
            fournisseur = form.save(commit=False)
            
            # Créer ou mettre à jour le User Django associé
            try:
                # Utiliser l'email comme username (plus flexible que le nom)
                username = email.split('@')[0] if email else code_fournisseur
                
                # Vérifier que le username est unique
                user_count = 1
                original_username = username
                while User.objects.filter(username=username).exists():
                    username = f"{original_username}{user_count}"
                    user_count += 1
                
                # Créer l'utilisateur Django
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': email,
                        'first_name': nom_fournisseur,
                        'is_active': True,
                    }
                )
                
                # Toujours définir le mot de passe avec le mot de passe du fournisseur
                user.set_password(mot_de_passe if mot_de_passe else 'TempPassword123!')
                
                if not created:
                    # Mettre à jour les infos existantes
                    user.email = email
                    user.first_name = nom_fournisseur
                
                user.save()
                
                # Associer le fournisseur au User
                fournisseur.user = user
                
                # Ajouter l'utilisateur au groupe "Fournisseur"
                fournisseur_group, _ = Group.objects.get_or_create(name='Fournisseur')
                user.groups.add(fournisseur_group)
                
                # Sauvegarder le fournisseur
                fournisseur.save()
                
                messages.success(
                    request,
                    f"Fournisseur '{fournisseur.nom_fournisseur}' créé avec succès! "
                    f"(Login: {username}, Email: {email})"
                )
                return redirect(self.success_url)
            
            except Exception as e:
                messages.error(request, f"Erreur lors de la création du User: {str(e)}")
                return self.form_invalid(form)
        
        return self.form_invalid(form)


class FournisseurUpdateView(AdminOnlyMixin, UpdateView):
    """Modifie un fournisseur"""
    model = Fournisseur
    template_name = 'stock/fournisseur_edit.html'
    fields = ['nom_fournisseur', 'mot_de_passe', 'telephone', 'email', 'statut']
    success_url = reverse_lazy('stock:fournisseur_list')
    
    def form_valid(self, form):
        """Valide le formulaire"""
        self.object = form.save()
        messages.success(self.request, f"Fournisseur '{self.object.nom_fournisseur}' mis à jour avec succès!")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object:
            context['produits_count'] = Produit.objects.filter(
                fournisseur=self.object,
                is_deleted=False
            ).count()
            context['commandes_count'] = Commande.objects.filter(
                code_prod__fournisseur=self.object
            ).count()
        return context


class FournisseurDeleteView(AdminOnlyMixin, DeleteView):
    """Supprime un fournisseur (soft delete)"""
    model = Fournisseur
    template_name = 'stock/fournisseur_confirm_delete.html'
    success_url = reverse_lazy('stock:fournisseur_list')
    context_object_name = 'fournisseur'
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        nom = self.object.nom_fournisseur
        
        # Soft delete: marquer comme inactif
        self.object.statut = 'inactif'
        self.object.save()
        
        messages.success(request, f"Fournisseur '{nom}' désactivé avec succès!")
        return redirect(self.success_url)