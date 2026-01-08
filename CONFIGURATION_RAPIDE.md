# 🚀 Configuration Rapide - Production

## Étapes Automatisées

### 1. Configuration Backend (.env)

```bash
cd /Users/alain/Documents/aia-regenord
./scripts/setup_production_env.sh
```

Ce script va:
- Générer automatiquement les clés de sécurité (Fernet + Secret)
- Demander l'URL de votre backend
- Créer le fichier `backend/.env` avec toutes les variables configurées

**⚠️ Important:** Vérifiez `DATABASE_URL` après la création du fichier!

### 2. Préparer le Code Squarespace

```bash
./scripts/prepare_squarespace_code.sh
```

Ce script va:
- Extraire l'URL du backend depuis `backend/.env`
- Créer `SQUARESPACE_CODE_INJECTION_READY.html` avec l'URL configurée
- Vous donner les instructions pour l'injection

### 3. Tester la Configuration

```bash
./scripts/test_production_config.sh
```

Ce script vérifie:
- ✅ Toutes les variables d'environnement sont configurées
- ✅ Les credentials production sont corrects
- ✅ Le backend est accessible
- ✅ La configuration QBO est valide

---

## Instructions Manuelles

### Si vous préférez configurer manuellement:

#### 1. Générer les Clés de Sécurité

```bash
python3 scripts/generate_security_keys.py
```

Copier les clés générées.

#### 2. Créer backend/.env

Copier `BACKEND_ENV_TEMPLATE.txt` vers `backend/.env` et:
- Remplacer `YOUR_BACKEND_URL` par l'URL réelle
- Remplacer `YOUR_FERNET_KEY_HERE` par la clé Fernet générée
- Remplacer `YOUR_SECRET_KEY_HERE` par la clé secrète générée
- Configurer `DATABASE_URL`

#### 3. Préparer Code Squarespace

Ouvrir `SQUARESPACE_CODE_INJECTION_FINAL.html`:
- Ligne 10: Remplacer `YOUR_BACKEND_URL` par l'URL du backend
- Copier tout le contenu
- Coller dans Squarespace: **Settings > Advanced > Code Injection > Footer**

---

## ✅ Checklist Finale

Après avoir exécuté les scripts:

- [ ] `backend/.env` créé et configuré
- [ ] Clés de sécurité générées
- [ ] `DATABASE_URL` vérifié et configuré
- [ ] `SQUARESPACE_CODE_INJECTION_READY.html` créé (ou code modifié manuellement)
- [ ] Code injecté dans Squarespace
- [ ] Test de configuration réussi (`./scripts/test_production_config.sh`)
- [ ] Test de connexion OAuth réussi

---

## 🔍 Dépannage

### Scripts ne fonctionnent pas

```bash
# Rendre les scripts exécutables
chmod +x scripts/*.sh

# Vérifier les permissions
ls -l scripts/*.sh
```

### Module cryptography manquant

```bash
pip install cryptography
```

### Backend non accessible

- Vérifier que le backend est déployé
- Vérifier que HTTPS est activé
- Vérifier les règles de firewall/CORS

---

**🎉 Une fois les scripts exécutés, votre configuration production sera prête!**
