# 🔄 Redémarrer le Backend en Mode Production

## ❌ Problème Détecté

Le backend est configuré pour la production dans `backend/.env`, mais le processus en cours d'exécution utilise encore les paramètres sandbox.

**Solution:** Redémarrer le backend pour charger la nouvelle configuration.

---

## 🔍 État Actuel

- ✅ `backend/.env` configuré: `QBO_ENVIRONMENT=production`
- ❌ Backend en cours d'exécution: Utilise encore sandbox
- ✅ Frontend corrigé: Utilise maintenant `/api/qbo/connect/production`

---

## 🔄 Étape 1: Arrêter le Backend Actuel

### Option A: Via le Terminal où il tourne

1. Trouver le terminal où le backend est lancé
2. Appuyer sur `Ctrl+C` pour arrêter le processus

### Option B: Arrêter le processus directement

```bash
# Trouver le processus
ps aux | grep uvicorn

# Arrêter le processus (remplacer PID par le numéro du processus)
kill <PID>

# Ou forcer l'arrêt si nécessaire
kill -9 <PID>
```

### Option C: Arrêter par port

```bash
# Tuer le processus utilisant le port 8000
lsof -ti:8000 | xargs kill -9
```

---

## 🚀 Étape 2: Vérifier la Configuration

Avant de redémarrer, vérifier que `backend/.env` est correct:

```bash
cd /Users/alain/Documents/aia-regenord/backend
cat .env | grep QBO_ENVIRONMENT
# Devrait afficher: QBO_ENVIRONMENT=production
```

**Variables importantes:**
- `QBO_ENVIRONMENT=production`
- `QBO_CLIENT_ID=ABhjTWUsPqScOqpWeCghMKHpx85MbL0fM9JQnt4uXpD4Wynk`
- `QBO_CLIENT_SECRET=d2R1L2EFjbZyNmJdcYnnbibh6AVsIVlZDFF9dc8V`
- `QBO_REDIRECT_URI=https://www.regenord.com/quickbooks-integration/callback`

---

## 🚀 Étape 3: Redémarrer le Backend

### Option A: Avec l'environnement virtuel (Recommandé)

```bash
cd /Users/alain/Documents/aia-regenord/backend

# Activer l'environnement virtuel
source .venv/bin/activate

# Démarrer le backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Option B: Avec Docker (si utilisé)

```bash
docker-compose restart backend
# ou
docker restart <container_name>
```

---

## ✅ Étape 4: Vérifier que c'est en Production

Une fois le backend redémarré, vérifier:

```bash
curl http://localhost:8000/api/qbo/config/check | python3 -m json.tool
```

**Vérifier que:**
- `"environment": "production"`
- `"api_base_url": "https://quickbooks.api.intuit.com"` (pas sandbox)
- `"ready_for_production": true`

---

## 🔧 Étape 5: Vérifier le Frontend

1. Rafraîchir la page `http://localhost:3000`
2. Vérifier que l'environnement affiche "Production" dans les paramètres
3. Cliquer sur "Connecter QBO" devrait maintenant utiliser l'endpoint production

---

## 🐛 Dépannage

### Le backend ne démarre pas

**Vérifier:**
- Les dépendances sont installées: `pip install -r requirements.txt`
- L'environnement virtuel est activé
- Le port 8000 est libre: `lsof -i:8000`

### Le backend démarre mais reste en sandbox

**Vérifier:**
- Le fichier `.env` est bien dans `backend/.env`
- Les variables sont bien définies (pas de guillemets, pas d'espaces)
- Le backend charge bien le `.env` (vérifier les logs au démarrage)

### Erreur de connexion QBO en production

**Vérifier:**
- Les credentials de production dans Intuit Developer sont corrects
- Le Redirect URI est configuré dans Intuit Developer
- L'application est en mode Production dans Intuit Developer

---

## 📝 Notes

- Le backend doit être redémarré après chaque modification du fichier `.env`
- L'option `--reload` permet de recharger automatiquement lors des changements de code, mais pas pour les variables d'environnement
- En production, utiliser un gestionnaire de processus comme `systemd`, `supervisor`, ou `PM2`

---

**Une fois le backend redémarré, il utilisera la configuration de production!**
