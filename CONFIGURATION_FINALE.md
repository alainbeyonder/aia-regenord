# ✅ Configuration Finale - Production

## 🎯 URLs Configurées

- **Backend API:** `https://api.regenord.com` ✅
- **Frontend:** `https://www.regenord.com` ✅
- **Page d'intégration:** `https://www.regenord.com/quickbooks-integration` ✅

## 🔗 OAuth URLs

- **Redirect URI:** `https://www.regenord.com/quickbooks-integration/callback` ✅
- **Launch URL:** `https://www.regenord.com/quickbooks-integration/connect` ✅
- **Disconnect URL:** `https://www.regenord.com/quickbooks-integration/disconnect` ✅

---

## 📁 Fichiers Créés et Configurés

### 1. Code Squarespace ✅

**Fichier:** `SQUARESPACE_CODE_INJECTION_READY.html`

**✅ Statut:** PRÊT À INJECTER
- URL backend configurée: `https://api.regenord.com`
- Code complet et fonctionnel
- Instructions incluses

**Action:**
1. Ouvrir `SQUARESPACE_CODE_INJECTION_READY.html`
2. Sélectionner TOUT (Cmd+A)
3. Copier (Cmd+C)
4. Dans Squarespace: **Settings > Advanced > Code Injection > Footer**
5. Coller et sauvegarder

### 2. Configuration Backend ⏳

**Fichier:** `backend/.env.production`

**✅ Statut:** TEMPLATE CRÉÉ

**⚠️ Actions requises:**
1. Renommer/copier vers `backend/.env`
2. Générer les clés de sécurité
3. Configurer `DATABASE_URL`

**Générer les clés:**
```bash
cd /Users/alain/Documents/aia-regenord
python3 scripts/generate_security_keys.py
```

Puis copier les clés dans `backend/.env`:
- `AIA_TOKEN_ENCRYPTION_KEY` (clé Fernet)
- `SECRET_KEY` (clé secrète)

---

## 🔧 Configuration Backend Complète

### backend/.env (à créer)

```env
# QuickBooks Online - PRODUCTION
QBO_ENVIRONMENT=production
QBO_CLIENT_ID=ABhjTWUsPqScOqpWeCghMKHpx85MbL0fM9JQnt4uXpD4Wynk
QBO_CLIENT_SECRET=d2R1L2EFjbZyNmJdcYnnbibh6AVsIVlZDFF9dc8V
QBO_REDIRECT_URI=https://www.regenord.com/quickbooks-integration/callback

# Application
APP_NAME=AIA Regenord
APP_ENV=production
DEBUG=False
APP_BASE_URL=https://api.regenord.com
FRONTEND_URL=https://www.regenord.com

# Sécurité (GÉNÉRER avec: python3 scripts/generate_security_keys.py)
AIA_TOKEN_ENCRYPTION_KEY=<clé_fernet_générée>
SECRET_KEY=<clé_secrète_générée>

# Base de données (À CONFIGURER)
DATABASE_URL=postgresql://user:password@host:5432/aia_regenord

# CORS
CORS_ORIGINS=["https://www.regenord.com"]

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/aia-regenord.log
```

---

## ✅ Checklist Finale

### Configuration Intuit Developer ✅

- [x] Client ID configuré
- [x] Client Secret configuré
- [x] Redirect URI: `https://www.regenord.com/quickbooks-integration/callback`
- [x] Application en mode Production
- [x] Questionnaire complété et approuvé

### Backend Configuration ⏳

- [ ] Fichier `backend/.env` créé (copier depuis `backend/.env.production`)
- [ ] Clés de sécurité générées et ajoutées
- [ ] `DATABASE_URL` configuré selon votre déploiement
- [ ] Backend déployé sur `https://api.regenord.com`
- [ ] CORS configuré pour `https://www.regenord.com`
- [ ] Test de connectivité: `curl https://api.regenord.com/api/qbo/config/check`

### Squarespace Injection ⏳

- [ ] Ouvrir `SQUARESPACE_CODE_INJECTION_READY.html`
- [ ] Copier tout le contenu
- [ ] Coller dans **Settings > Advanced > Code Injection > Footer**
- [ ] Sauvegarder
- [ ] Tester sur `https://www.regenord.com/quickbooks-integration`

### Tests Finaux ⏳

- [ ] Interface QuickBooks s'affiche correctement
- [ ] Test de connexion OAuth réussi
- [ ] Statut de connexion se met à jour
- [ ] Test de déconnexion réussi

---

## 🧪 Tests de Validation

### Test 1: Backend Accessible

```bash
curl https://api.regenord.com/api/qbo/config/check
```

**Résultat attendu:**
```json
{
  "configuration": {
    "environment": "production",
    "status": "ok"
  },
  "ready_for_production": true
}
```

### Test 2: CORS Configuré

```bash
curl -H "Origin: https://www.regenord.com" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     https://api.regenord.com/api/qbo/status
```

Vérifier les en-têtes `Access-Control-Allow-Origin` dans la réponse.

### Test 3: Interface Squarespace

1. Aller sur `https://www.regenord.com/quickbooks-integration`
2. Vérifier que l'interface s'affiche
3. Vérifier que le statut se charge (connecté/non connecté)

### Test 4: Connexion OAuth

1. Cliquer sur "Connecter QuickBooks"
2. Autoriser dans Intuit
3. Vérifier la redirection vers Squarespace
4. Vérifier que le statut affiche "✅ QuickBooks Connecté"

---

## 🐛 Dépannage

### Backend non accessible

**Vérifications:**
1. Le backend est-il déployé sur `https://api.regenord.com`?
2. Le DNS pointe-t-il vers le bon serveur?
3. HTTPS est-il configuré correctement?
4. Le backend est-il en cours d'exécution?

### Erreur CORS

**Solution:**
Vérifier que `CORS_ORIGINS=["https://www.regenord.com"]` est dans `backend/.env`
Redémarrer le backend après modification

### Interface ne s'affiche pas

**Vérifications:**
1. Code bien injecté dans **Footer** (pas Header)
2. Pas d'erreurs dans la console du navigateur (F12)
3. `BACKEND_URL` correct dans le code (`https://api.regenord.com`)

---

## 🎉 Prochaines Étapes

1. **Générer les clés de sécurité:**
   ```bash
   python3 scripts/generate_security_keys.py
   ```

2. **Créer backend/.env:**
   ```bash
   cp backend/.env.production backend/.env
   # Puis éditer et ajouter les clés générées
   ```

3. **Injecter le code Squarespace:**
   - Ouvrir `SQUARESPACE_CODE_INJECTION_READY.html`
   - Copier tout le contenu
   - Coller dans Squarespace: Settings > Advanced > Code Injection > Footer

4. **Tester:**
   - Aller sur `https://www.regenord.com/quickbooks-integration`
   - Tester la connexion OAuth

---

**Date:** $(date)  
**Version:** 1.0  
**Statut:** Configuration prête pour injection ✅
