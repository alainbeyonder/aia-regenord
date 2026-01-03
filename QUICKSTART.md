# 🚀 Guide de Démarrage Rapide - AIA Regenord

## Prérequis

Avant de commencer, assurez-vous d'avoir installé:

- **Python 3.11+** - [Télécharger](https://www.python.org/downloads/)
- **Docker Desktop** - [Télécharger](https://www.docker.com/products/docker-desktop/)
- **Git** - [Télécharger](https://git-scm.com/downloads)
- **Compte QuickBooks Online** avec accès API
- **Clé API OpenAI** (GPT-4) - [Obtenir](https://platform.openai.com/api-keys)

## Installation Rapide

### 1️⃣ Cloner le Dépôt

```bash
git clone https://github.com/alainbeyonder/aia-regenord.git
cd aia-regenord
```

### 2️⃣ Créer l'Environnement Virtuel

```bash
# Créer l'environnement
python3 -m venv venv

# Activer (Mac/Linux)
source venv/bin/activate

# Activer (Windows)
venv\Scripts\activate
```

### 3️⃣ Installer les Dépendances

```bash
pip install -r requirements.txt
```

### 4️⃣ Configurer les Variables d'Environnement

```bash
# Copier le template
cp .env.example .env

# Éditer avec vos credentials
nano .env  # ou votre éditeur préféré
```

**Variables essentielles à configurer dans `.env`:**

```env
# QuickBooks Online
QBO_CLIENT_ID=votre-client-id-qbo
QBO_CLIENT_SECRET=votre-client-secret
QBO_REDIRECT_URI=http://localhost:8000/api/qbo/callback
QBO_COMPANY_ID=votre-company-id

# OpenAI
OPENAI_API_KEY=sk-votre-cle-api-openai

# Base de données
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/aia_regenord

# Application
SECRET_KEY=changez-cette-cle-secrete
DEBUG=True
```

### 5️⃣ Lancer la Base de Données (Docker)

```bash
# Lancer PostgreSQL et Redis
docker-compose up -d

# Vérifier que les conteneurs sont actifs
docker ps
```

### 6️⃣ Démarrer l'Application

```bash
# Lancer le serveur FastAPI
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🎯 Accéder à l'Application

- **Dashboard Frontend**: http://localhost:8000/
- **Documentation API**: http://localhost:8000/docs
- **API Alternative (ReDoc)**: http://localhost:8000/redoc

## ✅ Vérification de l'Installation

### Test de Santé de l'API

```bash
curl http://localhost:8000/health
```

Réponse attendue:
```json
{"status": "healthy", "version": "1.0.0"}
```

## 🔐 Configuration QuickBooks Online

### Obtenir vos Credentials QBO

1. Aller sur [QuickBooks Developer Portal](https://developer.intuit.com/)
2. Créer une nouvelle application
3. Copier le **Client ID** et **Client Secret**
4. Définir le **Redirect URI**: `http://localhost:8000/api/qbo/callback`
5. Ajouter ces valeurs dans votre fichier `.env`

### Se Connecter à QBO

1. Ouvrir http://localhost:8000/docs
2. Naviguer vers `/api/qbo/connect`
3. Suivre le processus OAuth
4. Autoriser l'application

## 📊 Utilisation de Base

### Générer des Projections Financières

```bash
curl -X POST "http://localhost:8000/api/projections/generate" \
  -H "Content-Type: application/json" \
  -d '{"years": 3, "growth_rate": 0.15}'
```

### Extraire les Données QBO

```bash
curl "http://localhost:8000/api/qbo/financial-data?year=2025"
```

## 🛠️ Commandes Utiles

### Arrêter l'Application

```bash
# Arrêter FastAPI: Ctrl+C dans le terminal

# Arrêter Docker
docker-compose down
```

### Voir les Logs Docker

```bash
# PostgreSQL
docker logs aia_regenord_db

# Redis
docker logs aia_regenord_redis
```

### Reconstruire la Base de Données

```bash
docker-compose down -v
docker-compose up -d
```

## ❓ Dépannage

### Erreur: "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Erreur: "Connection refused" (PostgreSQL)
```bash
docker-compose up -d
docker ps  # Vérifier que PostgreSQL est actif
```

### Erreur: "Invalid QBO credentials"
- Vérifier que `QBO_CLIENT_ID` et `QBO_CLIENT_SECRET` sont corrects dans `.env`
- S'assurer que le `REDIRECT_URI` correspond exactement à celui configuré sur QuickBooks Developer Portal

## 📚 Prochaines Étapes

1. Consulter la [Documentation Complète](./README.md)
2. Explorer les [Routes API](http://localhost:8000/docs)
3. Configurer [Google Sheets Export](./README.md#google-sheets)
4. Déployer en Production (voir README.md)

## 💡 Support

Pour toute question ou problème:
- Consulter la [Documentation](./README.md)
- Ouvrir une [Issue GitHub](https://github.com/alainbeyonder/aia-regenord/issues)

---

**Bon démarrage avec AIA Regenord! 🎉**
