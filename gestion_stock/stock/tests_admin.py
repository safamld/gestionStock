"""
Tests simples pour valider l'interface admin complète.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from stock.models import Produit, Commande, Facture


class AdminInterfaceTests(TestCase):
    """Tests simples pour vérifier que l'interface admin fonctionne."""
    
    def setUp(self):
        """Préparation."""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin', email='admin@test.com', password='admin123'
        )
        self.client.login(username='admin', password='admin123')
        
        # Créer des données de test
        self.produit = Produit.objects.create(
            nom_prod="Test Produit",
            quantite=10, prix_unit=50.0
        )
        self.commande = Commande.objects.create(
            code_prod=self.produit, quantite_cmd=5
        )
        self.facture = Facture.objects.create(
            commande=self.commande, montant_total=250.0, statut='brouillon'
        )
    
    def test_admin_produit_page(self):
        """Test que la page produits est accessible."""
        response = self.client.get('/admin/stock/produit/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_commande_page(self):
        """Test que la page commandes est accessible."""
        response = self.client.get('/admin/stock/commande/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_facture_page(self):
        """Test que la page factures est accessible."""
        response = self.client.get('/admin/stock/facture/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_fournisseur_page(self):
        """Test que la page fournisseurs est accessible."""
        response = self.client.get('/admin/stock/fournisseur/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_notification_page(self):
        """Test que la page notifications est accessible."""
        response = self.client.get('/admin/stock/notification/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_historique_page(self):
        """Test que la page historique est accessible."""
        response = self.client.get('/admin/stock/historique/')
        self.assertEqual(response.status_code, 200)
