# 🚀 Injection Rapide - Squarespace QuickBooks Integration

## ⚡ Étapes Rapides (2 minutes)

### 1️⃣ Ouvrir le code à injecter
Ouvrir le fichier: **`SQUARESPACE_CODE_INJECTION_READY.html`**

### 2️⃣ Sélectionner tout le contenu
- **Mac:** `Cmd + A`
- **Windows/Linux:** `Ctrl + A`

### 3️⃣ Copier
- **Mac:** `Cmd + C`
- **Windows/Linux:** `Ctrl + C`

### 4️⃣ Dans Squarespace
1. Aller à: **Settings** → **Advanced** → **Code Injection**
2. Dans la section **Footer**, coller le code (`Cmd+V` / `Ctrl+V`)
3. Cliquer sur **Save**

### 5️⃣ Vérifier
1. Aller sur: `https://www.regenord.com/quickbooks-integration`
2. Vous devriez voir l'interface d'intégration
3. Cliquer sur **"Connecter QuickBooks"** pour tester

---

## ✅ Checklist Pré-Injection

Avant d'injecter, vérifier:

- [ ] Backend déployé et accessible: `https://api.regenord.com`
- [ ] `backend/.env` configuré avec:
  - [ ] `QBO_CLIENT_ID` = `ABhjTWUsPqScOqpWeCghMKHpx85MbL0fM9JQnt4uXpD4Wynk`
  - [ ] `QBO_CLIENT_SECRET` configuré
  - [ ] `QBO_REDIRECT_URI` = `https://www.regenord.com/quickbooks-integration/callback`
  - [ ] `DATABASE_URL` configuré avec vos credentials PostgreSQL
- [ ] Intuit Developer configuré:
  - [ ] Redirect URI ajouté: `https://www.regenord.com/quickbooks-integration/callback`
  - [ ] App en mode Production

---

## 🔍 Vérification Post-Injection

### Test 1: Page accessible
✅ La page `https://www.regenord.com/quickbooks-integration` s'affiche

### Test 2: Interface visible
✅ L'interface avec le bouton "Connecter QuickBooks" est visible

### Test 3: Statut de connexion
✅ Le statut (Connecté / Non connecté) s'affiche automatiquement

### Test 4: Connexion OAuth
1. Cliquer sur **"Connecter QuickBooks"**
2. ✅ Redirection vers Intuit pour autorisation
3. ✅ Autoriser l'accès
4. ✅ Retour sur la page avec message de succès

---

## 🐛 Problèmes Courants

### ❌ "Erreur 404" ou page blanche
**Cause:** Code non injecté ou injecté au mauvais endroit

**Solution:**
- Vérifier que le code est dans **Footer** (pas Header)
- Vérifier qu'il n'y a pas d'erreurs de syntaxe
- Vider le cache du navigateur

### ❌ "Cannot connect to backend"
**Cause:** Backend non accessible ou URL incorrecte

**Solution:**
- Vérifier que `https://api.regenord.com` est accessible
- Vérifier les logs du backend
- Vérifier que le backend est déployé

### ❌ "redirect_uri_mismatch"
**Cause:** Redirect URI ne correspond pas entre Intuit et backend

**Solution:**
- Vérifier dans Intuit Developer: `https://www.regenord.com/quickbooks-integration/callback`
- Vérifier dans `backend/.env`: `QBO_REDIRECT_URI=https://www.regenord.com/quickbooks-integration/callback`
- Les URLs doivent être **exactement identiques** (pas d'espace, pas de slash final)

---

## 📞 Support

En cas de problème:
1. Vérifier la console du navigateur (F12)
2. Vérifier les logs du backend
3. Exécuter: `./scripts/verify_production_setup.sh`

---

**Durée estimée:** 2-3 minutes  
**Difficulté:** ⭐ Facile
