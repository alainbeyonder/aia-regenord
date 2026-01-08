# ⚡ Commandes Finales - Déploiement Railway

## ✅ État Actuel

- ✅ Code préparé et commité localement
- ✅ Fichiers de configuration créés
- ✅ Variables prêtes à copier

---

## 🚀 Commandes à Exécuter

### 1. Pousser le Code sur GitHub

```bash
cd /Users/alain/Documents/aia-regenord
git push origin main
```

**Si authentification requise:**
- GitHub vous demandera votre nom d'utilisateur et un token
- Créer un token: https://github.com/settings/tokens
- Sélectionner les permissions: `repo`

### 2. Créer un Projet Railway

**Manuellement dans le navigateur:**
1. Aller sur: https://railway.app
2. Se connecter avec GitHub
3. Cliquer "New Project"
4. Sélectionner "Deploy from GitHub repo"
5. Choisir: `alainbeyonder/aia-regenord`

---

## 📋 Configuration Railway (Interface Web)

### Service Backend

1. **Cliquer sur le service backend** créé automatiquement
2. **Settings** → **"Build & Deploy"**
3. Vérifier:
   - **Root Directory:** `backend` ✅
   - **Build Command:** `pip install -r requirements.txt` ✅ (dans railway.json)
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT` ✅ (dans railway.json)

### Ajouter PostgreSQL

1. Dans le projet Railway: **"New"** → **"Database"** → **"Add PostgreSQL"**
2. `DATABASE_URL` sera ajouté automatiquement

### Variables d'Environnement

Dans le service backend → **"Variables"** → Ajouter:

| Variable | Valeur |
|----------|--------|
| `QBO_ENVIRONMENT` | `production` |
| `QBO_CLIENT_ID` | `ABhjTWUsPqScOqpWeCghMKHpx85MbL0fM9JQnt4uXpD4Wynk` |
| `QBO_CLIENT_SECRET` | `d2R1L2EFjbZyNmJdcYnnbibh6AVsIVlZDFF9dc8V` |
| `QBO_REDIRECT_URI` | `https://www.regenord.com/quickbooks-integration/callback` |
| `APP_NAME` | `AIA Regenord` |
| `APP_ENV` | `production` |
| `DEBUG` | `False` |
| `FRONTEND_URL` | `https://www.regenord.com` |
| `AIA_TOKEN_ENCRYPTION_KEY` | `Jc8GWiI1zrJ9a-aWYgETa42PLx3FRUjbkJzQ_SEIg3c=` |
| `SECRET_KEY` | `o8x80d_-Uu_uPbE0vASawCqen_BrSr8hVtkelay_cpU` |
| `CORS_ORIGINS` | `["https://www.regenord.com"]` |
| `LOG_LEVEL` | `INFO` |
| `LOG_FILE` | `./logs/aia-regenord.log` |

**Note:** `APP_BASE_URL` sera ajouté APRÈS le premier déploiement (voir ci-dessous)

---

## 🔄 Après le Premier Déploiement

1. **Attendre que le build soit terminé** (2-5 minutes)
2. **Obtenir l'URL Railway:**
   - Service backend → **"Settings"** → **"Networking"**
   - Noter l'URL générée (ex: `https://aia-regenord-production.up.railway.app`)
3. **Ajouter la variable:**
   - **"Variables"** → Ajouter:
   - `APP_BASE_URL` = `https://[VOTRE-URL-RAILWAY]`
4. Railway redémarre automatiquement

---

## 📄 Mettre à Jour Squarespace

1. **Ouvrir:** `SQUARESPACE_CODE_INJECTION_READY.html`
2. **Ligne 13**, remplacer:
   ```javascript
   const BACKEND_URL = 'https://api.regenord.com';
   ```
   Par votre URL Railway:
   ```javascript
   const BACKEND_URL = 'https://[VOTRE-URL-RAILWAY]';
   ```
3. **Réinjecter dans Squarespace:**
   - Settings → Advanced → Code Injection → Footer
   - Coller le code mis à jour
   - Save

---

## ✅ Vérification

```bash
# Test santé
curl https://[VOTRE-URL-RAILWAY]/health

# Test config QBO
curl https://[VOTRE-URL-RAILWAY]/api/qbo/config/check

# Test depuis Squarespace
# Ouvrir: https://www.regenord.com/quickbooks-integration
# Console (F12) → Tester:
fetch('https://[VOTRE-URL-RAILWAY]/health')
  .then(r => r.json())
  .then(console.log)
```

---

## 📖 Guides Complets

- **Démarrage rapide:** `DEMARRAGE_RAILWAY_RAPIDE.md`
- **Finalisation:** `FINALISER_RAILWAY.md`
- **Guide complet:** `DEPLOIEMENT_RAILWAY_RENDER.md`

---

**Le code est prêt! Il ne reste qu'à pousser sur GitHub et configurer Railway!**
