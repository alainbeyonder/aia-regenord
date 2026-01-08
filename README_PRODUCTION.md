# 🚀 Déploiement Production - QuickBooks Online

## ✅ Credentials Production

**Client ID:** `ABhjTWUsPqScOqpWeCghMKHpx85MbL0fM9JQnt4uXpD4Wynk`  
**Client Secret:** `d2R1L2EFjbZyNmJdcYnnbibh6AVsIVlZDFF9dc8V`  
**Environment:** Production

**URLs Squarespace:**
- Page: `https://www.regenord.com/quickbooks-integration`
- Callback: `https://www.regenord.com/quickbooks-integration/callback`

---

## 📋 Étapes de Déploiement

### Étape 1: Générer les Clés de Sécurité

```bash
cd /Users/alain/Documents/aia-regenord
python3 scripts/generate_security_keys.py
```

**OU manuellement:**

```bash
# Clé Fernet
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Clé Secrète
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Étape 2: Configurer le Backend

Créer/modifier `backend/.env`:

```env
# QuickBooks Production
QBO_ENVIRONMENT=production
QBO_CLIENT_ID=ABhjTWUsPqScOqpWeCghMKHpx85MbL0fM9JQnt4uXpD4Wynk
QBO_CLIENT_SECRET=d2R1L2EFjbZyNmJdcYnnbibh6AVsIVlZDFF9dc8V
QBO_REDIRECT_URI=https://www.regenord.com/quickbooks-integration/callback

# Backend URL (⚠️ REMPLACER par votre URL réelle)
APP_BASE_URL=https://YOUR_BACKEND_URL
FRONTEND_URL=https://www.regenord.com

# Sécurité (utiliser les clés générées à l'étape 1)
AIA_TOKEN_ENCRYPTION_KEY=<clé_fernet_générée>
SECRET_KEY=<clé_secrète_générée>

# CORS
CORS_ORIGINS=["https://www.regenord.com"]

# Base de données
DATABASE_URL=postgresql://user:password@host:5432/aia_regenord
```

### Étape 3: Configurer Intuit Developer

1. Aller sur https://developer.intuit.com/
2. Sélectionner votre application
3. Vérifier que l'application est en mode **Production**
4. Dans **Redirect URIs**, ajouter:
   ```
   https://www.regenord.com/quickbooks-integration/callback
   ```
5. Vérifier les **Scopes**:
   - `com.intuit.quickbooks.accounting`
   - `openid`
   - `profile`
   - `email`

### Étape 4: Injecter le Code dans Squarespace

1. Ouvrir le fichier `SQUARESPACE_CODE_INJECTION_FINAL.html`
2. **⚠️ IMPORTANT:** Remplacer `YOUR_BACKEND_URL` par l'URL réelle de votre backend
3. Copier tout le contenu du fichier
4. Dans Squarespace:
   - Aller dans **Settings > Advanced > Code Injection**
   - Coller le code dans **Footer**
   - Sauvegarder

### Étape 5: Créer la Page Squarespace

1. **Pages > Add Page**
2. Nom: "QuickBooks Integration"
3. URL: `/quickbooks-integration`
4. Publier la page

### Étape 6: Tester

1. Aller sur `https://www.regenord.com/quickbooks-integration`
2. Cliquer sur "Connecter QuickBooks"
3. Autoriser l'application dans Intuit
4. Vérifier la redirection et le message de succès

---

## 🔍 Vérification

### Test Backend

```bash
curl "https://YOUR_BACKEND_URL/api/qbo/config/check"
```

Résultat attendu:
```json
{
  "configuration": {
    "environment": "production",
    "status": "ok"
  },
  "ready_for_production": true
}
```

---

## 📚 Documentation

- `CONFIGURATION_PRODUCTION.md` - Guide de configuration détaillé
- `DEPLOIEMENT_PRODUCTION.md` - Guide complet de déploiement
- `SQUARESPACE_INTEGRATION.md` - Guide d'intégration Squarespace

---

## ⚠️ Points d'Attention

1. **URL Backend**: Remplacer `YOUR_BACKEND_URL` dans:
   - `backend/.env` (APP_BASE_URL)
   - Code Squarespace (BACKEND_URL)

2. **Sécurité**: 
   - Ne jamais committer le fichier `.env`
   - Garder les clés en sécurité
   - HTTPS obligatoire en production

3. **CORS**: 
   - Configuré uniquement pour `https://www.regenord.com`
   - Vérifier que le backend accepte les requêtes depuis Squarespace

---

**🎉 Prêt pour la production!**
