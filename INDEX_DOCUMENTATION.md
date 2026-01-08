# 📚 Index de la Documentation - Configuration Production

## 🎯 Par où commencer?

### Pour un démarrage rapide (recommandé)
👉 **`README_DEPLOIEMENT.md`** - Guide de démarrage rapide (5 min)

### Pour un déploiement complet
👉 **`DEPLOIEMENT_ETAPE_PAR_ETAPE.md`** - Guide complet étape par étape (30-45 min)

### Pour vérifier avant déploiement
👉 **`VERIFICATION_FINALE.md`** - Checklist complète de vérification

### Pour une injection rapide (2 minutes)
👉 **`INJECTION_RAPIDE.md`** - Guide ultra-rapide avec étapes simples

### Pour une vue d'ensemble complète
👉 **`RESUME_FINAL_PRODUCTION.md`** - Résumé technique complet

### Pour suivre pas à pas
👉 **`CHECKLIST_FINALE.md`** - Checklist détaillée avec toutes les étapes

---

## 📁 Fichiers par catégorie

### 🚀 Guides d'injection

| Fichier | Description | Quand l'utiliser |
|---------|-------------|------------------|
| `INJECTION_RAPIDE.md` | Guide ultra-rapide (2 min) | Injection rapide dans Squarespace |
| `GUIDE_INJECTION_SQUARESPACE.md` | Guide détaillé avec dépannage | Besoin d'aide ou de détails |
| `GUIDE_TEST_POST_INJECTION.md` | Guide de test après injection | Tester l'intégration après déploiement |

### 📋 Configuration et résumés

| Fichier | Description | Quand l'utiliser |
|---------|-------------|------------------|
| `README_DEPLOIEMENT.md` | Guide de démarrage rapide | **Démarrage rapide (5 min)** |
| `DEPLOIEMENT_ETAPE_PAR_ETAPE.md` | Guide complet étape par étape | **Déploiement complet (30-45 min)** |
| `VERIFICATION_FINALE.md` | Checklist de vérification | Avant déploiement |
| `RESUME_FINAL_PRODUCTION.md` | Résumé technique complet | Vue d'ensemble de la config |
| `CHECKLIST_FINALE.md` | Checklist complète | Suivre toutes les étapes |
| `CONFIGURATION_FINALE.md` | Configuration détaillée | Détails techniques |

### 🔧 Code et configuration

| Fichier | Description | Quand l'utiliser |
|---------|-------------|------------------|
| `SQUARESPACE_CODE_INJECTION_READY.html` | Code JavaScript prêt | **À injecter dans Squarespace** (recommandé) |
| `SQUARESPACE_CODE_CLEAN.html` | Code sans commentaires HTML | Si Squarespace rejette les commentaires |
| `backend/.env` | Configuration backend | Variables d'environnement production |
| `BACKEND_ENV_TEMPLATE.txt` | Template de configuration | Référence pour .env |

### 🛠️ Scripts

| Fichier | Description | Commande |
|---------|-------------|----------|
| `scripts/validate_production_env.sh` | Validation avancée des variables | `./scripts/validate_production_env.sh` ⭐ |
| `scripts/verify_production_setup.sh` | Vérifie la configuration | `./scripts/verify_production_setup.sh` |
| `scripts/test_oauth_connection.sh` | Teste la connexion OAuth | `./scripts/test_oauth_connection.sh` |
| `scripts/prepare_code_for_squarespace.sh` | Prépare le code pour injection | `./scripts/prepare_code_for_squarespace.sh` |
| `scripts/generate_security_keys.py` | Génère les clés de sécurité | `python3 scripts/generate_security_keys.py` |

### 📖 Documentation technique

| Fichier | Description | Quand l'utiliser |
|---------|-------------|------------------|
| `SQUARESPACE_INTEGRATION.md` | Guide d'intégration Squarespace | Comprendre l'architecture |
| `DEPLOIEMENT_PRODUCTION.md` | Guide de déploiement | Déployer le backend |
| `CONFIGURATION_PRODUCTION.md` | Configuration production | Configurer l'environnement |

---

## 🎯 Workflow recommandé

### Étape 1: Configuration initiale
1. Lire: `RESUME_FINAL_PRODUCTION.md`
2. Vérifier: `./scripts/verify_production_setup.sh`
3. Configurer: `DATABASE_URL` dans `backend/.env`

### Étape 2: Injection Squarespace
1. Lire: `INJECTION_RAPIDE.md`
2. Ouvrir: `SQUARESPACE_CODE_INJECTION_READY.html`
3. Injecter dans Squarespace (voir guide)

### Étape 3: Tests
1. Suivre: `CHECKLIST_FINALE.md`
2. Tester la connexion OAuth
3. Vérifier les logs backend

---

## 🔍 Recherche rapide

### "Comment injecter le code?"
→ `INJECTION_RAPIDE.md`

### "Comment configurer la base de données?"
→ `RESUME_FINAL_PRODUCTION.md` (section DATABASE_URL)

### "Où sont les URLs configurées?"
→ `backend/.env` (APP_BASE_URL, FRONTEND_URL, QBO_REDIRECT_URI)

### "Comment vérifier que tout est prêt?"
→ `./scripts/verify_production_setup.sh`

### "Erreur redirect_uri_mismatch?"
→ `GUIDE_INJECTION_SQUARESPACE.md` (section Dépannage)

### "Quels sont les credentials QuickBooks?"
→ `backend/.env` (QBO_CLIENT_ID, QBO_CLIENT_SECRET)

### "Comment tester la connexion?"
→ `CHECKLIST_FINALE.md` (section Tests)

---

## ✅ Checklist rapide

- [ ] `backend/.env` configuré (sauf DATABASE_URL si pas encore)
- [ ] `DATABASE_URL` configuré dans `backend/.env`
- [ ] Code Squarespace prêt: `SQUARESPACE_CODE_INJECTION_READY.html`
- [ ] Backend déployé sur `https://api.regenord.com`
- [ ] Code injecté dans Squarespace
- [ ] Redirect URI configuré dans Intuit Developer
- [ ] Tests de connexion OAuth réussis

---

## 📞 Support

### Problème technique?
1. Vérifier les logs: `tail -f logs/aia-regenord.log`
2. Vérifier la config: `./scripts/verify_production_setup.sh`
3. Consulter: `GUIDE_INJECTION_SQUARESPACE.md` (section Dépannage)

### Question sur la configuration?
1. Consulter: `RESUME_FINAL_PRODUCTION.md`
2. Vérifier: `CHECKLIST_FINALE.md`

---

**Dernière mise à jour:** $(date)  
**Version:** Production 1.0
