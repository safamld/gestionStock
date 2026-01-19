# 📧 Guide Configuration Emails - Gestion de Stock

## 📋 Résumé

Ce guide t'explique comment configurer les **emails automatiques** pour les alertes de rupture de stock.

Quand un produit atteint 0 quantité, le système envoie automatiquement un email au fournisseur principal.

---

## 🎯 Etapes de Configuration

### ÉTAPE 1️⃣ : Créer un Compte Gmail

Si tu n'as pas de compte Gmail:

1. Aller sur: https://gmail.com
2. Cliquer sur "Créer un compte"
3. Remplir les informations
4. Valider les conditions d'utilisation

**Résultat**: Tu as un email: `monentreprise@gmail.com`

---

### ÉTAPE 2️⃣ : Générer un Mot de Passe d'Application

Gmail nécessite un **mot de passe d'application** spécial (pas ton vrai mot de passe):

1. Aller sur: https://myaccount.google.com/apppasswords
2. Te connecter si nécessaire
3. Sélectionner:
   - **Sélectionner l'app**: Mail
   - **Sélectionner l'appareil**: Windows Computer
4. Cliquer "Générer"
5. Google génère un mot de passe à 16 caractères (ex: `abcd efgh ijkl mnop`)
6. **Copier** ce mot de passe (sans les espaces)

**Résultat**: Tu as un mot de passe: `abcdefghijklmnop`

---

### ÉTAPE 3️⃣ : Configurer le Fichier .env

Dans le dossier `gestion_stock/`:

1. Trouver le fichier `.env` (ou le créer s'il n'existe pas)
2. Remplir avec:

```
EMAIL_HOST_USER=monentreprise@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop
```

3. Sauvegarder le fichier

**⚠️ IMPORTANT**: 
- Ne JAMAIS committer `.env` sur GitHub
- Il contient tes identifiants sensibles
- Ajouter `.env` dans `.gitignore`

---

### ÉTAPE 4️⃣ : Tester l'Configuration

Depuis le terminal, dans le dossier `gestion_stock/`:

```bash
python manage.py shell < test_email.py
```

**Résultat attendu**:
```
✅ Email envoyé avec succès!
📊 Nombre d'emails envoyés: 1
📬 Vérife ta boîte de réception: monentreprise@gmail.com
```

Ensuite, vérifier ta boîte de réception pour l'email de test.

---

## 🚀 Utilisation

Une fois configuré, le système envoie **automatiquement** des emails quand:

### ⚠️ Rupture de Stock (quantité = 0)

L'email contient:
- ✉️ Nom du produit
- 💰 Prix unitaire
- 📦 Quantité suggérée à commander
- 💵 Montant estimé
- ⏰ Délai de livraison

### 📉 Stock Bas (quantité < 10)

Une notification est créée (email optionnel)

---

## 🔧 Configuration Avancée

### Utiliser un Autre Fournisseur Email

Si tu veux utiliser **Outlook**, **SendGrid**, ou autre:

1. Modifier `gestion_stock/settings.py`
2. Changer les valeurs:

```python
EMAIL_HOST = 'smtp.outlook.com'  # ou autre serveur
EMAIL_PORT = 587  # ou 465 selon le fournisseur
EMAIL_USE_TLS = True  # ou False selon le fournisseur
EMAIL_HOST_USER = 'ton_email@outlook.com'
EMAIL_HOST_PASSWORD = 'ton_mot_de_passe'
```

---

## ✅ Checklist de Configuration

- [ ] Compte Gmail créé
- [ ] Mot de passe d'application généré
- [ ] Fichier `.env` rempli
- [ ] Test d'email envoyé avec succès
- [ ] Email reçu dans la boîte de réception
- [ ] Fournisseurs configurés dans l'admin

---

## 🐛 Dépannage

### Erreur: "Connection refused"

**Cause**: Le serveur SMTP n'est pas accessible
**Solution**: Vérifier la connexion Internet

### Erreur: "Authentication failed"

**Cause**: Email ou mot de passe incorrect
**Solution**: 
- Vérifier le fichier `.env`
- Régénérer le mot de passe d'application

### Erreur: "Username and Password not accepted"

**Cause**: Credentials invalides
**Solution**:
- S'assurer que c'est un compte Gmail
- Utiliser un mot de passe d'application (pas le vrai mot de passe)

### Email n'arrive pas

**Causes possibles**:
- L'email est en dossier "Spam"
- Délai de livraison (peut prendre quelques secondes)
- Compte Gmail bloqué

---

## 📚 Ressources Utiles

- **Gmail App Passwords**: https://myaccount.google.com/apppasswords
- **Django Email Documentation**: https://docs.djangoproject.com/en/6.0/topics/email/
- **Python-dotenv**: https://github.com/theskumar/python-dotenv

---

## 🎓 Exemple Concret

**Scénario**: Tu as un produit "Laptop" et un fournisseur "TechSupply"

1. ✅ Configurer Gmail (tu reçois les emails)
2. ✅ Créer le fournisseur "TechSupply" avec email
3. ✅ Lier le produit "Laptop" au fournisseur
4. ✅ Créer des commandes jusqu'à rupture (quantité = 0)
5. ✅ → Automatiquement, un email est envoyé à TechSupply
6. 📧 Tu reçois aussi une notification dans l'admin

---

**Questions?** Consulter la documentation Django ou les logs du serveur.
