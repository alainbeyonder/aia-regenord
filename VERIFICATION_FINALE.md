# ✅ Vérification Finale - Avant Déploiement

Guide de vérification complète avant de déployer en production.

---

## 🔍 Étape 1: Validation Automatique

### Validation complète

```bash
# Validation avancée de toutes les variables
./scripts/validate_production_env.sh

# Vérification rapide de la configuration
./scripts/verify_production_setup.sh
```

**Les deux scripts doivent passer sans erreurs critiques.**

---

## 📋 Étape 2: Vérification Manuelle des Variables

### 2.1 Variables QuickBooks (requises)

Vérifier dans `backend/.env`:

```env
QBO_ENVIRONMENT=production
QBO_CLIENT_ID=ABhjTWUsPqScOqpWeCghMKHpx85MbL0fM9JQnt4uXpD4Wynk
QBO_CLIENT_SECRET=d2R1L2EFjbZyNmJdcYnnbibh6AVsIVlZDFF9dc8V
QBO_REDIRECT_URI=https://www.regenord.com/quickbooks-integration/callback
```

✅ **Checklist:**
- [ ] `QBO_ENVIRONMENT` = `production` (pas `sandbox`)
- [ ] `QBO_CLIENT_ID` correspond exactement
- [ ] `QBO_CLIENT_SECRET` est configuré (pas vide, pas placeholder)
- [ ] `QBO_REDIRECT_URI` correspond exactement (pas d'espace, pas de slash final)

---

### 2.2 Variables Application

```env
APP_NAME=AIA Regenord
APP_ENV=production
DEBUG=False
APP_BASE_URL=https://api.regenord.com
FRONTEND_URL=https://www.regenord.com
```

✅ **Checklist:**
- [ ] `APP_ENV` = `production`
- [ ] `DEBUG` = `False` (pas `True`)
- [ ] `APP_BASE_URL` = `https://api.regenord.com`
- [ ] `FRONTEND_URL` = `https://www.regenord.com`

---

### 2.3 Variables de Sécurité (critiques)

```env
AIA_TOKEN_ENCRYPTION_KEY=Jc8GWiI1zrJ9a-aWYgETa42PLx3FRUjbkJzQ_SEIg3c=
SECRET_KEY=o8x80d_-Uu_uPbE0vASawCqen_BrSr8hVtkelay_cpU
```

✅ **Checklist:**
- [ ] `AIA_TOKEN_ENCRYPTION_KEY` est généré (se termine par `=`)
- [ ] `AIA_TOKEN_ENCRYPTION_KEY` n'est pas `YOUR_FERNET_KEY_HERE`
- [ ] `SECRET_KEY` est généré (minimum 32 caractères)
- [ ] `SECRET_KEY` n'est pas `CHANGE_ME_TO_A_LONG_RANDOM_STRING`
- [ ] Les deux clés sont différentes

⚠️ **Important:** Ces clés sont critiques pour la sécurité. Ne les partagez jamais et ne les committez pas dans Git.

---

### 2.4 Base de Données

```env
DATABASE_URL=postgresql://user:password@host:5432/database
```

✅ **Checklist:**
- [ ] `DATABASE_URL` est configuré avec vos credentials réels
- [ ] `DATABASE_URL` ne contient pas `user:password@host`
- [ ] Format correct: `postgresql://`
- [ ] La base de données est accessible depuis le serveur backend

**Test de connexion:**
```bash
# Tester la connexion (si psql est installé)
psql "$DATABASE_URL" -c "SELECT 1;" 2>&1
```

---

### 2.5 CORS (Cross-Origin Resource Sharing)

```env
CORS_ORIGINS=["https://www.regenord.com"]
```

✅ **Checklist:**
- [ ] `CORS_ORIGINS` inclut `https://www.regenord.com`
- [ ] Format JSON valide (avec crochets)
- [ ] Pas de `http://localhost` en production

**Si non défini:** Le backend utilisera les valeurs par défaut (localhost), ce qui bloquera les requêtes depuis Squarespace. **À configurer!**

---

### 2.6 Logging

```env
LOG_LEVEL=INFO
LOG_FILE=./logs/aia-regenord.log
```

✅ **Checklist:**
- [ ] `LOG_LEVEL` = `INFO` ou `WARNING` (pas `DEBUG` en production)
- [ ] `LOG_FILE` pointe vers un chemin accessible

---

## 🔧 Étape 3: Vérification Intuit Developer

### 3.1 Se connecter

1. Aller sur: https://developer.intuit.com
2. Se connecter avec votre compte
3. Sélectionner votre application QuickBooks

### 3.2 Vérifier les Redirect URIs

1. Aller dans **Settings** ou **Keys & OAuth**
2. Trouver la section **Redirect URIs**

✅ **Checklist:**
- [ ] Redirect URI ajouté: `https://www.regenord.com/quickbooks-integration/callback`
- [ ] **Exactement identique** (copier-coller recommandé)
- [ ] Pas d'espace avant ou après
- [ ] Pas de slash final
- [ ] Application en mode **Production** (pas Sandbox)

### 3.3 Vérifier les Credentials

✅ **Checklist:**
- [ ] Client ID: `ABhjTWUsPqScOqpWeCghMKHpx85MbL0fM9JQnt4uXpD4Wynk`
- [ ] Client Secret correspond à celui dans `backend/.env`
- [ ] Les credentials sont actifs

---

## 📄 Étape 4: Vérification Code Squarespace

### 4.1 Vérifier le fichier

Ouvrir `SQUARESPACE_CODE_INJECTION_READY.html` et vérifier:

✅ **Checklist:**
- [ ] `BACKEND_URL = 'https://api.regenord.com'`
- [ ] `COMPANY_ID = 1` (ou la valeur correcte)
- [ ] Pas d'URL localhost dans le code
- [ ] Code complet (306 lignes environ)

### 4.2 Vérifier l'injection

Si déjà injecté dans Squarespace:

1. Aller sur: `https://www.regenord.com/quickbooks-integration`
2. Ouvrir la console du navigateur (F12)
3. Vérifier qu'il n'y a pas d'erreurs JavaScript

✅ **Checklist:**
- [ ] Page accessible et s'affiche correctement
- [ ] Interface QuickBooks visible
- [ ] Pas d'erreurs dans la console
- [ ] Le code est dans **Footer** (pas Header)

---

## 🏗️ Étape 5: Vérification Backend

### 5.1 Accessibilité

```bash
# Test de santé
curl https://api.regenord.com/api/health

# Test de configuration QBO
curl https://api.regenord.com/api/qbo/config/check
```

✅ **Réponses attendues:**
- `/api/health`: `{"status": "ok", "service": "api"}`
- `/api/qbo/config/check`: Configuration complète avec `ready_for_production: true`

### 5.2 Vérifier les Logs

Si le backend est déjà déployé:

```bash
# Vérifier les logs (selon votre méthode de déploiement)
tail -f logs/aia-regenord.log

# Ou via votre plateforme de déploiement
# (Heroku, AWS, Docker, etc.)
```

✅ **Checklist:**
- [ ] Backend démarre sans erreurs
- [ ] Pas d'erreurs de connexion base de données
- [ ] Pas d'erreurs de chargement des variables d'environnement
- [ ] Les logs sont accessibles

---

## 🧪 Étape 6: Test End-to-End

### 6.1 Test de connexion OAuth

1. **Aller sur la page:**
   ```
   https://www.regenord.com/quickbooks-integration
   ```

2. **Vérifier le statut:**
   - Le statut devrait se charger automatiquement
   - Affiche "⏳ QuickBooks Non Connecté" (normal si première fois)

3. **Tester la connexion:**
   - Cliquer sur "Connecter QuickBooks"
   - Redirection vers Intuit OAuth
   - Autoriser l'accès
   - Retour sur la page avec message de succès

✅ **Checklist:**
- [ ] Redirection vers Intuit fonctionne
- [ ] Autorisation réussie
- [ ] Retour sur la page avec succès
- [ ] Statut mis à jour: "✅ QuickBooks Connecté"
- [ ] Realm ID affiché

### 6.2 Test de déconnexion

1. Cliquer sur "Déconnecter QuickBooks"
2. Confirmer
3. Vérifier que le statut revient à "Non Connecté"

✅ **Checklist:**
- [ ] Déconnexion fonctionne
- [ ] Statut mis à jour correctement

---

## 🔐 Étape 7: Vérification Sécurité

### 7.1 Fichier .env

✅ **Checklist:**
- [ ] `backend/.env` est dans `.gitignore`
- [ ] Le fichier n'est pas commité dans Git
- [ ] Les clés de sécurité ne sont pas dans le code source
- [ ] Les credentials ne sont pas dans les logs

### 7.2 Permissions

✅ **Checklist:**
- [ ] Le fichier `.env` a les bonnes permissions (600 recommandé)
- [ ] Seuls les processus nécessaires peuvent lire le fichier

### 7.3 HTTPS

✅ **Checklist:**
- [ ] Toutes les URLs utilisent HTTPS (pas HTTP)
- [ ] Certificat SSL valide pour `https://api.regenord.com`
- [ ] Certificat SSL valide pour `https://www.regenord.com`

---

## 📊 Étape 8: Checklist Finale

### Configuration
- [ ] Toutes les variables d'environnement configurées
- [ ] `DATABASE_URL` configuré avec credentials réels
- [ ] `CORS_ORIGINS` inclut `https://www.regenord.com`
- [ ] `DEBUG=False` en production
- [ ] Clés de sécurité générées

### Intuit Developer
- [ ] Redirect URI configuré exactement
- [ ] Application en mode Production
- [ ] Credentials correspondants

### Backend
- [ ] Backend déployé et accessible
- [ ] Base de données connectée
- [ ] Tests de santé passent
- [ ] Logs fonctionnels

### Frontend/Squarespace
- [ ] Code injecté dans Squarespace
- [ ] Page accessible
- [ ] Interface s'affiche correctement
- [ ] Pas d'erreurs JavaScript

### Tests
- [ ] Connexion OAuth fonctionne
- [ ] Déconnexion fonctionne
- [ ] Statut se met à jour correctement

### Sécurité
- [ ] `.env` dans `.gitignore`
- [ ] HTTPS activé partout
- [ ] Clés de sécurité sécurisées

---

## ✅ Prêt pour la Production!

Si toutes les vérifications sont passées:

🎉 **Votre intégration QuickBooks Online est prête pour la production!**

Vous pouvez maintenant:
- Connecter des comptes QuickBooks en production
- Synchroniser des données financières réelles
- Générer des projections basées sur des données réelles

---

## 🐛 Problèmes Détectés?

### Scripts de diagnostic

```bash
# Validation complète
./scripts/validate_production_env.sh

# Vérification rapide
./scripts/verify_production_setup.sh

# Test de connexion (après injection)
./scripts/test_oauth_connection.sh
```

### Documentation

- **Guide de dépannage:** `GUIDE_INJECTION_SQUARESPACE.md` (section Dépannage)
- **Guide complet:** `DEPLOIEMENT_ETAPE_PAR_ETAPE.md`
- **Checklist:** `CHECKLIST_FINALE.md`

---

**Date de création:** $(date)  
**Version:** Production 1.0
