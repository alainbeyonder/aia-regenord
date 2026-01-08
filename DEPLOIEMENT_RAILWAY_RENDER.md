# 🚂 Déploiement sur Railway ou Render - Guide Complet

Guide étape par étape pour déployer le backend sur Railway ou Render.

---

## 🎯 Choix de la Plateforme

### Railway (Recommandé)
- ✅ Interface moderne et intuitive
- ✅ Déploiement automatique depuis GitHub
- ✅ PostgreSQL inclus
- ✅ HTTPS automatique
- ✅ Variables d'environnement faciles
- ✅ URL personnalisable (api.regenord.com possible)

### Render
- ✅ Interface simple
- ✅ Déploiement depuis GitHub
- ✅ PostgreSQL disponible
- ✅ HTTPS automatique
- ✅ Free tier disponible

**Note:** Les deux sont excellents. Railway est légèrement plus moderne.

---

## 🚂 Option A: Déploiement sur Railway

### Étape 1: Préparer le Repository GitHub

```bash
cd /Users/alain/Documents/aia-regenord

# Initialiser Git si pas déjà fait
git init
git add .
git commit -m "Initial commit - Backend production ready"

# Créer un repository sur GitHub
# Aller sur: https://github.com/new
# Créer un repository: aia-regenord

# Lier le repository local
git remote add origin https://github.com/VOTRE_USERNAME/aia-regenord.git
git branch -M main
git push -u origin main
```

### Étape 2: Créer un Compte Railway

1. Aller sur: https://railway.app
2. Cliquer sur "Start a New Project"
3. Se connecter avec GitHub
4. Autoriser Railway à accéder à vos repositories

### Étape 3: Créer un Nouveau Projet

1. Cliquer sur **"New Project"**
2. Sélectionner **"Deploy from GitHub repo"**
3. Choisir le repository `aia-regenord`
4. Railway va détecter automatiquement le backend

### Étape 4: Configurer le Service Backend

Railway devrait détecter automatiquement:
- **Root Directory:** `/backend`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Si pas automatique:
1. Cliquer sur le service backend
2. Aller dans **"Settings"** → **"Build & Deploy"**
3. Configurer:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Étape 5: Ajouter PostgreSQL

1. Dans le projet Railway, cliquer sur **"New"**
2. Sélectionner **"Database"** → **"Add PostgreSQL"**
3. Railway créera automatiquement une base de données
4. La variable `DATABASE_URL` sera automatiquement configurée

### Étape 6: Configurer les Variables d'Environnement

1. Cliquer sur le service backend
2. Aller dans **"Variables"**
3. Ajouter les variables suivantes (une par une):

```env
# QuickBooks
QBO_ENVIRONMENT=production
QBO_CLIENT_ID=ABhjTWUsPqScOqpWeCghMKHpx85MbL0fM9JQnt4uXpD4Wynk
QBO_CLIENT_SECRET=d2R1L2EFjbZyNmJdcYnnbibh6AVsIVlZDFF9dc8V
QBO_REDIRECT_URI=https://www.regenord.com/quickbooks-integration/callback

# Application
APP_NAME=AIA Regenord
APP_ENV=production
DEBUG=False
APP_BASE_URL=https://aia-regenord-backend-production.up.railway.app
FRONTEND_URL=https://www.regenord.com

# Sécurité
AIA_TOKEN_ENCRYPTION_KEY=Jc8GWiI1zrJ9a-aWYgETa42PLx3FRUjbkJzQ_SEIg3c=
SECRET_KEY=o8x80d_-Uu_uPbE0vASawCqen_BrSr8hVtkelay_cpU

# CORS
CORS_ORIGINS=["https://www.regenord.com"]

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/aia-regenord.log
```

**Note:** `DATABASE_URL` sera automatiquement ajouté par Railway.

**Important:** 
- `APP_BASE_URL` sera l'URL Railway générée (ex: `https://aia-regenord-backend-production.up.railway.app`)
- Notez cette URL, vous devrez la mettre à jour dans le code Squarespace

### Étape 7: Configurer un Domaine Personnalisé (Optionnel)

Si vous voulez utiliser `api.regenord.com`:

1. Dans le service backend, aller dans **"Settings"** → **"Networking"**
2. Cliquer sur **"Generate Domain"** pour obtenir l'URL Railway
3. Cliquer sur **"Custom Domain"**
4. Entrer: `api.regenord.com`
5. Railway vous donnera un enregistrement DNS à ajouter
6. Ajouter l'enregistrement CNAME dans votre DNS:
   - **Type:** CNAME
   - **Nom:** api
   - **Valeur:** L'URL fournie par Railway (ex: `xxxx.up.railway.app`)
7. Attendre la propagation DNS (5-30 minutes)

### Étape 8: Déployer

1. Railway déploiera automatiquement à chaque push sur GitHub
2. Ou cliquer sur **"Deploy"** manuellement
3. Voir les logs dans l'onglet **"Deployments"**

### Étape 9: Vérifier le Déploiement

```bash
# Obtenir l'URL Railway (dans le dashboard)
# Exemple: https://aia-regenord-backend-production.up.railway.app

# Tester
curl https://aia-regenord-backend-production.up.railway.app/health

# Ou avec domaine personnalisé
curl https://api.regenord.com/health
```

### Étape 10: Mettre à Jour le Code Squarespace

Si vous utilisez l'URL Railway (pas de domaine personnalisé):

1. Ouvrir `SQUARESPACE_CODE_INJECTION_READY.html`
2. Remplacer:
   ```javascript
   const BACKEND_URL = 'https://api.regenord.com';
   ```
   Par:
   ```javascript
   const BACKEND_URL = 'https://aia-regenord-backend-production.up.railway.app';
   ```
   (Utiliser votre URL Railway réelle)

3. Réinjecter dans Squarespace

---

## 🎨 Option B: Déploiement sur Render

### Étape 1: Créer un Compte Render

1. Aller sur: https://render.com
2. Cliquer sur "Get Started for Free"
3. Se connecter avec GitHub

### Étape 2: Créer un Web Service

1. Dans le dashboard, cliquer sur **"New +"**
2. Sélectionner **"Web Service"**
3. Connecter votre repository GitHub `aia-regenord`

### Étape 3: Configurer le Service

**Settings:**
- **Name:** `aia-regenord-backend`
- **Region:** Choisir la région la plus proche
- **Branch:** `main`
- **Root Directory:** `backend`
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Instance Type:** Free (ou Paid pour plus de performance)

### Étape 4: Ajouter PostgreSQL

1. Dans le dashboard, cliquer sur **"New +"**
2. Sélectionner **"PostgreSQL"**
3. Configurer:
   - **Name:** `aia-regenord-db`
   - **Database:** `aia_regenord`
   - **User:** (sera généré automatiquement)
   - **Region:** Même région que le web service
4. Notez les credentials générés

### Étape 5: Configurer les Variables d'Environnement

Dans le Web Service, aller dans **"Environment"** et ajouter:

```env
# QuickBooks
QBO_ENVIRONMENT=production
QBO_CLIENT_ID=ABhjTWUsPqScOqpWeCghMKHpx85MbL0fM9JQnt4uXpD4Wynk
QBO_CLIENT_SECRET=d2R1L2EFjbZyNmJdcYnnbibh6AVsIVlZDFF9dc8V
QBO_REDIRECT_URI=https://www.regenord.com/quickbooks-integration/callback

# Application
APP_NAME=AIA Regenord
APP_ENV=production
DEBUG=False
APP_BASE_URL=https://aia-regenord-backend.onrender.com
FRONTEND_URL=https://www.regenord.com

# Base de données (depuis PostgreSQL service)
DATABASE_URL=<Copier depuis le service PostgreSQL>

# Sécurité
AIA_TOKEN_ENCRYPTION_KEY=Jc8GWiI1zrJ9a-aWYgETa42PLx3FRUjbkJzQ_SEIg3c=
SECRET_KEY=o8x80d_-Uu_uPbE0vASawCqen_BrSr8hVtkelay_cpU

# CORS
CORS_ORIGINS=["https://www.regenord.com"]

# Logging
LOG_LEVEL=INFO
```

**Important:** 
- `DATABASE_URL` doit être copié depuis le service PostgreSQL
- `APP_BASE_URL` sera `https://aia-regenord-backend.onrender.com` (ou votre nom)

### Étape 6: Configurer un Domaine Personnalisé (Optionnel)

1. Dans le Web Service, aller dans **"Settings"** → **"Custom Domain"**
2. Entrer: `api.regenord.com`
3. Render vous donnera un enregistrement DNS
4. Ajouter l'enregistrement CNAME dans votre DNS
5. Attendre la propagation

### Étape 7: Créer un fichier `render.yaml` (Optionnel)

Pour automatiser la configuration, créer `render.yaml` à la racine:

```yaml
services:
  - type: web
    name: aia-regenord-backend
    runtime: python
    buildCommand: pip install -r backend/requirements.txt
    startCommand: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: QBO_ENVIRONMENT
        value: production
      - key: APP_BASE_URL
        fromService:
          name: aia-regenord-backend
          type: web
          property: host
```

### Étape 8: Déployer

1. Render va déployer automatiquement
2. Voir les logs dans l'onglet **"Logs"**
3. Attendre que le build soit terminé (2-5 minutes)

### Étape 9: Vérifier le Déploiement

```bash
# Obtenir l'URL Render (dans le dashboard)
# Exemple: https://aia-regenord-backend.onrender.com

curl https://aia-regenord-backend.onrender.com/health
```

### Étape 10: Mettre à Jour le Code Squarespace

Si vous n'utilisez pas de domaine personnalisé:

1. Ouvrir `SQUARESPACE_CODE_INJECTION_READY.html`
2. Remplacer `BACKEND_URL` par votre URL Render
3. Réinjecter dans Squarespace

---

## ✅ Vérification Finale

### Test 1: Santé du Backend

```bash
# Railway
curl https://aia-regenord-backend-production.up.railway.app/health
# ou avec domaine personnalisé
curl https://api.regenord.com/health

# Render
curl https://aia-regenord-backend.onrender.com/health
```

**Réponse attendue:**
```json
{"status": "healthy"}
```

### Test 2: Configuration QBO

```bash
curl https://[VOTRE-URL]/api/qbo/config/check
```

**Vérifier:**
- `"environment": "production"`
- `"ready_for_production": true`
- `"api_base_url": "https://quickbooks.api.intuit.com"`

### Test 3: Depuis la Console Navigateur

Ouvrir la console sur `https://www.regenord.com/quickbooks-integration` et tester:

```javascript
fetch('https://[VOTRE-URL]/health')
  .then(r => r.json())
  .then(console.log)
```

---

## 🔄 Mises à Jour Futures

### Railway

Les mises à jour sont automatiques:
1. Faire un `git push` sur GitHub
2. Railway déploie automatiquement

### Render

Les mises à jour sont automatiques:
1. Faire un `git push` sur GitHub
2. Render déploie automatiquement (sur le plan gratuit, peut prendre quelques minutes)

### Mettre à Jour les Variables d'Environnement

**Railway:**
1. Aller dans le service → **"Variables"**
2. Modifier ou ajouter des variables
3. Le service redémarre automatiquement

**Render:**
1. Aller dans le service → **"Environment"**
2. Modifier ou ajouter des variables
3. Le service redémarre automatiquement

---

## 📊 Comparaison Railway vs Render

| Feature | Railway | Render |
|---------|---------|--------|
| Free Tier | ✅ Oui | ✅ Oui |
| PostgreSQL | ✅ Inclus | ✅ Disponible |
| HTTPS | ✅ Automatique | ✅ Automatique |
| Domaine personnalisé | ✅ Oui | ✅ Oui |
| Déploiement auto | ✅ Oui | ✅ Oui |
| Interface | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Performance | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

**Recommandation:** Les deux sont excellents. Railway a une interface légèrement plus moderne.

---

## 🐛 Dépannage

### Le déploiement échoue

**Vérifier:**
- Les variables d'environnement sont toutes configurées
- `requirements.txt` est présent dans `backend/`
- Le Root Directory est correct (`backend`)
- Les logs dans Railway/Render pour voir l'erreur exacte

### Erreur de connexion base de données

**Railway:**
- Vérifier que le service PostgreSQL est créé
- `DATABASE_URL` est automatiquement configuré
- Vérifier dans les variables

**Render:**
- Vérifier que le service PostgreSQL est créé
- Copier `DATABASE_URL` depuis le service PostgreSQL
- Vérifier qu'il est bien ajouté dans le Web Service

### Le backend démarre mais retourne des erreurs

**Vérifier les logs:**
- Railway: Onglet **"Deployments"** → Cliquer sur un déploiement → **"View Logs"**
- Render: Onglet **"Logs"**

**Vérifier:**
- Toutes les variables d'environnement sont présentes
- Les credentials QuickBooks sont corrects
- La base de données est accessible

---

## 🎉 Déploiement Réussi!

Une fois déployé:
1. ✅ Notez l'URL du backend (Railway ou Render)
2. ✅ Mettez à jour `BACKEND_URL` dans le code Squarespace
3. ✅ Réinjectez le code dans Squarespace
4. ✅ Testez sur `https://www.regenord.com/quickbooks-integration`

**Le frontend Squarespace pourra alors se connecter correctement!**

---

**Date de création:** $(date)  
**Version:** Production 1.0
