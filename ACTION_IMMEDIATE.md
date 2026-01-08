# ⚡ Action Immédiate - Déploiement Railway

## ✅ État Actuel

- ✅ Code préparé et commité localement
- ✅ Fichiers de configuration créés
- ✅ Repository GitHub: `alainbeyonder/aia-regenord`
- ⏳ Push GitHub nécessite authentification (à faire manuellement)

---

## 🚀 Action Immédiate

### Option 1: Push via Terminal (Recommandé)

```bash
cd /Users/alain/Documents/aia-regenord
git push origin main
```

**Si authentification requise:**
- Nom d'utilisateur: `alainbeyonder`
- Mot de passe: Utiliser un **Personal Access Token** (pas votre mot de passe GitHub)
- Créer un token: https://github.com/settings/tokens
  - Cliquer "Generate new token (classic)"
  - Nom: "Railway Deployment"
  - Sélectionner: `repo` (toutes les permissions repo)
  - Copier le token et l'utiliser comme mot de passe

### Option 2: Push via GitHub Desktop

1. Ouvrir GitHub Desktop
2. Ajouter le repository: `aia-regenord`
3. Cliquer "Push origin"

### Option 3: Push via GitHub Web (Simple)

Si vous ne pouvez pas pousser maintenant, vous pouvez:
1. Aller directement sur Railway
2. Railway peut cloner depuis GitHub même si vous n'avez pas poussé les derniers commits
3. Railway utilisera la version actuelle sur GitHub

---

## 🚂 Déploiement Railway - Étapes Simplifiées

Une fois le code poussé (ou si Railway peut accéder au repo):

### 1. Créer un Projet Railway

1. **Aller sur:** https://railway.app
2. **Cliquer:** "Start a New Project" ou "Login"
3. **Se connecter avec GitHub**
4. **Cliquer:** "New Project" → "Deploy from GitHub repo"
5. **Sélectionner:** `alainbeyonder/aia-regenord`

### 2. Configurer le Service Backend

Railway détectera automatiquement le backend grâce à `backend/railway.json`.

**Vérifier dans Settings → Build & Deploy:**
- **Root Directory:** `backend` ✅
- **Build Command:** `pip install -r requirements.txt` ✅
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT` ✅

### 3. Ajouter PostgreSQL

1. Dans le projet Railway: **"New"** → **"Database"**
2. **Sélectionner:** "Add PostgreSQL"
3. Railway créera automatiquement la base de données
4. **`DATABASE_URL` sera automatiquement ajouté** aux variables

### 4. Ajouter les Variables d'Environnement

1. **Cliquer sur le service backend**
2. **Onglet "Variables"**
3. **Ajouter chaque variable** (copier depuis `VARIABLES_RAILWAY.txt`):

**Variables essentielles:**

```
QBO_ENVIRONMENT = production
QBO_CLIENT_ID = ABhjTWUsPqScOqpWeCghMKHpx85MbL0fM9JQnt4uXpD4Wynk
QBO_CLIENT_SECRET = d2R1L2EFjbZyNmJdcYnnbibh6AVsIVlZDFF9dc8V
QBO_REDIRECT_URI = https://www.regenord.com/quickbooks-integration/callback
APP_NAME = AIA Regenord
APP_ENV = production
DEBUG = False
FRONTEND_URL = https://www.regenord.com
AIA_TOKEN_ENCRYPTION_KEY = Jc8GWiI1zrJ9a-aWYgETa42PLx3FRUjbkJzQ_SEIg3c=
SECRET_KEY = o8x80d_-Uu_uPbE0vASawCqen_BrSr8hVtkelay_cpU
CORS_ORIGINS = ["https://www.regenord.com"]
LOG_LEVEL = INFO
LOG_FILE = ./logs/aia-regenord.log
```

**Note:** `DATABASE_URL` est ajouté automatiquement par Railway.

### 5. Déployer

1. Railway va **déployer automatiquement**
2. **Voir les logs:** Service backend → "Deployments" → Cliquer sur le déploiement → "View Logs"
3. **Attendre 2-5 minutes** pour le build

### 6. Obtenir l'URL Railway

1. Une fois déployé: Service backend → **"Settings"** → **"Networking"**
2. **Noter l'URL générée** (ex: `https://aia-regenord-production.up.railway.app`)
3. **OU cliquer sur "Generate Domain"** pour obtenir une URL

### 7. Ajouter APP_BASE_URL

1. Dans **"Variables"**, ajouter:
   ```
   APP_BASE_URL = https://[VOTRE-URL-RAILWAY]
   ```
   (Remplacer par votre URL Railway réelle)

2. Railway redémarre automatiquement

### 8. Mettre à Jour Squarespace

1. **Ouvrir:** `SQUARESPACE_CODE_INJECTION_READY.html`
2. **Ligne 13**, remplacer:
   ```javascript
   const BACKEND_URL = 'https://api.regenord.com';
   ```
   **Par votre URL Railway:**
   ```javascript
   const BACKEND_URL = 'https://[VOTRE-URL-RAILWAY]';
   ```

3. **Réinjecter dans Squarespace:**
   - Settings → Advanced → Code Injection → Footer
   - Coller le code mis à jour
   - Save

### 9. Tester

1. **Aller sur:** `https://www.regenord.com/quickbooks-integration`
2. **Ouvrir la console** (F12)
3. **Vérifier qu'il n'y a pas d'erreurs**
4. **L'interface devrait apparaître!**

---

## 📋 Checklist Rapide

- [ ] Code poussé sur GitHub (ou Railway accède au repo)
- [ ] Compte Railway créé
- [ ] Projet Railway créé et connecté à GitHub
- [ ] Service backend configuré (Root Directory: backend)
- [ ] PostgreSQL ajouté
- [ ] Variables d'environnement ajoutées (voir `VARIABLES_RAILWAY.txt`)
- [ ] Déploiement réussi (vérifier les logs)
- [ ] URL Railway obtenue
- [ ] `APP_BASE_URL` ajouté avec l'URL Railway
- [ ] Test `/health` fonctionne
- [ ] Code Squarespace mis à jour avec l'URL Railway
- [ ] Code réinjecté dans Squarespace
- [ ] Test sur `https://www.regenord.com/quickbooks-integration` réussit

---

## 🎯 Résumé - Temps Estimé: 15-20 minutes

1. **Pousser sur GitHub:** 2 minutes
2. **Configurer Railway:** 5 minutes
3. **Ajouter PostgreSQL:** 1 minute
4. **Configurer les variables:** 3 minutes
5. **Attendre le déploiement:** 3-5 minutes
6. **Mettre à jour Squarespace:** 2 minutes
7. **Tester:** 2 minutes

---

## 📖 Guides Disponibles

- **Ce guide:** `ACTION_IMMEDIATE.md` (démarrage rapide)
- **Guide détaillé:** `FINALISER_RAILWAY.md`
- **Guide complet:** `DEPLOIEMENT_RAILWAY_RENDER.md`

---

**Vous êtes prêt! Commencez par pousser sur GitHub, puis suivez les étapes ci-dessus.**
