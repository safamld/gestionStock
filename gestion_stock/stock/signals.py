"""
Signaux Django pour automatiser les alertes et notifications.

Ce module gère:
- Création automatique d'alertes rupture de stock
- Envoi d'emails aux fournisseurs
- Mise à jour des notifications
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from .models import Produit, Commande, Notification, ProduitFournisseur


@receiver(post_save, sender=Commande)
def creer_alerte_rupture_stock(sender, instance, created, **kwargs):
    """
    Signal déclenché après la création/modification d'une commande.
    Crée une notification si le stock passe sous le seuil critique.
    """
    if instance.is_deleted:
        return
    
    produit = instance.code_prod
    
    # Vérifier si le stock est en rupture (quantité = 0)
    if produit.quantite == 0:
        # Créer ou récupérer la notification de rupture
        notification, created = Notification.objects.get_or_create(
            produit=produit,
            type_notification='rupture',
            est_traitee=False,
            defaults={
                'titre': f'⚠️ RUPTURE DE STOCK: {produit.nom_prod}',
                'message': f'Le produit "{produit.nom_prod}" est en rupture de stock!\n\nDétails:\n- Prix unitaire: {produit.prix_unit}€\n- Dernière commande: {instance.date_commande}',
                'fournisseur': None,
            }
        )
        
        if created:
            # Envoyer les alertes aux fournisseurs
            contacter_fournisseurs(produit, notification)
    
    # Vérifier si le stock est bas (moins de 10 unités)
    elif produit.quantite < 10 and produit.quantite > 0:
        notification, created = Notification.objects.get_or_create(
            produit=produit,
            type_notification='alerte_basse',
            est_traitee=False,
            defaults={
                'titre': f'📉 STOCK BAS: {produit.nom_prod} ({produit.quantite} unités)',
                'message': f'Le produit "{produit.nom_prod}" a un stock bas.\n\nDétails:\n- Quantité restante: {produit.quantite} unités\n- Prix unitaire: {produit.prix_unit}€',
                'fournisseur': None,
            }
        )


def contacter_fournisseurs(produit, notification):
    """
    Contacte les fournisseurs du produit en rupture de stock.
    Envoie un email et crée une notification.
    """
    # Récupérer les fournisseurs du produit
    produits_fournisseurs = ProduitFournisseur.objects.filter(
        produit=produit,
        fournisseur__is_actif=True
    ).select_related('fournisseur').order_by('-is_principal')
    
    for pf in produits_fournisseurs:
        fournisseur = pf.fournisseur
        
        # Envoyer email au fournisseur
        envoyer_email_fournisseur(produit, fournisseur, pf)
        
        # Créer notification de contact fournisseur
        Notification.objects.create(
            type_notification='fournisseur_contact',
            produit=produit,
            fournisseur=fournisseur,
            titre=f'📧 Fournisseur contacté: {fournisseur.nom_fournisseur}',
            message=f'Email envoyé à {fournisseur.email} pour commander {pf.quantite_min} unités de "{produit.nom_prod}".\n\nDélai de livraison prévu: {pf.delai_livraison} jours\nPrix fournisseur: {pf.prix_fournisseur}€/unité',
            est_lue=False,
        )


def envoyer_email_fournisseur(produit, fournisseur, produit_fournisseur):
    """
    Envoie un email au fournisseur pour signaler la rupture de stock.
    """
    try:
        sujet = f"⚠️ URGENCE: Rupture de stock - {produit.nom_prod}"
        
        message = f"""
Bonjour {fournisseur.nom_fournisseur},

⚠️  ALERTE RUPTURE DE STOCK ⚠️

Le produit suivant est en rupture de stock:

📦 Produit: {produit.nom_prod}
💰 Prix unitaire: {produit.prix_unit}€
📊 Stock actuel: 0 unités
📝 Description: {produit.description or 'N/A'}

COMMANDE SUGGÉRÉE:
- Quantité: {produit_fournisseur.quantite_min} unités
- Prix fournisseur: {produit_fournisseur.prix_fournisseur}€/unité
- Montant total: {produit_fournisseur.quantite_min * produit_fournisseur.prix_fournisseur}€
- Délai de livraison: {produit_fournisseur.delai_livraison} jours

⏰ Merci de confirmer la commande au plus tôt!

Cordialement,
Système de Gestion de Stock
"""
        
        # Envoyer l'email
        send_mail(
            sujet,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [fournisseur.email],
            fail_silently=False,
        )
        
        print(f"✅ Email envoyé à {fournisseur.email}")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi de l'email à {fournisseur.email}: {str(e)}")


@receiver(post_save, sender=Commande)
def notification_commande_confirmee(sender, instance, created, **kwargs):
    """
    Crée une notification quand une commande est confirmée.
    """
    if created and not instance.is_deleted:
        Notification.objects.create(
            type_notification='commande_confirmee',
            produit=instance.code_prod,
            titre=f'✅ Commande confirmée: {instance.code_prod.nom_prod}',
            message=f'Commande #{instance.code_cmd} créée avec succès.\n\nProduit: {instance.code_prod.nom_prod}\nQuantité: {instance.quantite_cmd}\nMontant: {instance.montant_commande()}€',
        )
