"""
Script de test pour l'envoi d'emails.

Utilisation:
    python manage.py shell < test_email.py

Cela testera l'envoi d'un email via Django.
"""

from django.core.mail import send_mail
from django.conf import settings

print("=" * 60)
print("TEST D'ENVOI D'EMAIL")
print("=" * 60)

print(f"\n📧 Email configuré: {settings.EMAIL_HOST_USER}")
print(f"🔧 Serveur SMTP: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
print(f"🔐 TLS activé: {settings.EMAIL_USE_TLS}")

try:
    # Envoyer un email de test
    sujet = "✅ TEST - Gestion de Stock"
    message = """
Bonjour,

Ceci est un email de test du système de Gestion de Stock.

Si tu reçois cet email, la configuration est correcte! 🎉

Système de Gestion de Stock
"""
    
    envoyeur = settings.EMAIL_HOST_USER
    destinataire = [settings.EMAIL_HOST_USER]  # S'envoyer l'email à soi-même
    
    # Envoyer l'email
    nombre_envoyes = send_mail(
        sujet,
        message,
        envoyeur,
        destinataire,
        fail_silently=False,
    )
    
    print(f"\n✅ Email envoyé avec succès!")
    print(f"📊 Nombre d'emails envoyés: {nombre_envoyes}")
    print(f"📬 Vérife ta boîte de réception: {settings.EMAIL_HOST_USER}")
    
except Exception as e:
    print(f"\n❌ Erreur lors de l'envoi:")
    print(f"   {type(e).__name__}: {str(e)}")
    print(f"\n💡 Vérifications à faire:")
    print(f"   1. EMAIL_HOST_USER est configuré dans .env")
    print(f"   2. EMAIL_HOST_PASSWORD n'est pas vide dans .env")
    print(f"   3. L'email est un compte Gmail valide")
    print(f"   4. Un mot de passe d'application a été généré")
    print(f"   5. La connexion Internet est active")

print("\n" + "=" * 60)
