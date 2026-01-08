# Guide de Déploiement QuickBooks Online

## 📋 Checklist Pré-Production

### 1. Configuration Sandbox (Actuel)

✅ **Status actuel**: Configuration sandbox en place

**Variables d'environnement** (`backend/.env`):
```env
QBO_ENVIRONMENT=sandbox
QBO_CLIENT_ID=<votre_client_id_sandbox>
QBO_CLIENT_SECRET=<votre_client_secret_sandbox>
QBO_REDIRECT_URI=http://localhost:8000/api/qbo/callback
```

**Endpoints disponibles**:
- `GET /api/qbo/connect/sandbox?company_id=1` - Connexion sandbox
- `GET /api/qbo/status?company_id=1` - Statut de la connexion
- `GET /api/qbo/data?company_id=1&months=12` - Données brutes QBO

---

## 🧪 Tests Sandbox

### Étapes de test

1. **Connexion OAuth Sandbox**
   ```
   Ouvrir: http://localhost:3000
   Cliquer sur "Connecter QBO" (sandbox)
   Autoriser l'application dans Intuit Sandbox
   ```

2. **Vérifier la connexion**
   - Le statut doit afficher "Connecté"
   - Le Realm ID doit être visible

3. **Synchroniser les données**
   ```bash
   curl -X POST http://localhost:8000/api/qbo/sync \
     -H "Content-Type: application/json" \
     -d '{"company_id": 1, "months": 12}'
   ```

4. **Vérifier les données**
   - Cliquer sur "Voir Vue QBO" dans l'interface
   - Vérifier les comptes, transactions et snapshots
   - Analyser les anomalies détectées

5. **Tester la vue AIA**
   - Cliquer sur "Voir Vue AIA"
   - Vérifier le mapping des catégories
   - Vérifier la réconciliation (total_qbo = total_aia)

6. **Tester l'export**
   ```bash
   curl "http://localhost:8000/api/aia/export/google-sheets?company_id=1&months=12&format=csv"
   ```

---

## 🚀 Passage en Production

### Prérequis

1. **Application Intuit en Production**
   - [ ] Application créée dans Intuit Developer (mode Production)
   - [ ] Client ID de production obtenu
   - [ ] Client Secret de production obtenu
   - [ ] Redirect URI configurée dans Intuit Developer:
     ```
     https://votre-domaine.com/api/qbo/callback
     ```
   - [ ] Scopes autorisés: `com.intuit.quickbooks.accounting openid profile email`

2. **Certificats et Sécurité**
   - [ ] `AIA_TOKEN_ENCRYPTION_KEY` générée (Fernet key, 32 bytes base64)
     ```python
     from cryptography.fernet import Fernet
     key = Fernet.generate_key()
     print(key.decode())  # À mettre dans .env
     ```
   - [ ] `SECRET_KEY` changé (string longue et aléatoire)
   - [ ] HTTPS activé pour la production

3. **Base de Données**
   - [ ] Base de données production configurée
   - [ ] Migrations appliquées
   - [ ] Backup configuré

4. **Variables d'Environnement Production**

   Créer `backend/.env.production`:
   ```env
   # QuickBooks Production
   QBO_ENVIRONMENT=production
   QBO_CLIENT_ID=<client_id_production>
   QBO_CLIENT_SECRET=<client_secret_production>
   QBO_REDIRECT_URI=https://votre-domaine.com/api/qbo/callback
   
   # Sécurité
   AIA_TOKEN_ENCRYPTION_KEY=<clé_fernet_32_bytes_base64>
   SECRET_KEY=<clé_secrète_longue_et_aléatoire>
   
   # Base de données
   DATABASE_URL=postgresql://user:pass@host:5432/dbname
   
   # Frontend
   CORS_ORIGINS=["https://votre-domaine.com"]
   APP_BASE_URL=https://votre-domaine.com
   ```

### Migration Sandbox → Production

⚠️ **IMPORTANT**: Les connexions sandbox et production sont **séparées**. Vous devrez reconnecter l'application en production.

#### Option 1: Utiliser la même configuration (recommandé pour débuter)

Modifier `backend/.env`:
```env
QBO_ENVIRONMENT=production
QBO_CLIENT_ID=<client_id_production>
QBO_CLIENT_SECRET=<client_secret_production>
QBO_REDIRECT_URI=https://votre-domaine.com/api/qbo/callback
```

Redémarrer le backend:
```bash
docker-compose restart backend
```

#### Option 2: Support simultané Sandbox + Production

Le code supporte déjà des variables d'environnement séparées:
```env
QBO_SANDBOX_CLIENT_ID=<sandbox_client_id>
QBO_SANDBOX_CLIENT_SECRET=<sandbox_client_secret>
QBO_PRODUCTION_CLIENT_ID=<production_client_id>
QBO_PRODUCTION_CLIENT_SECRET=<production_client_secret>
QBO_ENVIRONMENT=production  # ou sandbox
```

---

## 🔄 Processus de Connexion Production

1. **Endpoint de connexion production**
   ```
   GET /api/qbo/connect/production?company_id=1
   ```
   
   Ou depuis le frontend, utiliser:
   ```javascript
   const response = await axios.get(
     `${API_URL}/api/qbo/connect/production?company_id=1&redirect=false`
   );
   window.location.href = response.data.auth_url;
   ```

2. **Autorisation utilisateur**
   - L'utilisateur sera redirigé vers Intuit OAuth (production)
   - Il devra autoriser l'application
   - Après autorisation, redirection vers votre callback

3. **Vérification**
   ```bash
   curl "http://localhost:8000/api/qbo/status?company_id=1"
   ```

---

## ⚠️ Points d'Attention Production

1. **Rate Limiting**
   - QuickBooks API a des limites de taux
   - Surveiller les erreurs 429 (Too Many Requests)
   - Implémenter un backoff exponentiel si nécessaire

2. **Tokens de Rafraîchissement**
   - Les tokens expirent après 101 jours
   - Le système rafraîchit automatiquement les tokens
   - Surveiller les erreurs d'authentification

3. **Sécurité**
   - ✅ Tokens encryptés dans la base de données
   - ✅ HTTPS obligatoire en production
   - ✅ CORS configuré pour votre domaine uniquement
   - ✅ Secrets dans variables d'environnement (jamais dans le code)

4. **Monitoring**
   - Logger les erreurs d'API QBO
   - Surveiller les échecs de synchronisation
   - Surveiller les anomalies détectées

5. **Backup**
   - Sauvegarder régulièrement la base de données
   - Les tokens encryptés nécessitent `AIA_TOKEN_ENCRYPTION_KEY` pour être décryptés

---

## 🧹 Nettoyage Sandbox (Optionnel)

Si vous voulez nettoyer les données sandbox après migration:

```sql
-- Supprimer les connexions sandbox (ATTENTION: données de test seulement)
DELETE FROM qbo_connections WHERE company_id = 1;
DELETE FROM qbo_accounts WHERE qbo_company_id IN (SELECT realm_id FROM qbo_connections WHERE company_id = 1);
DELETE FROM qbo_transaction_lines WHERE company_id = 1;
DELETE FROM qbo_report_snapshots WHERE company_id = 1;
```

**⚠️ Ne pas faire cela avant d'avoir testé la production!**

---

## 📊 Vérification Post-Déploiement

1. **Test de connexion**
   - [ ] Connexion OAuth production réussie
   - [ ] Realm ID reçu et stocké

2. **Test de synchronisation**
   - [ ] Comptes synchronisés
   - [ ] Transactions synchronisées (derniers 12 mois)
   - [ ] Snapshots P&L créés

3. **Test de mapping AIA**
   - [ ] Vue AIA générée
   - [ ] Mapping des catégories correct
   - [ ] Réconciliation OK (total_qbo = total_aia)

4. **Test d'anomalies**
   - [ ] Analyse d'anomalies fonctionnelle
   - [ ] Détection des problèmes correcte

5. **Test d'export**
   - [ ] Export CSV fonctionnel
   - [ ] Export JSON fonctionnel

---

## 🔧 Dépannage

### Erreur: "Invalid redirect_uri"
- Vérifier que le redirect_uri dans `.env` correspond exactement à celui configuré dans Intuit Developer
- Les URLs doivent être identiques (https, pas de slash final)

### Erreur: "Invalid client credentials"
- Vérifier que les Client ID et Secret correspondent à l'environnement (sandbox vs production)
- Vérifier que l'application est en mode "Production" dans Intuit Developer

### Erreur: "Token expired"
- Les tokens sont automatiquement rafraîchis, mais vérifier que le refresh_token est valide
- Si le refresh_token est expiré (>101 jours), reconnecter l'application

### Erreur: "Rate limit exceeded"
- Réduire la fréquence des appels API
- Implémenter un cache pour les données rarement modifiées
- Utiliser les snapshots au lieu de requêter les transactions à chaque fois

---

## 📞 Support

- **Documentation Intuit**: https://developer.intuit.com/docs
- **Status API Intuit**: https://status.developer.intuit.com/
- **Logs**: Vérifier `backend/logs/aia-regenord.log`

---

## ✅ Checklist Finale Production

- [ ] Application Intuit en mode Production
- [ ] Client ID et Secret de production configurés
- [ ] Redirect URI configurée et testée
- [ ] HTTPS activé
- [ ] Variables d'environnement sécurisées
- [ ] Tokens encryptés avec clé forte
- [ ] CORS configuré pour votre domaine
- [ ] Tests de connexion réussis
- [ ] Tests de synchronisation réussis
- [ ] Tests de mapping AIA réussis
- [ ] Monitoring et logging en place
- [ ] Backup de la base de données configuré

---

**Bon déploiement! 🚀**
