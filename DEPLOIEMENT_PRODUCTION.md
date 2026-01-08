# 🚀 Guide de Déploiement Production - QuickBooks Online

## ✅ Credentials Production Configurés

**Client ID:** `ABhjTWUsPqScOqpWeCghMKHpx85MbL0fM9JQnt4uXpD4Wynk`  
**Client Secret:** `d2R1L2EFjbZyNmJdcYnnbibh6AVsIVlZDFF9dc8V`  
**Environment:** Production

**URLs Squarespace:**
- Page: `https://www.regenord.com/quickbooks-integration`
- Callback: `https://www.regenord.com/quickbooks-integration/callback`

---

## 📋 Checklist de Déploiement

### 1. Configuration Intuit Developer

✅ **Vérifier dans Intuit Developer:**
- [ ] Application en mode **Production** (pas Sandbox)
- [ ] Client ID: `ABhjTWUsPqScOqpWeCghMKHpx85MbL0fM9JQnt4uXpD4Wynk`
- [ ] Redirect URI configurée: `https://www.regenord.com/quickbooks-integration/callback`
- [ ] Scopes autorisés: `com.intuit.quickbooks.accounting openid profile email`

### 2. Configuration Backend

#### A. Variables d'environnement

Créer/modifier `backend/.env`:

```env
# QuickBooks Production
QBO_ENVIRONMENT=production
QBO_CLIENT_ID=ABhjTWUsPqScOqpWeCghMKHpx85MbL0fM9JQnt4uXpD4Wynk
QBO_CLIENT_SECRET=d2R1L2EFjbZyNmJdcYnnbibh6AVsIVlZDFF9dc8V
QBO_REDIRECT_URI=https://www.regenord.com/quickbooks-integration/callback

# Backend URL (⚠️ À REMPLACER par votre URL réelle)
APP_BASE_URL=https://YOUR_BACKEND_URL
FRONTEND_URL=https://www.regenord.com

# Sécurité
# Générer avec: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
AIA_TOKEN_ENCRYPTION_KEY=YOUR_FERNET_KEY

# Générer avec: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=YOUR_SECRET_KEY

# CORS
CORS_ORIGINS=["https://www.regenord.com"]

# Base de données
DATABASE_URL=postgresql://user:password@host:5432/aia_regenord
```

#### B. Générer les clés de sécurité

```bash
# Clé Fernet pour l'encryption des tokens
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Clé secrète pour l'application
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copier les résultats dans `.env` pour `AIA_TOKEN_ENCRYPTION_KEY` et `SECRET_KEY`.

### 3. Configuration Squarespace

#### A. Créer la page

1. Aller dans **Pages > Add Page**
2. Créer une page nommée "QuickBooks Integration"
3. URL: `/quickbooks-integration`
4. Publier la page

#### B. Ajouter le code d'injection

1. Aller dans **Settings > Advanced > Code Injection**
2. Dans **Footer**, coller le contenu de `SQUARESPACE_CODE_INJECTION_FINAL.html`
3. **⚠️ IMPORTANT:** Remplacer `YOUR_BACKEND_URL` par l'URL réelle de votre backend
4. Sauvegarder

### 4. Vérification Intuit Developer

Dans [Intuit Developer Portal](https://developer.intuit.com/):

1. Aller dans votre application
2. Vérifier **Redirect URIs**:
   ```
   https://www.regenord.com/quickbooks-integration/callback
   ```
3. Vérifier **Scopes**:
   - `com.intuit.quickbooks.accounting`
   - `openid`
   - `profile`
   - `email`

---

## 🧪 Tests de Déploiement

### Test 1: Vérification Backend

```bash
# Vérifier la configuration
curl "https://YOUR_BACKEND_URL/api/qbo/config/check"
```

Résultat attendu:
```json
{
  "configuration": {
    "environment": "production",
    "client_id_configured": true,
    "client_secret_configured": true,
    "redirect_uri_configured": true,
    "status": "ok"
  },
  "ready_for_production": true
}
```

### Test 2: Test de Connexion OAuth

1. Aller sur `https://www.regenord.com/quickbooks-integration`
2. Cliquer sur "Connecter QuickBooks"
3. Vérifier la redirection vers Intuit OAuth (production)
4. Autoriser l'application
5. Vérifier la redirection vers Squarespace avec message de succès

### Test 3: Vérification du Statut

Après connexion, vérifier que:
- Le statut affiche "✅ QuickBooks Connecté"
- Le Realm ID est visible
- Le bouton "Déconnecter" est affiché

### Test 4: Test de Déconnexion

1. Cliquer sur "Déconnecter QuickBooks"
2. Confirmer
3. Vérifier que le statut change à "Non connecté"

---

## 🔒 Sécurité Production

### ✅ Vérifications

- [ ] HTTPS activé sur le backend
- [ ] `AIA_TOKEN_ENCRYPTION_KEY` générée et unique
- [ ] `SECRET_KEY` générée et unique
- [ ] CORS configuré uniquement pour `https://www.regenord.com`
- [ ] Credentials jamais dans le code source (uniquement dans `.env`)
- [ ] `.env` dans `.gitignore`

### ⚠️ Points d'attention

1. **Tokens encryptés**: Les tokens QBO sont encryptés avec Fernet
2. **Refresh automatique**: Les tokens sont rafraîchis automatiquement
3. **Rate limiting**: Surveiller les limites d'API QuickBooks
4. **Logs**: Ne pas logger les credentials ou tokens

---

## 📊 Endpoints Disponibles

### OAuth
- `GET /api/qbo/connect/production?company_id=1&redirect=false` - Obtenir URL OAuth
- `GET /api/qbo/callback?code=...&realmId=...&state=...` - Callback OAuth
- `POST /api/qbo/disconnect?company_id=1` - Déconnexion

### Statut & Données
- `GET /api/qbo/status?company_id=1` - Statut de connexion
- `GET /api/qbo/data?company_id=1&months=12` - Données brutes QBO
- `POST /api/qbo/sync?company_id=1&months=12` - Synchronisation manuelle

### AIA
- `GET /api/aia/view?company_id=1&months=12` - Vue financière AIA
- `GET /api/aia/export/google-sheets?company_id=1&months=12&format=csv` - Export CSV
- `GET /api/aia/export/google-sheets?company_id=1&months=12&format=json` - Export JSON

---

## 🔧 Dépannage

### Erreur: "Invalid redirect_uri"
- Vérifier que l'URL dans `.env` correspond exactement à celle dans Intuit Developer
- Pas de slash final
- HTTPS obligatoire

### Erreur: "Invalid client credentials"
- Vérifier que les credentials sont ceux de **Production** (pas Sandbox)
- Vérifier que l'application est en mode Production dans Intuit Developer

### Erreur CORS
- Vérifier que `CORS_ORIGINS` contient `https://www.regenord.com`
- Vérifier que le backend accepte les requêtes depuis Squarespace

### Le statut ne se charge pas
- Vérifier que `BACKEND_URL` dans le code Squarespace est correct
- Vérifier la console du navigateur (F12) pour les erreurs
- Vérifier que le backend est accessible publiquement

---

## ✅ Checklist Finale

- [ ] Backend déployé en production avec HTTPS
- [ ] Variables d'environnement configurées
- [ ] Clés de sécurité générées (Fernet + Secret)
- [ ] Intuit Developer configuré (Production)
- [ ] Redirect URI configurée dans Intuit
- [ ] Code Squarespace injecté avec BACKEND_URL correct
- [ ] Test de connexion réussi
- [ ] Test de déconnexion réussi
- [ ] CORS configuré correctement
- [ ] Logs et monitoring en place

---

**🎉 Prêt pour la production!**
