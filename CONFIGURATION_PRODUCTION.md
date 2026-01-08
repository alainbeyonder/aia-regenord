# 🔐 Configuration Production - QuickBooks Online

## ✅ Credentials Production Configurés

**Client ID:** `ABhjTWUsPqScOqpWeCghMKHpx85MbL0fM9JQnt4uXpD4Wynk`  
**Client Secret:** `d2R1L2EFjbZyNmJdcYnnbibh6AVsIVlZDFF9dc8V`  
**Environment:** Production

**URLs:**
- Page Squarespace: `https://www.regenord.com/quickbooks-integration`
- Callback: `https://www.regenord.com/quickbooks-integration/callback`

---

## 📝 Configuration Backend (.env)

Créer/modifier `backend/.env` avec ces valeurs:

```env
# ============================================
# QuickBooks Online - PRODUCTION
# ============================================
QBO_ENVIRONMENT=production
QBO_CLIENT_ID=ABhjTWUsPqScOqpWeCghMKHpx85MbL0fM9JQnt4uXpD4Wynk
QBO_CLIENT_SECRET=d2R1L2EFjbZyNmJdcYnnbibh6AVsIVlZDFF9dc8V
QBO_REDIRECT_URI=https://www.regenord.com/quickbooks-integration/callback

# ============================================
# Application
# ============================================
APP_NAME=AIA Regenord
APP_ENV=production
DEBUG=False
APP_BASE_URL=https://YOUR_BACKEND_URL  # ⚠️ À REMPLACER: URL de votre backend
FRONTEND_URL=https://www.regenord.com

# ============================================
# Sécurité (GÉNÉRER CES CLÉS!)
# ============================================
# Clé Fernet pour l'encryption des tokens QBO
# Générer avec: python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
AIA_TOKEN_ENCRYPTION_KEY=YOUR_FERNET_KEY_HERE

# Clé secrète pour l'application
# Générer avec: python3 -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=YOUR_SECRET_KEY_HERE

# ============================================
# Base de données
# ============================================
DATABASE_URL=postgresql://user:password@host:5432/aia_regenord

# ============================================
# CORS
# ============================================
CORS_ORIGINS=["https://www.regenord.com"]

# ============================================
# Logging
# ============================================
LOG_LEVEL=INFO
LOG_FILE=./logs/aia-regenord.log
```

---

## 🔑 Génération des Clés de Sécurité

### 1. Clé Fernet (pour encryption des tokens)

```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copier le résultat dans `AIA_TOKEN_ENCRYPTION_KEY`

### 2. Clé Secrète (pour l'application)

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copier le résultat dans `SECRET_KEY`

---

## 📋 Configuration Intuit Developer

Dans [Intuit Developer Portal](https://developer.intuit.com/):

1. **Application en mode Production** (pas Sandbox)
2. **Redirect URIs**:
   ```
   https://www.regenord.com/quickbooks-integration/callback
   ```
3. **Scopes**:
   - `com.intuit.quickbooks.accounting`
   - `openid`
   - `profile`
   - `email`

---

## 📝 Code Squarespace

1. Ouvrir `SQUARESPACE_CODE_INJECTION_FINAL.html`
2. Remplacer `YOUR_BACKEND_URL` par l'URL réelle de votre backend
3. Copier tout le contenu
4. Dans Squarespace: **Settings > Advanced > Code Injection > Footer**
5. Coller le code
6. Sauvegarder

---

## ✅ Checklist Finale

- [ ] Backend `.env` configuré avec credentials production
- [ ] Clés de sécurité générées (Fernet + Secret)
- [ ] `APP_BASE_URL` configuré dans `.env`
- [ ] Intuit Developer: Application en Production
- [ ] Intuit Developer: Redirect URI configurée
- [ ] Code Squarespace injecté avec `BACKEND_URL` correct
- [ ] CORS configuré pour `https://www.regenord.com`
- [ ] Test de connexion effectué

---

**🚀 Prêt pour la production!**
