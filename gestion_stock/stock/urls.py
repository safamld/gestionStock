"""
Configuration des URLs pour l'application stock.

Ce module mappe toutes les vues aux routes URL.
"""

from django.urls import path
from . import views

app_name = 'stock'

urlpatterns = [
    # Page d'accueil
    path('', views.home_view, name='home'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # ==================== ROUTES POUR LES PRODUITS ====================
    
    # Liste et création de produits
    path('produits/', views.ProduitListView.as_view(), name='produit_list'),
    path('produits/nouveau/', views.ProduitCreateView.as_view(), name='produit_create'),
    
    # Détail, modification et suppression
    path('produits/<int:pk>/', views.ProduitDetailView.as_view(), name='produit_detail'),
    path('produits/<int:pk>/modifier/', views.ProduitUpdateView.as_view(), name='produit_update'),
    path('produits/<int:pk>/supprimer/', views.ProduitDeleteView.as_view(), name='produit_delete'),
    
    # ==================== ROUTES POUR LES COMMANDES ====================
    
    # Liste et création de commandes
    path('commandes/', views.CommandeListView.as_view(), name='commande_list'),
    path('commandes/nouvelle/', views.CommandeCreateView.as_view(), name='commande_create'),
    
    # Détail, modification et suppression
    path('commandes/<int:pk>/', views.CommandeDetailView.as_view(), name='commande_detail'),
    path('commandes/<int:pk>/modifier/', views.CommandeUpdateView.as_view(), name='commande_update'),
    path('commandes/<int:pk>/supprimer/', views.CommandeDeleteView.as_view(), name='commande_delete'),
    
    # ==================== ROUTES POUR LES FACTURES ====================
    
    # Liste et création de factures
    path('factures/', views.FactureListView.as_view(), name='facture_list'),
    path('factures/nouvelle/', views.FactureCreateView.as_view(), name='facture_create'),
    
    # Détail, modification et suppression
    path('factures/<int:pk>/', views.FactureDetailView.as_view(), name='facture_detail'),
    path('factures/<int:pk>/modifier/', views.FactureUpdateView.as_view(), name='facture_update'),
    path('factures/<int:pk>/supprimer/', views.FactureDeleteView.as_view(), name='facture_delete'),
    
    # ==================== ROUTES POUR L'HISTORIQUE ====================
    
    path('historique/', views.HistoriqueListView.as_view(), name='historique_list'),
    path('historique-view/', views.historique_view, name='historique'),
    
    # ==================== ROUTES POUR LES STATISTIQUES ====================
    
    path('statistiques/', views.StatistiquesView.as_view(), name='statistiques_list'),
    path('statistiques-view/', views.statistiques_view, name='statistiques'),
    
    # ==================== ROUTES POUR LA GESTION DES AGENTS (ADMIN) ====================
    
    path('agents/', views.AgentListView.as_view(), name='agent_list'),
    path('agents/rapport/', views.AgentReportView.as_view(), name='agent_report'),
    path('agents/nouveau/', views.AgentCreateView.as_view(), name='agent_create'),
    path('agents/<int:pk>/modifier/', views.AgentUpdateView.as_view(), name='agent_edit'),
    path('agents/<int:pk>/supprimer/', views.AgentDeleteView.as_view(), name='agent_delete'),
    path('agents/<int:pk>/graphiques/', views.agent_graphs_data, name='agent_graphs_data'),
    
    # ==================== ROUTES POUR AGENT DASHBOARD ====================
    
    path('agent/dashboard/', views.agent_dashboard_view, name='agent_dashboard'),
    path('agent/commande/<int:produit_id>/', views.passer_commande_view, name='passer_commande'),
    
    # ==================== ROUTES POUR FOURNISSEUR DASHBOARD ====================
    
    path('fournisseur/login/', views.fournisseur_login_view, name='fournisseur_login'),
    path('fournisseur/logout/', views.fournisseur_logout_view, name='fournisseur_logout'),
    path('fournisseur/dashboard/', views.fournisseur_dashboard_view, name='fournisseur_dashboard'),
    path('fournisseur/produit/ajouter/', views.ajouter_produit_fournisseur_view, name='ajouter_produit_fournisseur'),
    path('fournisseur/produit/<int:produit_id>/modifier/', views.modifier_produit_fournisseur_view, name='modifier_produit_fournisseur'),
    path('fournisseur/produit/<int:produit_id>/supprimer/', views.supprimer_produit_fournisseur_view, name='supprimer_produit_fournisseur'),
    path('fournisseur/facture/<int:facture_id>/payee/', views.marquer_facture_payee_view, name='marquer_facture_payee'),
    path('fournisseur/facture/<int:facture_id>/valider-paiement/', views.marquer_facture_payee_view, name='valider_paiement_facture'),
    path('fournisseur/facture/<int:facture_id>/details/', views.detailler_facture_fournisseur_view, name='detailler_facture_fournisseur'),
    path('fournisseur/commande/<int:commande_id>/marquer-payee/', views.marquer_commande_payee_view, name='marquer_commande_payee'),
    
    # ==================== ROUTES POUR LA GESTION DES FOURNISSEURS (ADMIN) ====================
    
    path('fournisseurs/', views.FournisseurListView.as_view(), name='fournisseur_list'),
    path('fournisseurs/nouveau/', views.FournisseurCreateView.as_view(), name='fournisseur_create'),
    path('fournisseurs/<str:pk>/modifier/', views.FournisseurUpdateView.as_view(), name='fournisseur_edit'),
    path('fournisseurs/<str:pk>/supprimer/', views.FournisseurDeleteView.as_view(), name='fournisseur_delete'),
]