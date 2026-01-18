"""
Configuration des URLs pour l'application stock.

Ce module mappe toutes les vues aux routes URL.
"""

from django.urls import path
from . import views

app_name = 'stock'

urlpatterns = [
    # Page d'accueil
    path('', views.DashboardView.as_view(), name='dashboard'),
    
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
    
    # ==================== ROUTES POUR LES STATISTIQUES ====================
    
    path('statistiques/', views.StatistiquesView.as_view(), name='statistiques'),
]
