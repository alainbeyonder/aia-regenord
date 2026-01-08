# 🚀 Guide d'Injection Squarespace - QuickBooks Integration

## ✅ Étape 1: Accéder aux Paramètres Squarespace

1. Connectez-vous à votre compte Squarespace
2. Naviguez vers: **Settings** → **Advanced** → **Code Injection**

## ✅ Étape 2: Injecter le Code

1. Dans la section **Footer**, collez le contenu du fichier `SQUARESPACE_CODE_INJECTION_READY.html`
2. Cliquez sur **Save** pour enregistrer

## ✅ Étape 3: Vérifier la Page

1. Allez sur: `https://www.regenord.com/quickbooks-integration`
2. Vous devriez voir l'interface d'intégration QuickBooks
3. Cliquez sur **"Connecter QuickBooks"** pour tester

---

## 📋 Contenu à Injecter

Le fichier `SQUARESPACE_CODE_INJECTION_READY.html` contient tout le code nécessaire. 
**N'injectez QUE le code JavaScript**, sans les commentaires HTML d'en-tête si Squarespace les refuse.

### Code à Injecter (dans Footer):

```html
<script>
(function() {
  const BACKEND_URL = 'https://api.regenord.com';
  const COMPANY_ID = 1;
  
  // ... (reste du code du fichier SQUARESPACE_CODE_INJECTION_READY.html)
})();
</script>
```

---

## 🔍 Vérifications Post-Injection

### ✅ Test 1: Vérifier que le code est chargé
- Ouvrez la console du navigateur (F12)
- Allez sur `https://www.regenord.com/quickbooks-integration`
- Vérifiez qu'il n'y a pas d'erreurs JavaScript

### ✅ Test 2: Vérifier la connexion au backend
- Cliquez sur "Connecter QuickBooks"
- Vous devriez être redirigé vers la page d'autorisation Intuit
- Après autorisation, vous serez redirigé vers la page avec un message de succès

### ✅ Test 3: Vérifier le statut de connexion
- La page devrait afficher automatiquement le statut (Connecté / Non connecté)
- Si connecté, le bouton "Déconnecter" devrait apparaître

---

## 🐛 Dépannage

### Problème: Le code ne s'affiche pas
**Solution**: 
- Vérifiez que le code est bien injecté dans le Footer (pas dans Header)
- Vérifiez qu'il n'y a pas de conflits avec d'autres scripts Squarespace
- Videz le cache du navigateur

### Problème: Erreur de connexion au backend
**Solution**:
- Vérifiez que `https://api.regenord.com` est accessible
- Vérifiez que le backend est déployé et en cours d'exécution
- Vérifiez les logs du backend pour les erreurs

### Problème: Erreur OAuth (redirect_uri_mismatch)
**Solution**:
- Vérifiez que le Redirect URI dans Intuit Developer est exactement: 
  `https://www.regenord.com/quickbooks-integration/callback`
- Vérifiez que `backend/.env` contient: 
  `QBO_REDIRECT_URI=https://www.regenord.com/quickbooks-integration/callback`

---

## 📞 Support

Si vous rencontrez des problèmes:
1. Vérifiez les logs du backend
2. Vérifiez la console du navigateur
3. Vérifiez que tous les fichiers de configuration sont corrects

---

## ✅ Checklist Finale

- [ ] Code injecté dans Squarespace (Settings > Advanced > Code Injection > Footer)
- [ ] Page accessible: `https://www.regenord.com/quickbooks-integration`
- [ ] Backend accessible: `https://api.regenord.com`
- [ ] Test de connexion OAuth réussi
- [ ] Statut de connexion s'affiche correctement
- [ ] Déconnexion fonctionne

---

**Date de création**: $(date)
**Version**: Production 1.0
**Backend URL**: https://api.regenord.com
