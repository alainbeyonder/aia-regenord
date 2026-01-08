# Guide de Reconnexion QuickBooks Online

## 🎯 Contexte

Vous voyez le message "Aucune catégorie de revenus détectée" dans le questionnaire des hypothèses de projection.

**Cause:** Le token d'authentification QuickBooks a expiré (erreur 403: ApplicationAuthorizationFailed).

**Solution:** Reconnecter QuickBooks pour obtenir un nouveau token et synchroniser les données.

---

## 📋 Étapes de Reconnexion

### Étape 1: Fermer le questionnaire

1. Dans le modal du questionnaire, cliquez sur le bouton **"← Retour au tableau de bord"**
2. Vous revenez au tableau de bord principal

### Étape 2: Localiser la carte QuickBooks

Sur le tableau de bord, repérez la carte **"📊 QuickBooks Online"**

Elle affiche actuellement :
- État: "Connecté" (mais le token est expiré)
- Realm ID: 9341456045827624
- Dernière erreur: ApplicationAuthorizationFailed

### Étape 3: Reconnecter QuickBooks

1. Cliquez sur le bouton **"Connecter QBO"** dans cette carte
2. Une nouvelle fenêtre/onglet s'ouvre vers Intuit Developer Sandbox
3. **Connectez-vous** avec vos identifiants Intuit Developer :
   - Email: votre email Intuit Developer
   - Mot de passe: votre mot de passe

### Étape 4: Autoriser l'accès

1. Sélectionnez votre **entreprise sandbox** : "Regennord Accounting Integration"
2. Cliquez sur **"Autoriser"** ou **"Connect"**
3. Vous serez redirigé vers votre application (http://localhost:3000)
4. Un message de succès s'affiche : "✅ QuickBooks connecté avec succès!"

### Étape 5: Attendre la synchronisation automatique

Le backend effectue automatiquement les actions suivantes :

**Données synchronisées :**
- ✅ Liste complète des comptes QBO
- ✅ Transactions des 12 derniers mois
- ✅ Rapport Profit & Loss (P&L)
- ✅ Mapping des comptes vers les catégories AIA

**Durée estimée :** 10-30 secondes

**Indicateurs de progression :**
- La carte "QuickBooks Online" affiche "Connecté" en vert
- Pas de message d'erreur visible

### Étape 6: Vérifier les données (optionnel)

Pour confirmer que les données sont bien synchronisées :

1. Cliquez sur **"📋 Voir Vue QBO"** dans la carte "Projections Financières"
2. Vous devriez voir :
   - Nombre de comptes (ex: 89 comptes)
   - Nombre de transactions (ex: 12 transactions)
   - Statistiques détaillées
   - Analyse d'anomalies

3. Ou cliquez sur **"📊 Voir Vue AIA"** pour voir :
   - Les catégories de revenus (licences, services, produits, etc.)
   - Les totaux par catégorie
   - Les graphiques de tendances

### Étape 7: Relancer le questionnaire

1. Fermez les modals de vérification (si ouverts)
2. Cliquez à nouveau sur **"🚀 Simuler Projections"**
3. Le questionnaire s'ouvre avec l'**Étape 1 : Contexte Général**
4. Choisissez la finalité (ex: Discussion bancaire)
5. Cliquez sur **"Suivant →"**
6. À l'**Étape 2**, vous verrez maintenant :
   - ✅ Toutes vos catégories de revenus détectées
   - 📊 Historique de chaque catégorie
   - 💰 Montants calculés
   - 📈 Suggestions de croissance (conservateur, réaliste, ambitieux)

---

## ⚠️ Dépannage

### Problème: Le bouton "Connecter QBO" ne fait rien

**Solution :**
1. Vérifiez que le backend est en cours d'exécution :
   ```bash
   curl http://localhost:8000/health
   ```
2. Si le backend ne répond pas, redémarrez-le :
   ```bash
   docker-compose restart backend
   ```

### Problème: Après la reconnexion, toujours "Aucune catégorie détectée"

**Solutions possibles :**

1. **Vérifier la synchronisation :**
   - Cliquez sur "Voir Vue QBO"
   - Si vous voyez "0 comptes", la synchronisation a échoué

2. **Forcer une nouvelle synchronisation :**
   - Ouvrez la console du backend :
     ```bash
     docker-compose logs -f backend
     ```
   - Vérifiez les messages d'erreur
   - Si erreur 403 persiste, reconnectez à nouveau

3. **Vérifier les credentials :**
   - Ouvrez `backend/.env`
   - Vérifiez que `QBO_CLIENT_ID` et `QBO_CLIENT_SECRET` sont corrects
   - Vérifiez que `QBO_ENVIRONMENT=sandbox`

4. **Vider le cache et reconnecter :**
   - Dans le navigateur, ouvrez les DevTools (F12)
   - Console → Tapez : `localStorage.clear()`
   - Rafraîchissez la page
   - Reconnectez QuickBooks

### Problème: "Token expiré" à nouveau après quelques heures

**Explication :**
Les tokens OAuth2 d'Intuit expirent après **1 heure**. Le backend utilise un **refresh token** (valide 100 jours) pour obtenir automatiquement un nouveau token.

**Si le problème persiste :**
- Le refresh token a peut-être également expiré
- Reconnectez QuickBooks (procédure ci-dessus)
- Le backend obtiendra de nouveaux tokens (access + refresh)

### Problème: Sandbox vs Production

**Important :** Vous êtes actuellement en mode **Sandbox** (données de test).

Pour passer en **Production** (données réelles) :

1. Obtenir des credentials de production sur Intuit Developer
2. Mettre à jour `backend/.env` :
   ```env
   QBO_ENVIRONMENT=production
   QBO_CLIENT_ID=<votre_client_id_production>
   QBO_CLIENT_SECRET=<votre_client_secret_production>
   ```
3. Redémarrer le backend
4. Reconnecter avec votre entreprise réelle

---

## 🎉 Succès !

Une fois la reconnexion réussie, vous devriez :

✅ Voir les catégories de revenus dans le questionnaire  
✅ Avoir des valeurs par défaut intelligentes calculées  
✅ Pouvoir compléter toutes les étapes du questionnaire  
✅ Générer des projections financières sur 3 ans  

---

## 📞 Besoin d'aide ?

Si vous rencontrez toujours des problèmes après avoir suivi ce guide :

1. Vérifiez les logs du backend :
   ```bash
   docker-compose logs backend | grep -i error
   ```

2. Vérifiez les logs du frontend (Console du navigateur, F12)

3. Consultez le `GUIDE_DEPLOIEMENT_QBO.md` pour plus de détails sur la configuration

4. Testez l'API directement :
   ```bash
   curl "http://localhost:8000/api/qbo/status?company_id=1"
   curl "http://localhost:8000/api/aia/view?company_id=1&months=12"
   ```

---

**Date de création :** 2026-01-07  
**Version :** 1.0  
**Projet :** AIA Regenord - Agent IA Financier
