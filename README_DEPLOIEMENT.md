# 🚀 Guide de Déploiement Rapide - QuickBooks Integration

**Guide de démarrage rapide pour déployer l'intégration QuickBooks Online en production.**

---

## ⚡ Démarrage Rapide (5 minutes)

### 1. Vérifier la configuration

```bash
# Validation complète
./scripts/validate_production_env.sh

# Vérification rapide
./scripts/verify_production_setup.sh
```

### 2. Configurer DATABASE_URL (si pas déjà fait)

Éditer `backend/.env`:
```env
DATABASE_URL=postgresql://votre_user:votre_password@votre_host:5432/votre_database
```

### 3. Injecter le code Squarespace

```bash
# Préparer le code
./scripts/prepare_code_for_squarespace.sh

# Ou ouvrir manuellement:
# SQUARESPACE_CODE_INJECTION_READY.html
```

Dans Squarespace: **Settings → Advanced → Code Injection → Footer**

### 4. Tester

```bash
# Test automatique
./scripts/test_oauth_connection.sh

# Test manuel
# Aller sur: https://www.regenord.com/quickbooks-integration
```

---

## 📚 Documentation Complète

### Pour un déploiement complet
👉 **[DEPLOIEMENT_ETAPE_PAR_ETAPE.md](DEPLOIEMENT_ETAPE_PAR_ETAPE.md)** - Guide complet (30-45 min)

### Pour vérifier avant déploiement
👉 **[VERIFICATION_FINALE.md](VERIFICATION_FINALE.md)** - Checklist complète

### Pour injection rapide
👉 **[INJECTION_RAPIDE.md](INJECTION_RAPIDE.md)** - Guide 2 minutes

### Pour tester après injection
👉 **[GUIDE_TEST_POST_INJECTION.md](GUIDE_TEST_POST_INJECTION.md)** - Tests détaillés

### Navigation complète
👉 **[INDEX_DOCUMENTATION.md](INDEX_DOCUMENTATION.md)** - Index de tous les guides

---

## 🔧 Scripts Disponibles

| Script | Description | Commande |
|--------|-------------|----------|
| `validate_production_env.sh` | Validation avancée des variables | `./scripts/validate_production_env.sh` |
| `verify_production_setup.sh` | Vérification rapide de la config | `./scripts/verify_production_setup.sh` |
| `test_oauth_connection.sh` | Test de connexion OAuth | `./scripts/test_oauth_connection.sh` |
| `prepare_code_for_squarespace.sh` | Préparer code pour injection | `./scripts/prepare_code_for_squarespace.sh` |
| `generate_security_keys.py` | Générer les clés de sécurité | `python3 scripts/generate_security_keys.py` |

---

## ✅ Checklist Minimale

- [ ] `DATABASE_URL` configuré dans `backend/.env`
- [ ] Backend déployé sur `https://api.regenord.com`
- [ ] Redirect URI configuré dans Intuit Developer: `https://www.regenord.com/quickbooks-integration/callback`
- [ ] Code injecté dans Squarespace (Settings → Advanced → Code Injection → Footer)
- [ ] Test de connexion OAuth réussi

---

## 🔍 Vérification Rapide

```bash
# 1. Vérifier la configuration
./scripts/validate_production_env.sh

# 2. Vérifier le backend (si déployé)
curl https://api.regenord.com/api/health

# 3. Tester la connexion (après injection)
./scripts/test_oauth_connection.sh
```

---

## 📋 Configuration Requise

### Variables Backend (`backend/.env`)

**QuickBooks:**
- `QBO_ENVIRONMENT=production`
- `QBO_CLIENT_ID=ABhjTWUsPqScOqpWeCghMKHpx85MbL0fM9JQnt4uXpD4Wynk`
- `QBO_CLIENT_SECRET=d2R1L2EFjbZyNmJdcYnnbibh6AVsIVlZDFF9dc8V`
- `QBO_REDIRECT_URI=https://www.regenord.com/quickbooks-integration/callback`

**Application:**
- `APP_BASE_URL=https://api.regenord.com`
- `FRONTEND_URL=https://www.regenord.com`
- `DEBUG=False`
- `DATABASE_URL=postgresql://...` ⚠️ **À configurer**

**Sécurité:**
- `AIA_TOKEN_ENCRYPTION_KEY=...` ✅ Généré
- `SECRET_KEY=...` ✅ Généré

---

## 🐛 Problèmes Courants

### "redirect_uri_mismatch"
→ Vérifier que le Redirect URI dans Intuit Developer correspond exactement à `backend/.env`

### "Cannot connect to backend"
→ Vérifier que le backend est déployé et accessible sur `https://api.regenord.com`

### "Database connection failed"
→ Vérifier `DATABASE_URL` dans `backend/.env`

### Page Squarespace blanche
→ Vérifier que le code est dans **Footer** (pas Header) et qu'il n'y a pas d'erreurs JavaScript

---

## 📞 Support

- **Documentation complète:** `INDEX_DOCUMENTATION.md`
- **Guide de dépannage:** `GUIDE_INJECTION_SQUARESPACE.md`
- **Vérification:** `VERIFICATION_FINALE.md`

---

## 🎉 Prêt!

Une fois toutes les étapes complétées, l'intégration QuickBooks Online sera opérationnelle en production.

**Prochaine étape:** Consulter `DEPLOIEMENT_ETAPE_PAR_ETAPE.md` pour le guide complet.

---

**Version:** Production 1.0  
**Dernière mise à jour:** $(date)
