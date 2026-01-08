# 🚀 Démarrage Complet - De Zéro à Production

Guide complet pour déployer l'intégration QuickBooks Online en production, étape par étape.

---

## 📋 Vue d'Ensemble

**Objectif:** Déployer le backend sur Railway et connecter le frontend Squarespace.

**Temps estimé:** 20-30 minutes  
**Difficulté:** ⭐⭐ Moyenne

---

## ✅ Étape 0: Vérification de l'État Actuel

### Ce qui est déjà fait:

- ✅ Backend configuré avec credentials production
- ✅ Code commité localement
- ✅ Repository GitHub: `alainbeyonder/aia-regenord`
- ✅ Fichiers de configuration créés
- ✅ Code Squarespace prêt

### Ce qui reste à faire:

- [ ] Pousser le code sur GitHub
- [ ] Déployer sur Railway
- [ ] Mettre à jour Squarespace avec l'URL Railway

---

## 🚀 Partie 1: Pousser le Code sur GitHub

### Option A: Avec Personal Access Token (Rapide)

1. **Créer un token GitHub:**
   - Aller sur: https://github.com/settings/tokens
   - Cliquer: "Generate new token (classic)"
   - Nom: "Railway Deployment"
   - Sélectionner: `repo` (toutes les permissions)
   - Générer et **copier le token**

2. **Pousser le code:**
   ```bash
   cd /Users/alain/Documents/aia-regenord
   git push origin main
   ```
   - Username: `alainbeyonder`
   - Password: **Coller le token** (pas votre mot de passe!)

### Option B: Avec GitHub Desktop (Plus Simple)

1. Ouvrir GitHub Desktop
2. Ajouter le repository: `aia-regenord`
3. Cliquer "Publish branch" ou "Push origin"

### Option C: Configurer SSH (Permanent)

```bash
# Générer une clé SSH
ssh-keygen -t ed25519 -C "votre_email@example.com"
# Appuyer sur Entrée pour accepter les valeurs par défaut

# Afficher la clé publique
cat ~/.ssh/id_ed25519.pub

# Copier la clé et l'ajouter sur GitHub:
# https://github.com/settings/keys → New SSH key

# Changer le remote vers SSH
cd /Users/alain/Documents/aia-regenord
git remote set-url origin git@github.com:alainbeyonder/aia-regenord.git

# Pousser (plus besoin de mot de passe!)
git push origin main
```

**Une fois le push réussi, passer à la Partie 2.**

---

## 🚂 Partie 2: Déployer sur Railway

### Étape 1: Créer un Compte Railway

1. Aller sur: https://railway.app
2. Cliquer: "Start a New Project"
3. Se connecter avec **GitHub**
4. Autoriser Railway à accéder à vos repositories

### Étape 2: Créer un Nouveau Projet

1. Cliquer: **"New Project"**
2. Sélectionner: **"Deploy from GitHub repo"**
3. Choisir: `alainbeyonder/aia-regenord`
4. Railway va détecter automatiquement le backend

### Étape 3: Configurer le Service Backend

Railway devrait détecter automatiquement grâce à `backend/railway.json`.

**Vérifier dans Settings → Build & Deploy:**
- **Root Directory:** `backend` ✅
- **Build Command:** `pip install -r requirements.txt` ✅
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT` ✅

### Étape 4: Ajouter PostgreSQL

1. Dans le projet Railway: Cliquer **"New"**
2. Sélectionner: **"Database"** → **"Add PostgreSQL"**
3. Railway créera automatiquement la base de données
4. **`DATABASE_URL` sera automatiquement ajouté** aux variables

### Étape 5: Configurer les Variables d'Environnement

1. **Cliquer sur le service backend**
2. Aller dans l'onglet **"Variables"**
3. Ajouter chaque variable (copier depuis `VARIABLES_RAILWAY.txt`):

**Variables à ajouter (une par une):**

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

### Étape 6: Déployer

1. Railway va **déployer automatiquement** après avoir ajouté les variables
2. **Voir les logs:**
   - Onglet **"Deployments"**
   - Cliquer sur le déploiement en cours
   - **"View Logs"** pour voir le progrès
3. **Attendre 2-5 minutes** pour que le build soit terminé

### Étape 7: Obtenir l'URL Railway

Une fois le déploiement terminé:

1. **Aller dans:** Service backend → **"Settings"** → **"Networking"**
2. **Noter l'URL générée** (ex: `https://aia-regenord-production.up.railway.app`)
3. **OU cliquer sur "Generate Domain"** pour obtenir une URL

**⚠️ IMPORTANT:** Notez cette URL, vous en aurez besoin pour la prochaine étape!

### Étape 8: Ajouter APP_BASE_URL

1. Dans **"Variables"**, ajouter:
   ```
   APP_BASE_URL = https://[VOTRE-URL-RAILWAY]
   ```
   (Remplacer par votre URL Railway réelle)

2. Railway redémarre automatiquement le service

### Étape 9: Vérifier le Déploiement

```bash
# Test 1: Santé
curl https://[VOTRE-URL-RAILWAY]/health
# Réponse attendue: {"status":"healthy"}

# Test 2: Configuration QBO
curl https://[VOTRE-URL-RAILWAY]/api/qbo/config/check
# Vérifier: "environment": "production", "ready_for_production": true
```

---

## 📄 Partie 3: Mettre à Jour Squarespace

### Étape 1: Modifier le Code Squarespace

1. **Ouvrir:** `SQUARESPACE_CODE_INJECTION_READY.html`
2. **Ligne 13**, remplacer:
   ```javascript
   const BACKEND_URL = 'https://api.regenord.com';
   ```
   **Par votre URL Railway:**
   ```javascript
   const BACKEND_URL = 'https://[VOTRE-URL-RAILWAY]';
   ```
   (Utiliser votre URL Railway réelle, ex: `https://aia-regenord-production.up.railway.app`)

3. **Sauvegarder** le fichier

### Étape 2: Injecter dans Squarespace

1. **Se connecter à Squarespace:**
   - Aller sur: https://www.squarespace.com
   - Se connecter avec votre compte

2. **Accéder aux paramètres:**
   - Cliquer sur votre site
   - Aller dans **Settings** (Paramètres)
   - Dans le menu latéral: **Advanced** (Avancé)
   - Cliquer sur **Code Injection** (Injection de code)

3. **Injecter le code:**
   - Dans la section **Footer** (Pied de page)
   - **Sélectionner tout** le contenu de `SQUARESPACE_CODE_INJECTION_READY.html`
   - **Copier** (Cmd+C / Ctrl+C)
   - **Coller** dans la section Footer (Cmd+V / Ctrl+V)
   - Cliquer sur **Save** (Enregistrer)

4. **Publier les changements** (si nécessaire)

### Étape 3: Tester

1. **Aller sur:** `https://www.regenord.com/quickbooks-integration`
2. **Ouvrir la console du navigateur** (F12)
3. **Vérifier qu'il n'y a pas d'erreurs JavaScript**
4. **L'interface devrait apparaître!**

---

## ✅ Checklist Complète

### Préparation
- [ ] Backend configuré (`backend/.env` avec toutes les variables)
- [ ] Code commité localement
- [ ] Repository GitHub configuré

### GitHub
- [ ] Code poussé sur GitHub
- [ ] Repository accessible sur GitHub

### Railway
- [ ] Compte Railway créé
- [ ] Projet Railway créé et connecté à GitHub
- [ ] Service backend configuré (Root Directory: backend)
- [ ] PostgreSQL ajouté
- [ ] Toutes les variables d'environnement ajoutées
- [ ] Déploiement réussi (vérifier les logs)
- [ ] URL Railway obtenue
- [ ] `APP_BASE_URL` ajouté avec l'URL Railway
- [ ] Test `/health` fonctionne
- [ ] Test `/api/qbo/config/check` montre production

### Squarespace
- [ ] Code Squarespace mis à jour avec l'URL Railway
- [ ] Code injecté dans Squarespace (Settings → Advanced → Code Injection → Footer)
- [ ] Code sauvegardé
- [ ] Page publiée

### Tests
- [ ] Page Squarespace accessible
- [ ] Interface QuickBooks visible
- [ ] Pas d'erreurs dans la console
- [ ] Test de connexion OAuth fonctionne

---

## 🐛 Dépannage

### Le push GitHub échoue

**Solution:** Voir `GUIDE_PUSH_GITHUB.md` pour 4 méthodes différentes.

### Le déploiement Railway échoue

**Vérifier:**
- Les logs dans Railway → Deployments → View Logs
- Toutes les variables d'environnement sont présentes
- Root Directory est `backend`
- Build Command et Start Command sont corrects

### L'interface Squarespace ne s'affiche pas

**Vérifier:**
- Le code est injecté dans Footer (pas Header)
- L'URL Railway dans le code est correcte
- Ouvrir la console (F12) et vérifier les erreurs
- Tester: `fetch('https://[VOTRE-URL-RAILWAY]/health')` dans la console

---

## 📚 Guides de Référence

- **Push GitHub:** `GUIDE_PUSH_GITHUB.md`
- **Déploiement Railway:** `ACTION_IMMEDIATE.md` ou `DEPLOIEMENT_RAILWAY_RENDER.md`
- **Dépannage Squarespace:** `DEPANNAGE_SQUARESPACE.md`
- **Variables:** `VARIABLES_RAILWAY.txt`

---

## 🎉 Déploiement Réussi!

Une fois toutes les étapes terminées:

✅ Le backend sera accessible sur Railway  
✅ Le frontend Squarespace sera connecté  
✅ L'intégration QuickBooks sera opérationnelle en production!

Vous pourrez alors:
- Connecter des comptes QuickBooks en production
- Synchroniser des données financières réelles
- Générer des projections basées sur des données réelles

---

**Temps total estimé:** 20-30 minutes  
**Difficulté:** ⭐⭐ Moyenne

---

**Date de création:** $(date)  
**Version:** Production 1.0
