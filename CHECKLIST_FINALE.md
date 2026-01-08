# ✅ Checklist Finale - Déploiement Production

## 🔐 Configuration Backend

### Variables d'environnement (`backend/.env`)
- [x] `QBO_ENVIRONMENT=production`
- [x] `QBO_CLIENT_ID=ABhjTWUsPqScOqpWeCghMKHpx85MbL0fM9JQnt4uXpD4Wynk`
- [x] `QBO_CLIENT_SECRET` configuré
- [x] `QBO_REDIRECT_URI=https://www.regenord.com/quickbooks-integration/callback`
- [x] `APP_BASE_URL=https://api.regenord.com`
- [x] `FRONTEND_URL=https://www.regenord.com`
- [x] `AIA_TOKEN_ENCRYPTION_KEY` générée
- [x] `SECRET_KEY` générée
- [ ] `DATABASE_URL` configuré avec credentials PostgreSQL ← **À FAIRE**

---

## 🏗️ Déploiement Backend

- [ ] Backend déployé sur `https://api.regenord.com`
- [ ] Backend accessible (test: `curl https://api.regenord.com/api/health`)
- [ ] Base de données PostgreSQL accessible depuis le backend
- [ ] Variables d'environnement chargées correctement
- [ ] Logs du backend fonctionnels

---

## 🔧 Configuration Intuit Developer

### Redirect URIs
- [ ] Redirect URI ajouté: `https://www.regenord.com/quickbooks-integration/callback`
- [ ] **URL exacte** (pas d'espace, pas de slash final)
- [ ] Environnement: **Production** (pas Sandbox)

### OAuth 2.0 Settings
- [ ] Application ID: `ABhjTWUsPqScOqpWeCghMKHpx85MbL0fM9JQnt4uXpD4Wynk`
- [ ] Client Secret correspond à celui dans `backend/.env`
- [ ] Scopes configurés: `com.intuit.quickbooks.accounting`

---

## 📄 Injection Squarespace

### Préparation
- [x] Fichier `SQUARESPACE_CODE_INJECTION_READY.html` prêt
- [x] Code contient: `BACKEND_URL = 'https://api.regenord.com'`
- [x] Code contient: `COMPANY_ID = 1`

### Injection
- [ ] Code copié depuis `SQUARESPACE_CODE_INJECTION_READY.html`
- [ ] Code collé dans Squarespace: **Settings → Advanced → Code Injection → Footer**
- [ ] Code sauvegardé dans Squarespace
- [ ] Page Squarespace publiée

---

## 🧪 Tests de Vérification

### Test 1: Page accessible
- [ ] URL `https://www.regenord.com/quickbooks-integration` accessible
- [ ] Interface QuickBooks s'affiche correctement
- [ ] Titre visible: "🔗 Intégration QuickBooks Online"
- [ ] Bouton "Connecter QuickBooks" visible

### Test 2: Statut de connexion
- [ ] Le statut se charge automatiquement
- [ ] Affiche "⏳ QuickBooks Non Connecté" ou "✅ QuickBooks Connecté"
- [ ] Pas d'erreur dans la console du navigateur (F12)

### Test 3: Connexion OAuth
- [ ] Cliquer sur "Connecter QuickBooks"
- [ ] Redirection vers Intuit OAuth (URL commence par `https://appcenter.intuit.com`)
- [ ] Page d'autorisation Intuit s'affiche
- [ ] Autoriser l'accès
- [ ] Redirection vers `https://www.regenord.com/quickbooks-integration?qbo_connected=true&realm_id=...`
- [ ] Message de succès affiché: "✅ QuickBooks connecté avec succès!"
- [ ] Statut mis à jour automatiquement

### Test 4: Déconnexion
- [ ] Bouton "Déconnecter QuickBooks" visible après connexion
- [ ] Cliquer sur "Déconnecter"
- [ ] Confirmation demandée
- [ ] Déconnexion réussie
- [ ] Statut mis à jour: "⏳ QuickBooks Non Connecté"

### Test 5: Synchronisation
- [ ] Après connexion, vérifier les logs backend
- [ ] Vérifier que les tokens sont sauvegardés
- [ ] Tester une synchronisation de données (si fonctionnalité disponible)

---

## 🔍 Vérifications Techniques

### Backend API
```bash
# Test de santé
curl https://api.regenord.com/api/health

# Test de configuration QBO
curl https://api.regenord.com/api/qbo/config/check

# Test de statut (nécessite company_id)
curl "https://api.regenord.com/api/qbo/status?company_id=1"
```

### Console Navigateur
- [ ] Pas d'erreurs JavaScript
- [ ] Requêtes vers `https://api.regenord.com` réussies
- [ ] Pas d'erreurs CORS
- [ ] Pas d'erreurs 404 ou 500

### Logs Backend
- [ ] Pas d'erreurs critiques
- [ ] Logs OAuth disponibles
- [ ] Tokens encryptés correctement
- [ ] Callbacks OAuth traités

---

## 📚 Documentation

### Fichiers créés
- [x] `SQUARESPACE_CODE_INJECTION_READY.html` - Code prêt à injecter
- [x] `backend/.env` - Configuration production
- [x] `GUIDE_INJECTION_SQUARESPACE.md` - Guide détaillé
- [x] `INJECTION_RAPIDE.md` - Guide rapide
- [x] `RESUME_FINAL_PRODUCTION.md` - Résumé complet
- [x] `CHECKLIST_FINALE.md` - Cette checklist

### Scripts utiles
- [x] `scripts/generate_security_keys.py` - Génération clés
- [x] `scripts/verify_production_setup.sh` - Vérification config

---

## 🚨 Points d'Attention

### Sécurité
- [ ] Le fichier `backend/.env` est dans `.gitignore`
- [ ] Les clés de sécurité ne sont pas commitées
- [ ] Les credentials PostgreSQL sont sécurisés
- [ ] HTTPS activé sur tous les endpoints

### Performance
- [ ] Backend répond rapidement (< 2 secondes)
- [ ] Page Squarespace se charge rapidement
- [ ] Pas de requêtes bloquantes

### Monitoring
- [ ] Logs du backend surveillés
- [ ] Erreurs trackées
- [ ] Métriques de performance disponibles

---

## ✅ Statut Final

### Configuration: ⚠️ Presque complète
- Il reste à configurer `DATABASE_URL` dans `backend/.env`

### Déploiement: ⏳ En attente
- Backend doit être déployé sur `https://api.regenord.com`
- Code doit être injecté dans Squarespace

### Tests: ⏳ En attente
- Tests à effectuer après déploiement et injection

---

## 📞 Support & Dépannage

### Commandes utiles
```bash
# Vérifier la configuration
./scripts/verify_production_setup.sh

# Vérifier les logs backend
tail -f logs/aia-regenord.log

# Tester la connexion backend
curl https://api.regenord.com/api/health
```

### Documentation
- Guide d'injection: `INJECTION_RAPIDE.md`
- Guide détaillé: `GUIDE_INJECTION_SQUARESPACE.md`
- Résumé complet: `RESUME_FINAL_PRODUCTION.md`

---

**Dernière mise à jour:** $(date)  
**Version:** Production 1.0
