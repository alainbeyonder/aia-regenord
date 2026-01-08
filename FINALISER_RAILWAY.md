# ✅ Finaliser le Déploiement Railway - Étapes Finales

Le code est maintenant sur GitHub. Il ne reste plus qu'à configurer Railway.

---

## 🚀 Étapes Finales dans Railway

### 1. Créer un Compte/Projet Railway

1. **Aller sur:** https://railway.app
2. **Cliquer:** "Start a New Project" ou "Login"
3. **Se connecter avec GitHub**
4. **Autoriser Railway** à accéder à vos repositories

### 2. Créer un Nouveau Projet

1. **Cliquer:** "New Project"
2. **Sélectionner:** "Deploy from GitHub repo"
3. **Choisir le repository:** `alainbeyonder/aia-regenord`
4. Railway va détecter automatiquement le backend

### 3. Configurer le Service Backend

1. **Cliquer sur le service backend** (s'il n'apparaît pas, Railway va le créer automatiquement)
2. **Aller dans "Settings"** → **"Build & Deploy"**
3. **Vérifier/Configurer:**
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt` (déjà dans railway.json)
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT` (déjà dans railway.json)

**Note:** Le fichier `backend/railway.json` devrait être détecté automatiquement par Railway.

### 4. Ajouter PostgreSQL

1. Dans le projet Railway, **cliquer sur "New"**
2. **Sélectionner:** "Database" → **"Add PostgreSQL"**
3. Railway créera automatiquement la base de données
4. **`DATABASE_URL` sera automatiquement ajouté** aux variables du service backend

### 5. Ajouter les Variables d'Environnement

1. **Cliquer sur le service backend**
2. **Aller dans l'onglet "Variables"**
3. **Ajouter les variables suivantes** (une par une, cliquer sur "New Variable" pour chaque):

**Variables à ajouter:**

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

**Important:** 
- `DATABASE_URL` sera ajouté automatiquement par Railway (ne pas l'ajouter manuellement)
- `APP_BASE_URL` sera ajouté APRÈS le premier déploiement (voir étape suivante)

### 6. Déployer

1. Railway va **déployer automatiquement** après avoir ajouté les variables
2. **Voir les logs:**
   - Onglet **"Deployments"**
   - Cliquer sur le déploiement en cours
   - **"View Logs"** pour voir le progrès
3. **Attendre 2-5 minutes** pour que le build soit terminé

### 7. Obtenir l'URL Railway

Une fois le déploiement terminé:

1. **Aller dans:** Service backend → **"Settings"** → **"Networking"**
2. **Noter l'URL générée** (ex: `https://aia-regenord-production.up.railway.app`)
3. **OU cliquer sur "Generate Domain"** pour obtenir une URL

### 8. Ajouter APP_BASE_URL

1. Dans **"Variables"**, ajouter:
   ```
   APP_BASE_URL = https://[VOTRE-URL-RAILWAY]
   ```
   (Remplacer par votre URL Railway réelle, ex: `https://aia-regenord-production.up.railway.app`)

2. Railway redémarre automatiquement le service

### 9. Vérifier le Déploiement

```bash
# Remplacer par votre URL Railway
curl https://[VOTRE-URL-RAILWAY]/health

# Devrait retourner:
# {"status":"healthy"}

curl https://[VOTRE-URL-RAILWAY]/api/qbo/config/check

# Devrait montrer:
# "environment": "production"
# "ready_for_production": true
```

### 10. Mettre à Jour le Code Squarespace

1. **Ouvrir:** `SQUARESPACE_CODE_INJECTION_READY.html`
2. **Ligne 13**, remplacer:
   ```javascript
   const BACKEND_URL = 'https://api.regenord.com';
   ```
   **Par:**
   ```javascript
   const BACKEND_URL = 'https://[VOTRE-URL-RAILWAY]';
   ```
   (Utiliser votre URL Railway réelle)

3. **Réinjecter dans Squarespace:**
   - Settings → Advanced → Code Injection → Footer
   - Coller le code mis à jour
   - Save

### 11. Tester

1. **Aller sur:** `https://www.regenord.com/quickbooks-integration`
2. **Ouvrir la console** (F12)
3. **Vérifier qu'il n'y a pas d'erreurs**
4. **L'interface devrait apparaître!**

---

## 🎯 Option: Domaine Personnalisé (Plus tard)

Si vous voulez utiliser `api.regenord.com` au lieu de l'URL Railway:

1. Dans Railway: Service backend → **"Settings"** → **"Networking"**
2. **"Custom Domain"** → Entrer: `api.regenord.com`
3. Railway donnera un enregistrement CNAME
4. **Ajouter dans votre DNS:**
   - Type: CNAME
   - Nom: api
   - Valeur: L'URL fournie par Railway
5. Attendre 5-30 minutes pour la propagation
6. **Mettre à jour `APP_BASE_URL`** dans Railway: `https://api.regenord.com`
7. **Mettre à jour le code Squarespace** avec `https://api.regenord.com`

---

## ✅ Checklist de Déploiement

- [ ] Code poussé sur GitHub
- [ ] Compte Railway créé
- [ ] Projet Railway créé et connecté à GitHub
- [ ] Service backend configuré (Root Directory: backend)
- [ ] PostgreSQL ajouté
- [ ] Toutes les variables d'environnement ajoutées
- [ ] Déploiement réussi (voir les logs)
- [ ] URL Railway obtenue
- [ ] `APP_BASE_URL` ajouté avec l'URL Railway
- [ ] Test `/health` fonctionne
- [ ] Test `/api/qbo/config/check` montre production
- [ ] Code Squarespace mis à jour avec l'URL Railway
- [ ] Code réinjecté dans Squarespace
- [ ] Test sur `https://www.regenord.com/quickbooks-integration` réussit

---

## 🎉 Déploiement Réussi!

Une fois toutes les étapes terminées:

✅ Le backend sera accessible sur Railway  
✅ Le frontend Squarespace pourra se connecter  
✅ L'intégration QuickBooks sera opérationnelle en production!

---

**Temps estimé:** 10-15 minutes  
**Difficulté:** ⭐ Facile

---

**Date de création:** $(date)  
**Version:** Production 1.0
