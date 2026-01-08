# 🧪 Guide de Test Post-Injection

Ce guide vous aide à tester l'intégration QuickBooks après l'injection du code dans Squarespace.

---

## ✅ Pré-requis

Avant de commencer les tests, vérifiez que:

- [ ] Le code est injecté dans Squarespace (Settings > Advanced > Code Injection > Footer)
- [ ] Le backend est déployé et accessible sur `https://api.regenord.com`
- [ ] `DATABASE_URL` est configuré dans `backend/.env`
- [ ] Le Redirect URI est configuré dans Intuit Developer

---

## 🔍 Test 1: Vérification Automatique

Utilisez le script de test pour vérifier rapidement:

```bash
./scripts/test_oauth_connection.sh
```

Ce script vérifie:
- ✅ Accessibilité du backend
- ✅ Configuration QuickBooks
- ✅ Statut de connexion
- ✅ Page Squarespace
- ✅ Redirect URI

---

## 🌐 Test 2: Page Squarespace

### Étape 1: Accéder à la page
1. Ouvrez votre navigateur
2. Allez sur: `https://www.regenord.com/quickbooks-integration`

### Étape 2: Vérifier l'interface
Vous devriez voir:
- ✅ Titre: "🔗 Intégration QuickBooks Online"
- ✅ Description de l'intégration
- ✅ Zone de statut avec "Chargement du statut..."
- ✅ Bouton "🔗 Connecter QuickBooks"
- ✅ Section "ℹ️ À propos de cette intégration"

### Étape 3: Vérifier la console
1. Ouvrez la console du navigateur (F12)
2. Allez dans l'onglet "Console"
3. Vérifiez qu'il n'y a **pas d'erreurs JavaScript**

**Erreurs possibles:**
- ❌ `Cannot read property...` → Code mal injecté
- ❌ `Failed to fetch` → Backend non accessible
- ❌ `CORS error` → Configuration CORS incorrecte

---

## 🔗 Test 3: Connexion OAuth

### Étape 1: Cliquer sur "Connecter QuickBooks"
1. Cliquez sur le bouton **"🔗 Connecter QuickBooks"**
2. Le bouton devrait afficher "⏳ Connexion en cours..."

### Étape 2: Autorisation Intuit
1. Vous devriez être redirigé vers `https://appcenter.intuit.com`
2. Connectez-vous à votre compte Intuit (si nécessaire)
3. Autorisez l'accès à votre compte QuickBooks
4. Sélectionnez votre entreprise QuickBooks (si plusieurs)

### Étape 3: Retour sur la page
1. Après autorisation, vous devriez être redirigé vers:
   `https://www.regenord.com/quickbooks-integration?qbo_connected=true&realm_id=XXXXX`
2. Vous devriez voir un message de succès:
   **"✅ QuickBooks connecté avec succès! Realm ID: XXXXX"**
3. Le statut devrait s'afficher comme **"✅ QuickBooks Connecté"**
4. Le bouton "Connecter" devrait disparaître
5. Le bouton "🚫 Déconnecter QuickBooks" devrait apparaître

---

## 🧪 Test 4: Statut de Connexion

### Vérifier via l'interface
Le statut devrait afficher:
- ✅ **"QuickBooks Connecté"** (en vert)
- ✅ **Realm ID** (identifiant de votre entreprise QuickBooks)
- ✅ **Dernière synchronisation** (si disponible)

### Vérifier via l'API
```bash
curl "https://api.regenord.com/api/qbo/status?company_id=1"
```

Réponse attendue:
```json
{
  "connected": true,
  "realm_id": "1234567890",
  "last_sync": "2024-01-15T10:30:00Z"
}
```

---

## 🚫 Test 5: Déconnexion

### Étape 1: Déconnecter
1. Cliquez sur **"🚫 Déconnecter QuickBooks"**
2. Confirmez la déconnexion dans la boîte de dialogue

### Étape 2: Vérifier
1. La page devrait se recharger
2. Le statut devrait afficher **"⏳ QuickBooks Non Connecté"**
3. Le bouton "Connecter" devrait réapparaître
4. Le bouton "Déconnecter" devrait disparaître

---

## 🐛 Dépannage

### Problème: Page blanche ou erreur 404

**Causes possibles:**
- Code non injecté dans Squarespace
- Code injecté au mauvais endroit (Header au lieu de Footer)
- Erreur de syntaxe dans le code

**Solutions:**
1. Vérifiez que le code est dans **Footer** (pas Header)
2. Vérifiez qu'il n'y a pas d'erreurs dans la console
3. Videz le cache du navigateur (Cmd+Shift+R / Ctrl+Shift+R)
4. Réinjectez le code depuis `SQUARESPACE_CODE_INJECTION_READY.html`

---

### Problème: "Erreur de connexion" ou "Cannot connect to backend"

**Causes possibles:**
- Backend non déployé ou inaccessible
- URL backend incorrecte
- Problème réseau ou firewall

**Solutions:**
1. Vérifiez que `https://api.regenord.com` est accessible:
   ```bash
   curl https://api.regenord.com/api/health
   ```
2. Vérifiez les logs du backend
3. Vérifiez la configuration dans `backend/.env`

---

### Problème: "redirect_uri_mismatch"

**Causes possibles:**
- Redirect URI ne correspond pas entre Intuit Developer et backend

**Solutions:**
1. Dans Intuit Developer, vérifiez que le Redirect URI est exactement:
   `https://www.regenord.com/quickbooks-integration/callback`
   - Pas d'espace
   - Pas de slash final
   - Exactement identique

2. Dans `backend/.env`, vérifiez:
   ```env
   QBO_REDIRECT_URI=https://www.regenord.com/quickbooks-integration/callback
   ```

3. Les deux doivent être **exactement identiques**

---

### Problème: "Database connection failed"

**Causes possibles:**
- `DATABASE_URL` non configuré ou incorrect
- Base de données PostgreSQL inaccessible

**Solutions:**
1. Vérifiez `DATABASE_URL` dans `backend/.env`:
   ```env
   DATABASE_URL=postgresql://user:password@host:5432/database
   ```
2. Testez la connexion à la base de données:
   ```bash
   psql $DATABASE_URL -c "SELECT 1;"
   ```
3. Vérifiez que la base de données est accessible depuis le serveur backend

---

### Problème: Le statut ne se charge pas

**Causes possibles:**
- Backend non accessible
- Erreur dans l'API `/api/qbo/status`
- Problème CORS

**Solutions:**
1. Vérifiez la console du navigateur pour les erreurs
2. Testez l'API manuellement:
   ```bash
   curl "https://api.regenord.com/api/qbo/status?company_id=1"
   ```
3. Vérifiez la configuration CORS dans le backend

---

## ✅ Checklist de Test Complète

- [ ] Page Squarespace accessible et interface visible
- [ ] Pas d'erreurs dans la console du navigateur
- [ ] Statut se charge automatiquement
- [ ] Bouton "Connecter QuickBooks" fonctionne
- [ ] Redirection vers Intuit OAuth réussie
- [ ] Autorisation Intuit réussie
- [ ] Retour sur la page avec message de succès
- [ ] Statut affiche "QuickBooks Connecté"
- [ ] Realm ID affiché correctement
- [ ] Bouton "Déconnecter" apparaît après connexion
- [ ] Déconnexion fonctionne correctement
- [ ] Après déconnexion, statut affiche "Non Connecté"

---

## 📊 Logs à Surveiller

### Backend Logs
Surveillez les logs du backend pour:
- ✅ Requêtes OAuth réussies
- ✅ Tokens encryptés et sauvegardés
- ✅ Callbacks OAuth traités
- ❌ Erreurs de connexion base de données
- ❌ Erreurs de token exchange

### Console Navigateur
Surveillez la console pour:
- ✅ Requêtes vers `https://api.regenord.com` réussies
- ❌ Erreurs CORS
- ❌ Erreurs 404 ou 500
- ❌ Erreurs JavaScript

---

## 🎉 Test Réussi!

Si tous les tests passent:
1. ✅ L'intégration est fonctionnelle
2. ✅ Vous pouvez commencer à synchroniser les données QuickBooks
3. ✅ L'application peut générer des projections basées sur les données réelles

---

**Questions?** Consultez `GUIDE_INJECTION_SQUARESPACE.md` ou `INDEX_DOCUMENTATION.md`
