# ⚡ Démarrage Rapide - Railway

Guide ultra-rapide pour déployer sur Railway en 5 minutes.

---

## ✅ Prérequis Vérifiés

- ✅ Git initialisé
- ✅ Repository GitHub: `alainbeyonder/aia-regenord`
- ✅ Tous les fichiers nécessaires présents
- ✅ Configuration backend/.env prête

---

## 🚀 Déploiement en 5 Étapes

### Étape 1: Pousser le Code sur GitHub

```bash
cd /Users/alain/Documents/aia-regenord

# Vérifier les changements
git status

# Ajouter tous les fichiers (sauf ceux dans .gitignore)
git add .

# Commit
git commit -m "Production ready - Railway deployment"

# Pousser vers GitHub
git push origin main
```

### Étape 2: Créer un Compte Railway

1. Aller sur: https://railway.app
2. Cliquer sur **"Start a New Project"**
3. Se connecter avec **GitHub**
4. Autoriser Railway à accéder à vos repositories

### Étape 3: Créer un Nouveau Projet

1. Cliquer sur **"New Project"**
2. Sélectionner **"Deploy from GitHub repo"**
3. Choisir le repository: **`alainbeyonder/aia-regenord`**
4. Railway va détecter automatiquement le backend

### Étape 4: Configurer le Service Backend

Railway devrait détecter automatiquement, mais vérifier:

1. **Cliquer sur le service backend** (s'il n'apparaît pas, cliquer sur "Add Service" → "GitHub Repo")
2. Aller dans **"Settings"** → **"Build & Deploy"**
3. Configurer:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Étape 5: Ajouter PostgreSQL et Variables

#### A. Ajouter PostgreSQL

1. Dans le projet Railway, cliquer sur **"New"**
2. Sélectionner **"Database"** → **"Add PostgreSQL"**
3. Railway créera automatiquement la base de données
4. `DATABASE_URL` sera automatiquement ajouté aux variables

#### B. Ajouter les Variables d'Environnement

1. **Cliquer sur le service backend**
2. Aller dans **"Variables"**
3. Ajouter chaque variable (copier-coller):

```env
QBO_ENVIRONMENT=production
QBO_CLIENT_ID=ABhjTWUsPqScOqpWeCghMKHpx85MbL0fM9JQnt4uXpD4Wynk
QBO_CLIENT_SECRET=d2R1L2EFjbZyNmJdcYnnbibh6AVsIVlZDFF9dc8V
QBO_REDIRECT_URI=https://www.regenord.com/quickbooks-integration/callback
APP_NAME=AIA Regenord
APP_ENV=production
DEBUG=False
FRONTEND_URL=https://www.regenord.com
AIA_TOKEN_ENCRYPTION_KEY=Jc8GWiI1zrJ9a-aWYgETa42PLx3FRUjbkJzQ_SEIg3c=
SECRET_KEY=o8x80d_-Uu_uPbE0vASawCqen_BrSr8hVtkelay_cpU
CORS_ORIGINS=["https://www.regenord.com"]
LOG_LEVEL=INFO
LOG_FILE=./logs/aia-regenord.log
```

**Important pour APP_BASE_URL:**

1. **D'abord**, laisser Railway déployer une première fois
2. **Ensuite**, Railway donnera une URL (ex: `https://aia-regenord-production.up.railway.app`)
3. **Ajouter la variable:**
   ```env
   APP_BASE_URL=https://aia-regenord-production.up.railway.app
   ```
   (Utiliser votre URL Railway réelle)

### Étape 6: Déployer

1. Railway va déployer automatiquement après avoir configuré les variables
2. **Voir les logs** dans l'onglet **"Deployments"** → Cliquer sur un déploiement → **"View Logs"**
3. **Attendre que le build soit terminé** (2-5 minutes)

### Étape 7: Obtenir l'URL du Backend

1. Dans le service backend, aller dans **"Settings"** → **"Networking"**
2. **Notez l'URL générée** (ex: `https://aia-regenord-production.up.railway.app`)
3. **Ou générer un domaine** en cliquant sur **"Generate Domain"**

### Étape 8: Mettre à Jour le Code Squarespace

1. **Ouvrir** `SQUARESPACE_CODE_INJECTION_READY.html`
2. **Remplacer la ligne 13:**
   ```javascript
   const BACKEND_URL = 'https://api.regenord.com';
   ```
   **Par votre URL Railway:**
   ```javascript
   const BACKEND_URL = 'https://aia-regenord-production.up.railway.app';
   ```
   (Utiliser votre URL Railway réelle)

3. **Réinjecter dans Squarespace:**
   - Settings → Advanced → Code Injection → Footer
   - Coller le code mis à jour
   - Save

### Étape 9: Configurer un Domaine Personnalisé (Optionnel)

Si vous voulez utiliser `api.regenord.com`:

1. Dans le service backend → **"Settings"** → **"Networking"**
2. Cliquer sur **"Custom Domain"**
3. Entrer: `api.regenord.com`
4. Railway vous donnera un enregistrement CNAME
5. **Ajouter dans votre DNS:**
   - Type: CNAME
   - Nom: api
   - Valeur: L'URL fournie par Railway
6. Attendre la propagation (5-30 minutes)
7. **Mettre à jour APP_BASE_URL** dans Railway: `https://api.regenord.com`
8. **Mettre à jour le code Squarespace** avec `https://api.regenord.com`

---

## ✅ Vérification

### Test 1: Santé du Backend

```bash
curl https://VOTRE-URL-RAILWAY/health
```

**Réponse attendue:**
```json
{"status": "healthy"}
```

### Test 2: Configuration QBO

```bash
curl https://VOTRE-URL-RAILWAY/api/qbo/config/check
```

**Vérifier:**
- `"environment": "production"`
- `"ready_for_production": true`

### Test 3: Depuis Squarespace

1. Aller sur: `https://www.regenord.com/quickbooks-integration`
2. Ouvrir la console (F12)
3. Vérifier qu'il n'y a pas d'erreurs
4. L'interface devrait apparaître!

---

## 🔄 Mises à Jour Futures

Les mises à jour sont automatiques:

1. Faire des modifications dans votre code
2. Committer et pousser sur GitHub:
   ```bash
   git add .
   git commit -m "Description des changements"
   git push origin main
   ```
3. Railway déploie automatiquement!

---

## 🐛 Dépannage

### Le déploiement échoue

**Vérifier les logs:**
1. Dans Railway → Service backend → **"Deployments"**
2. Cliquer sur le déploiement qui a échoué
3. **"View Logs"** pour voir l'erreur

**Erreurs courantes:**
- Variables d'environnement manquantes → Vérifier toutes les variables
- Build command incorrect → Vérifier "Build & Deploy" settings
- Port incorrect → S'assurer d'utiliser `$PORT` dans la commande start

### Erreur de connexion base de données

**Vérifier:**
1. Le service PostgreSQL est créé
2. `DATABASE_URL` est dans les variables du service backend
3. Les logs pour voir l'erreur exacte

### L'interface Squarespace ne fonctionne toujours pas

**Vérifier:**
1. Le code Squarespace est mis à jour avec la bonne URL Railway
2. Ouvrir la console (F12) sur la page Squarespace
3. Vérifier les erreurs JavaScript
4. Tester: `fetch('https://VOTRE-URL-RAILWAY/health')` dans la console

---

## 📚 Documentation Complète

Pour plus de détails, voir:
- **Guide complet Railway/Render:** `DEPLOIEMENT_RAILWAY_RENDER.md`
- **Guide général:** `DEPLOIEMENT_ETAPE_PAR_ETAPE.md`

---

**Temps estimé:** 10-15 minutes  
**Difficulté:** ⭐ Facile

---

**Date de création:** $(date)  
**Version:** Production 1.0
