# 🚀 Guide de Déploiement - Étape par Étape

Guide complet pour déployer l'intégration QuickBooks Online en production.

---

## 📋 Vue d'ensemble

Ce guide vous accompagne à travers toutes les étapes nécessaires pour mettre en production l'intégration QuickBooks Online sur votre site Squarespace.

**Temps estimé:** 30-45 minutes  
**Difficulté:** ⭐⭐ Moyenne

---

## ✅ Pré-requis

Avant de commencer, assurez-vous d'avoir:

- [ ] Accès à votre compte Intuit Developer
- [ ] Credentials de production QuickBooks (Client ID et Secret)
- [ ] Accès administrateur à votre site Squarespace
- [ ] Credentials PostgreSQL pour la base de données
- [ ] Accès au serveur où le backend sera déployé

---

## 📝 Étape 1: Configuration Backend

### 1.1 Vérifier les fichiers de configuration

```bash
# Vérifier que backend/.env existe
ls -la backend/.env

# Vérifier la configuration
./scripts/verify_production_setup.sh
```

### 1.2 Configurer DATABASE_URL

**Action requise:** Ouvrir `backend/.env` et modifier:

```env
DATABASE_URL=postgresql://votre_user:votre_password@votre_host:5432/votre_database
```

**Exemple:**
```env
DATABASE_URL=postgresql://aia_user:SecurePass123@db.regenord.com:5432/aia_production
```

⚠️ **Important:** Remplacez `votre_user`, `votre_password`, `votre_host`, et `votre_database` par vos valeurs réelles.

### 1.3 Vérifier les autres variables

Assurez-vous que ces variables sont correctes dans `backend/.env`:

```env
# QuickBooks
QBO_ENVIRONMENT=production
QBO_CLIENT_ID=ABhjTWUsPqScOqpWeCghMKHpx85MbL0fM9JQnt4uXpD4Wynk
QBO_CLIENT_SECRET=d2R1L2EFjbZyNmJdcYnnbibh6AVsIVlZDFF9dc8V
QBO_REDIRECT_URI=https://www.regenord.com/quickbooks-integration/callback

# Application
APP_BASE_URL=https://api.regenord.com
FRONTEND_URL=https://www.regenord.com

# Sécurité (déjà générées)
AIA_TOKEN_ENCRYPTION_KEY=Jc8GWiI1zrJ9a-aWYgETa42PLx3FRUjbkJzQ_SEIg3c=
SECRET_KEY=o8x80d_-Uu_uPbE0vASawCqen_BrSr8hVtkelay_cpU
```

### 1.4 Vérifier la configuration

```bash
./scripts/verify_production_setup.sh
```

Tous les tests doivent passer (sauf DATABASE_URL si pas encore configuré).

---

## 🏗️ Étape 2: Déploiement Backend

### 2.1 Préparer le serveur

Assurez-vous que:
- Python 3.9+ est installé
- PostgreSQL est installé et accessible
- Les variables d'environnement sont chargées

### 2.2 Déployer le backend

**Méthode dépend de votre infrastructure:**
- Docker: Utiliser Dockerfile
- Serverless: Configurer selon votre plateforme (AWS Lambda, etc.)
- Serveur traditionnel: Suivre les instructions de déploiement

### 2.3 Vérifier le déploiement

```bash
# Tester la santé du backend
curl https://api.regenord.com/api/health

# Tester la configuration QBO
curl https://api.regenord.com/api/qbo/config/check
```

**Réponse attendue:**
```json
{
  "status": "ok",
  "service": "api"
}
```

---

## 🔧 Étape 3: Configuration Intuit Developer

### 3.1 Se connecter à Intuit Developer

1. Aller sur: https://developer.intuit.com
2. Se connecter avec votre compte
3. Sélectionner votre application

### 3.2 Configurer le Redirect URI

1. Aller dans **Settings** ou **Keys**
2. Trouver la section **Redirect URIs**
3. Ajouter exactement (copier-coller):
   ```
   https://www.regenord.com/quickbooks-integration/callback
   ```

⚠️ **Important:** 
- L'URL doit être **exactement** identique (pas d'espace, pas de slash final)
- Vérifiez que vous êtes en mode **Production** (pas Sandbox)

### 3.3 Vérifier les credentials

Assurez-vous que:
- Client ID: `ABhjTWUsPqScOqpWeCghMKHpx85MbL0fM9JQnt4uXpD4Wynk`
- Client Secret correspond à celui dans `backend/.env`
- Application est en mode **Production**

---

## 📄 Étape 4: Injection Code Squarespace

### 4.1 Préparer le code

**Option A: Script automatique (macOS/Linux)**
```bash
./scripts/prepare_code_for_squarespace.sh
# Suivre les instructions à l'écran
```

**Option B: Manuellement**
1. Ouvrir le fichier: `SQUARESPACE_CODE_INJECTION_READY.html`
2. Sélectionner tout (Cmd+A / Ctrl+A)
3. Copier (Cmd+C / Ctrl+C)

### 4.2 Injecter dans Squarespace

1. **Se connecter à Squarespace**
   - Aller sur: https://www.squarespace.com
   - Se connecter avec votre compte

2. **Accéder aux paramètres**
   - Cliquer sur votre site
   - Aller dans **Settings** (Paramètres)
   - Dans le menu latéral, cliquer sur **Advanced** (Avancé)
   - Cliquer sur **Code Injection** (Injection de code)

3. **Injecter le code**
   - Dans la section **Footer** (Pied de page)
   - Coller le code copié (Cmd+V / Ctrl+V)
   - **Important:** Ne pas modifier le code
   - Cliquer sur **Save** (Enregistrer)

4. **Publier les changements**
   - Si nécessaire, publier le site
   - Les changements devraient être immédiats

### 4.3 Vérifier l'injection

1. Aller sur: `https://www.regenord.com/quickbooks-integration`
2. Vous devriez voir:
   - Titre: "🔗 Intégration QuickBooks Online"
   - Bouton "Connecter QuickBooks"
   - Section avec informations

3. Ouvrir la console du navigateur (F12)
4. Vérifier qu'il n'y a **pas d'erreurs JavaScript**

---

## 🧪 Étape 5: Tests

### 5.1 Test automatique

```bash
# Tester la configuration complète
./scripts/test_oauth_connection.sh
```

### 5.2 Test manuel de connexion

1. **Aller sur la page**
   - URL: `https://www.regenord.com/quickbooks-integration`

2. **Vérifier le statut**
   - Le statut devrait se charger automatiquement
   - Affiche "⏳ QuickBooks Non Connecté" (normal)

3. **Tester la connexion**
   - Cliquer sur **"🔗 Connecter QuickBooks"**
   - Le bouton devrait afficher "⏳ Connexion en cours..."
   - Redirection vers Intuit OAuth

4. **Autoriser l'accès**
   - Se connecter à Intuit (si nécessaire)
   - Autoriser l'accès à QuickBooks
   - Sélectionner votre entreprise QuickBooks

5. **Vérifier le retour**
   - Retour automatique sur la page
   - Message de succès: "✅ QuickBooks connecté avec succès!"
   - Statut mis à jour: "✅ QuickBooks Connecté"
   - Realm ID affiché

6. **Vérifier la déconnexion**
   - Cliquer sur **"🚫 Déconnecter QuickBooks"**
   - Confirmer la déconnexion
   - Statut revient à "⏳ QuickBooks Non Connecté"

### 5.3 Vérifier via l'API

```bash
# Vérifier le statut de connexion
curl "https://api.regenord.com/api/qbo/status?company_id=1"
```

**Réponse attendue après connexion:**
```json
{
  "connected": true,
  "realm_id": "1234567890",
  "last_sync": "2024-01-15T10:30:00Z"
}
```

---

## 🔍 Étape 6: Vérifications Finales

### Checklist complète

- [ ] Backend déployé et accessible
- [ ] Base de données connectée et fonctionnelle
- [ ] Configuration Intuit Developer correcte
- [ ] Redirect URI configuré dans Intuit
- [ ] Code injecté dans Squarespace
- [ ] Page accessible: `https://www.regenord.com/quickbooks-integration`
- [ ] Interface s'affiche correctement
- [ ] Connexion OAuth fonctionne
- [ ] Déconnexion fonctionne
- [ ] Tokens stockés et encryptés (vérifier logs backend)
- [ ] Pas d'erreurs dans la console du navigateur
- [ ] Pas d'erreurs dans les logs backend

---

## 🐛 Dépannage

### Problème: Backend non accessible

**Symptômes:**
- Erreur "Cannot connect to backend"
- Erreur 404 ou 500

**Solutions:**
1. Vérifier que le backend est déployé
2. Vérifier l'URL: `https://api.regenord.com`
3. Vérifier les logs du backend
4. Vérifier les règles de firewall

### Problème: redirect_uri_mismatch

**Symptômes:**
- Erreur lors de l'autorisation Intuit
- Message "redirect_uri_mismatch"

**Solutions:**
1. Vérifier dans Intuit Developer que le Redirect URI est:
   `https://www.regenord.com/quickbooks-integration/callback`
2. Vérifier dans `backend/.env`:
   `QBO_REDIRECT_URI=https://www.regenord.com/quickbooks-integration/callback`
3. Les deux doivent être **exactement identiques**
4. Pas d'espace, pas de slash final

### Problème: Page Squarespace blanche

**Symptômes:**
- Page vide ou erreur 404
- Code non visible

**Solutions:**
1. Vérifier que le code est dans **Footer** (pas Header)
2. Vérifier qu'il n'y a pas d'erreurs de syntaxe
3. Vider le cache du navigateur
4. Vérifier la console du navigateur (F12)
5. Réinjecter le code

### Problème: Base de données

**Symptômes:**
- Erreur "Database connection failed"
- Erreurs dans les logs backend

**Solutions:**
1. Vérifier `DATABASE_URL` dans `backend/.env`
2. Tester la connexion: `psql $DATABASE_URL`
3. Vérifier que PostgreSQL est accessible depuis le backend
4. Vérifier les credentials (user, password, host, database)

---

## 📞 Support

### Ressources

- **Documentation complète:** `INDEX_DOCUMENTATION.md`
- **Guide d'injection rapide:** `INJECTION_RAPIDE.md`
- **Guide de test:** `GUIDE_TEST_POST_INJECTION.md`
- **Checklist:** `CHECKLIST_FINALE.md`

### Commandes utiles

```bash
# Vérifier la configuration
./scripts/verify_production_setup.sh

# Tester la connexion
./scripts/test_oauth_connection.sh

# Préparer le code pour Squarespace
./scripts/prepare_code_for_squarespace.sh

# Vérifier le backend
curl https://api.regenord.com/api/health
```

---

## ✅ Déploiement Réussi!

Une fois toutes les étapes terminées et tous les tests passés:

🎉 **L'intégration QuickBooks Online est opérationnelle en production!**

Vous pouvez maintenant:
- Connecter des comptes QuickBooks
- Synchroniser des données financières
- Générer des projections basées sur les données réelles

---

**Date de création:** $(date)  
**Version:** Production 1.0
