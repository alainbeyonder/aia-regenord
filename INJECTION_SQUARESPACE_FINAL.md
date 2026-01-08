# 📝 Guide Final - Injection Code Squarespace

## ✅ Statut Actuel

- ✅ **Intuit Developer:** Configuration complétée
- ✅ **Page Squarespace:** Créée et publiée à `https://www.regenord.com/quickbooks-integration`
- ✅ **Credentials Production:** Configurés
- ⏳ **Code d'injection:** À injecter dans Squarespace

---

## 🎯 Étapes Finales

### Étape 1: Préparer le Code (UNE SEULE MODIFICATION)

1. Ouvrir le fichier: `SQUARESPACE_CODE_INJECTION_FINAL.html`

2. Trouver la ligne 13 (dans la section CONFIGURATION):
   ```javascript
   const BACKEND_URL = 'YOUR_BACKEND_URL'; // ⚠️ À REMPLACER
   ```

3. Remplacer `YOUR_BACKEND_URL` par l'URL de votre backend en production.
   
   **Exemple:**
   ```javascript
   const BACKEND_URL = 'https://api.regenord.com'; // URL de votre backend
   ```

4. **IMPORTANT:** Vérifier que l'URL:
   - Commence par `https://` (pas `http://`)
   - Ne se termine PAS par un slash `/`
   - Est accessible publiquement
   - Supporte CORS pour `https://www.regenord.com`

### Étape 2: Copier le Code Complet

1. Sélectionner **TOUT** le contenu du fichier (Cmd+A ou Ctrl+A)
2. Copier (Cmd+C ou Ctrl+C)

### Étape 3: Injecter dans Squarespace

1. Se connecter à votre compte Squarespace
2. Aller dans **Settings** (Paramètres)
3. Cliquer sur **Advanced** (Avancé)
4. Cliquer sur **Code Injection** (Injection de code)
5. Dans la section **Footer**, coller le code copié
6. **Sauvegarder** (bouton en haut à droite)

⚠️ **IMPORTANT:** 
- Le code doit être dans **Footer**, pas dans Header
- Ne pas modifier le code après l'avoir collé (sauf si vous savez ce que vous faites)
- Le code fonctionnera sur toutes les pages, mais n'affichera l'interface que sur `/quickbooks-integration`

### Étape 4: Vérifier l'Injection

1. Aller sur `https://www.regenord.com/quickbooks-integration`
2. Vérifier que vous voyez:
   - Le titre "🔗 Intégration QuickBooks Online"
   - Un message de statut (connecté/non connecté)
   - Le bouton "Connecter QuickBooks" ou "Déconnecter QuickBooks"

Si l'interface n'apparaît pas:
- Vérifier que le code est bien dans **Footer**
- Vider le cache du navigateur (Cmd+Shift+R ou Ctrl+Shift+R)
- Vérifier la console du navigateur (F12) pour les erreurs

---

## 🔍 Vérification Technique

### Test 1: Backend Accessible

Avant d'injecter le code, vérifiez que votre backend répond:

```bash
curl https://YOUR_BACKEND_URL/api/qbo/config/check
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

### Test 2: CORS Configuré

Vérifiez que le backend accepte les requêtes depuis `www.regenord.com`:

```bash
curl -H "Origin: https://www.regenord.com" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     https://YOUR_BACKEND_URL/api/qbo/status
```

Vous devriez voir des en-têtes `Access-Control-Allow-Origin` dans la réponse.

---

## 🧪 Tests Après Injection

### Test de Connexion OAuth

1. Aller sur `https://www.regenord.com/quickbooks-integration`
2. Cliquer sur **"Connecter QuickBooks"**
3. Vous devriez être redirigé vers Intuit OAuth
4. Autoriser l'application
5. Vous devriez être redirigé vers `https://www.regenord.com/quickbooks-integration?qbo_connected=true&realm_id=...`
6. Le statut devrait afficher **"✅ QuickBooks Connecté"**

### Test de Déconnexion

1. Si connecté, cliquer sur **"Déconnecter QuickBooks"**
2. Confirmer
3. Le statut devrait changer à **"Non connecté"**

---

## 🐛 Dépannage

### L'interface n'apparaît pas

**Cause:** Code mal injecté ou erreur JavaScript

**Solution:**
1. Ouvrir la console du navigateur (F12)
2. Vérifier les erreurs
3. Vérifier que `BACKEND_URL` est correct
4. Vérifier que le code est dans **Footer** et non **Header**

### Erreur "Failed to fetch" ou CORS

**Cause:** Le backend n'accepte pas les requêtes depuis Squarespace

**Solution:**
1. Vérifier que `CORS_ORIGINS` dans `backend/.env` inclut `https://www.regenord.com`
2. Redémarrer le backend
3. Vérifier que `BACKEND_URL` dans le code est correct

### Redirection OAuth échoue

**Cause:** Redirect URI incorrect dans Intuit Developer

**Solution:**
1. Vérifier dans Intuit Developer que la Redirect URI est exactement:
   ```
   https://www.regenord.com/quickbooks-integration/callback
   ```
2. Pas de slash à la fin
3. HTTPS obligatoire

### "Backend not accessible"

**Cause:** URL du backend incorrecte ou backend non déployé

**Solution:**
1. Vérifier que `BACKEND_URL` est correct dans le code
2. Tester avec `curl` (voir section Vérification Technique)
3. Vérifier que le backend est déployé et en cours d'exécution

---

## 📋 Checklist Finale

Avant de considérer l'intégration complète:

- [ ] Code injecté dans Squarespace (Settings > Advanced > Code Injection > Footer)
- [ ] `YOUR_BACKEND_URL` remplacé par l'URL réelle du backend
- [ ] Backend accessible et répond à `/api/qbo/config/check`
- [ ] CORS configuré pour `https://www.regenord.com`
- [ ] Page Squarespace accessible: `https://www.regenord.com/quickbooks-integration`
- [ ] Interface QuickBooks s'affiche correctement
- [ ] Test de connexion OAuth réussi
- [ ] Test de déconnexion réussi
- [ ] Statut de connexion se met à jour correctement

---

## 🎉 Félicitations!

Une fois tous les tests passés, votre intégration QuickBooks Online est **COMPLÈTE** et prête pour la production!

---

**Besoin d'aide?** Consultez:
- `RECAPITULATIF_FINAL_PRODUCTION.md` - Récapitulatif complet
- `DEPLOIEMENT_PRODUCTION.md` - Guide de déploiement détaillé
- `CONFIGURATION_RAPIDE.md` - Configuration rapide avec scripts
