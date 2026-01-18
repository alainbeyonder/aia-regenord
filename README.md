# aia-regenord
Agent IA Financier pour Groupe Regenord - Projections financières 3 ans avec intégration QBO, DEXT, et modèle IP/licences/RSDE

## 📋 Table des Matières

- [Description](#description)
- [Architecture](#architecture)
- [Installation Rapide](#installation-rapide)
- [Guide de Création des Fichiers](#guide-de-création-des-fichiers)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Documentation Complète](#documentation-complète)

## 📖 Description

L'AIA Regenord est un agent d'intelligence artificielle conçu spécifiquement pour Groupe Regenord Inc. Il aide à :

- **Synchroniser les données** de QuickBooks Online (QBO) et DEXT
- **Créer des scénarios** de projection financière personnalisés
- **Générer des projections** sur 3 ans (états de résultats, bilan, flux de trésorerie)
- **Modéliser le modèle d'affaires** IP/licences/RSDE en transition
- **Utiliser l'IA** (OpenAI) pour affiner les hypothèses de projection

## 🏗️ Architecture

```
aia-regenord/
├── backend/
│   ├── app/
│   │   ├── main.py              # Point d'entrée FastAPI
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py        # Configuration Pydantic
│   │   │   └── database.py      # Connexion PostgreSQL
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── company.py       # Modèle Company
│   │   │   ├── financial_statement.py
│   │   │   ├── scenario.py
│   │   │   └── projection.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── qbo_service.py   # Intégration QBO
│   │   │   ├── dext_service.py  # Intégration DEXT
│   │   │   ├── openai_service.py
│   │   │   └── projection_service.py
│   │   └── api/
│   │       ├── __init__.py
│   │       ├── qbo.py           # Endpoints QBO
│   │       └── scenarios.py     # Endpoints scénarios
│   ├── requirements.txt
│   └── alembic/
│       └── env.py
├── frontend/
│   └── package.json
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## 🚀 Installation Rapide

### Prérequis

- Python 3.11+
- PostgreSQL 15+
- Git
- Node.js 18+ (pour le frontend)
- Compte QuickBooks Online
- Clés API OpenAI

### Étape 1: Cloner le Repository

```bash
git clone https://github.com/alainbeyonder/aia-regenord.git
cd aia-regenord
```


## 📝 Guide de Création des Fichiers

### Méthode Recommandée: Création Locale

Tous les fichiers et leur code source complet sont disponibles dans le document Google Docs:
**[AIA Regenord - Code Source Complet - Guide d'Implémentation](https://docs.google.com/document/d/1BkkW_QkMIhqabvljN2VQnP9XkAkizwlVNXoa0cXNUYk/edit)**

### Étape 2: Créer la Structure de Dossiers

```bash
# Créer tous les dossiers nécessaires
mkdir -p backend/app/core
mkdir -p backend/app/models
mkdir -p backend/app/services
mkdir -p backend/app/api
mkdir -p backend/alembic
mkdir -p frontend
mkdir -p tests
```

### Étape 3: Créer les Fichiers __init__.py

```bash
# Créer les fichiers __init__.py pour rendre les dossiers en modules Python
touch backend/app/__init__.py
touch backend/app/core/__init__.py
touch backend/app/models/__init__.py
touch backend/app/services/__init__.py
touch backend/app/api/__init__.py
```

### Étape 4: Créer les Fichiers et Copier le Code

**Ouvrez le [document Google Docs](https://docs.google.com/document/d/1BkkW_QkMIhqabvljN2VQnP9XkAkizwlVNXoa0cXNUYk/edit)** qui contient le code source complet de tous les 17 fichiers:

#### Fichiers Core (backend/app/core/)
1. **config.py** - Configuration Pydantic avec variables d'environnement
2. **database.py** - Connexion PostgreSQL et session SQLAlchemy

#### Fichiers Models (backend/app/models/)
3. **company.py** - Modèle Company (SQLAlchemy)
4. **financial_statement.py** - Modèle FinancialStatement
5. **scenario.py** - Modèle Scenario avec hypothèses
6. **projection.py** - Modèle Projection avec calculs

#### Fichiers Services (backend/app/services/)
7. **qbo_service.py** - Service d'intégration QuickBooks Online OAuth2
8. **dext_service.py** - Service d'intégration DEXT
9. **openai_service.py** - Service OpenAI pour génération d'hypothèses
10. **projection_service.py** - Service de calcul des projections financières

#### Fichiers API (backend/app/api/)
11. **qbo.py** - Endpoints FastAPI pour QuickBooks (sync, callback)
12. **scenarios.py** - Endpoints pour scénarios et projections

#### Fichier Principal
13. **main.py** - Point d'entrée FastAPI avec tous les routers

#### Fichiers de Configuration
14. **backend/alembic/env.py** - Configuration Alembic pour migrations
15. **Dockerfile** - Image Docker pour le backend
16. **docker-compose.yml** - Orchestration Docker (backend, db, frontend)
17. **frontend/package.json** - Dépendances React

### Script de Création Rapide

Voici un script bash pour créer rapidement tous les fichiers vides:

```bash
#!/bin/bash

# Créer la structure
mkdir -p backend/app/{core,models,services,api} backend/alembic frontend tests

# Créer les __init__.py
touch backend/app/{__init__,core/__init__,models/__init__,services/__init__,api/__init__}.py

# Créer les fichiers core
touch backend/app/core/{config,database}.py

# Créer les fichiers models
touch backend/app/models/{company,financial_statement,scenario,projection}.py

# Créer les fichiers services
touch backend/app/services/{qbo_service,dext_service,openai_service,projection_service}.py

# Créer les fichiers API
touch backend/app/api/{qbo,scenarios}.py

# Créer les fichiers de configuration
touch backend/alembic/env.py
touch Dockerfile docker-compose.yml
touch frontend/package.json

echo "✅ Structure de fichiers créée! Copiez maintenant le code depuis le document Google Docs."
```

Après avoir exécuté ce script, **ouvrez chaque fichier et copiez le code correspondant depuis le document Google Docs (Section 3: Description des Fichiers)**.

## ⚙️ Configuration

### Étape 5: Configurer les Variables d'Environnement

Copiez le fichier `.env.example` vers `.env` et remplissez les valeurs:

```bash
cp .env.example .env
```

Éditez le fichier `.env` avec vos valeurs:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/aia_regenord

# API Keys
QBO_CLIENT_ID=votre_client_id_qbo
QBO_CLIENT_SECRET=votre_client_secret_qbo
QBO_REDIRECT_URI=http://localhost:8000/api/qbo/callback
QBO_ENVIRONMENT=sandbox  # ou 'production'

OPENAI_API_KEY=votre_clé_openai
OPENAI_MODEL=gpt-4

DEXT_API_KEY=votre_clé_dext
DEXT_API_URL=https://api.dext.com/v1

# Security
SECRET_KEY=votre_secret_key_genere
ALGORITHM=HS256

# App
DEBUG=True
LOG_LEVEL=INFO
```

### Étape 6: Installer les Dépendances

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend (optionnel pour cette phase)
cd ../frontend
npm install
```

### Étape 7: Initialiser la Base de Données

```bash
cd backend

# Créer la première migration
alembic revision --autogenerate -m "initial migration"

# Exécuter les migrations
alembic upgrade head
```

## 💻 Utilisation

### Démarrage avec Docker (Recommandé)

```bash
# Démarrer tous les services
docker-compose up -d

# Vérifier les logs
docker-compose logs -f backend

# Arrêter les services
docker-compose down
```

### Démarrage en Développement Local

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend (optionnel)
cd frontend
npm start

# Terminal 3 - Base de données (si locale)
psql -U postgres
```

### Accéder à l'Application

- **Backend API**: http://localhost:8000
- **Documentation Swagger**: http://localhost:8000/docs
- **Documentation ReDoc**: http://localhost:8000/redoc
- **Frontend** (si démarré): http://localhost:3000

## 📡 Utilisation de l'API

### 1. Synchroniser les Données QBO

```bash
curl -X POST http://localhost:8000/api/qbo/sync \
  -H "Content-Type: application/json" \
  -d '{"company_id": "VOTRE_QBO_COMPANY_ID"}'
```

### 2. Créer un Scénario de Projection

```bash
curl -X POST http://localhost:8000/api/scenarios \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": 1,
    "name": "Transition IP/Licences 2025-2028",
    "base_date": "2025-01-01T00:00:00",
    "projection_months": 36,
    "sales_assumptions": {
      "licenses": {
        "base_count": 5,
        "monthly_price": 2500,
        "monthly_growth_rate": 0.10
      },
      "consulting": {
        "base_monthly": 8000,
        "growth_rate": 0.05
      }
    },
    "expense_assumptions": {
      "salaries": {
        "base_monthly": 15000,
        "annual_increase": 0.03
      }
    }
  }'
```

### 3. Calculer les Projections

```bash
curl -X POST http://localhost:8000/api/scenarios/1/calculate
```

### 4. Récupérer les Projections

```bash
curl http://localhost:8000/api/scenarios/1/projections
```

## 🧾 Format JSON V1 (Scénario & Hypothèses)

Ce format décrit les hypothèses V1 attendues côté backend. Il sert de référence pour l’intégration.

```json
{
  "company_id": 1,
  "scenario_default": "realistic",
  "horizon": { "months_1": 12, "years_2_3": 2 },
  "revenue": {
    "monthly_growth_rate": 0.05,
    "events": [
      { "month": 4, "name": "New license", "monthly_amount": 8000, "probability": 0.8 }
    ]
  },
  "costs": {
    "fixed_costs_annual_inflation": 0.03,
    "events": [
      { "month": 6, "name": "New hire", "monthly_amount": 6500 }
    ],
    "optimization": [
      { "category_key": "expense_admin", "reduction_percent": 0.10, "start_month": 7 }
    ]
  },
  "debt": {
    "mode": "interest_only_then_resume",
    "interest_only_months": 6,
    "resume_mode": "normal",
    "equity_backstop": {
      "enabled": true,
      "max_amount": 65000,
      "trigger_min_cash": 20000
    }
  },
  "rsde": {
    "enabled": true,
    "eligible_salary_share": 0.80,
    "credit_estimated_amount": 75000,
    "prudence_factor": 0.75,
    "refund_delay_months": 9
  },
  "ias38": {
    "enabled": true,
    "capitalization_salary_share": 0.80,
    "apply_to_overheads": true,
    "overhead_share": 0.80,
    "amortization": {
      "enabled": false,
      "start_month": 0,
      "useful_life_years": 5
    }
  }
}
```

## 📚 Documentation Complète

La documentation complète avec tout le code source se trouve dans:
**[Document Google Docs - AIA Regenord](https://docs.google.com/document/d/1BkkW_QkMIhqabvljN2VQnP9XkAkizwlVNXoa0cXNUYk/edit)**

Ce document contient:
- ✅ Section 1: Architecture et Structure
- ✅ Section 2: Installation et Configuration
- ✅ Section 3: Code Source Complet des 17 Fichiers
- ✅ Section 4: Guide de Déploiement et Utilisation
- ✅ Section 5: Prochaines Étapes

## 🧪 Tests

```bash
# Exécuter les tests unitaires
cd backend
pytest tests/ -v

# Exécuter les tests d'intégration
pytest tests/integration/ -v

# Avec coverage
pytest tests/ --cov=app --cov-report=html
```

## 🚀 Déploiement en Production

### Option 1: Heroku

```bash
# Installer Heroku CLI
heroku create aia-regenord

# Ajouter PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Configurer les variables d'environnement
heroku config:set QBO_CLIENT_ID=votre_id
heroku config:set OPENAI_API_KEY=votre_cle

# Déployer
git push heroku main

# Exécuter les migrations
heroku run alembic upgrade head
```

### Option 2: AWS ECS / DigitalOcean

Consultez la **Section 4.8** du document Google Docs pour les instructions détaillées.

## 🔧 Stack Technologique

### Backend
- **FastAPI** - Framework web Python moderne et rapide
- **SQLAlchemy** - ORM pour PostgreSQL
- **Alembic** - Migrations de base de données
- **Pydantic** - Validation de données
- **OpenAI API** - Génération d'hypothèses via GPT-4
- **OAuth2** - Authentification QuickBooks Online

### Frontend (Futur)
- **React** 18+
- **TypeScript**
- **Recharts** - Graphiques interactifs
- **Axios** - Client HTTP

### Infrastructure
- **PostgreSQL** 15+ - Base de données relationnelle
- **Docker** - Containerisation
- **Docker Compose** - Orchestration locale

## 📦 Prochaines Fonctionnalités

Consultez la **Section 5** du document Google Docs pour la roadmap complète:

### Phase 1 (En cours)
- [x] Backend FastAPI avec endpoints de base
- [x] Modèles de données SQLAlchemy
- [x] Intégration QuickBooks Online
- [x] Service de projection financière
- [ ] Tests unitaires complets

### Phase 2 (Prochain)
- [ ] Interface frontend React
- [ ] Dashboard avec graphiques interactifs
- [ ] Intégration DEXT complète
- [ ] Export PDF/Excel des projections
- [ ] Authentification JWT

### Phase 3 (Futur)
- [ ] Notifications par email
- [ ] Webhooks pour événements
- [ ] Cache Redis pour performances
- [ ] Machine Learning pour prédictions améliorées
- [ ] CI/CD avec GitHub Actions

## 🤝 Contribution

Les contributions sont les bienvenues! Pour contribuer:

1. Fork le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Contact

**Groupe Regenord Inc.**
- Repository: [https://github.com/alainbeyonder/aia-regenord](https://github.com/alainbeyonder/aia-regenord)
- Documentation: [Google Docs](https://docs.google.com/document/d/1BkkW_QkMIhqabvljN2VQnP9XkAkizwlVNXoa0cXNUYk/edit)
- Issues: [GitHub Issues](https://github.com/alainbeyonder/aia-regenord/issues)

## ⭐ Remerciements

- QuickBooks Online pour leur API d'intégration
- OpenAI pour GPT-4
- La communauté FastAPI et Python

---

**📌 Note Importante**: Tous les fichiers sources avec leur code complet sont disponibles dans le [document Google Docs](https://docs.google.com/document/d/1BkkW_QkMIhqabvljN2VQnP9XkAkizwlVNXoa0cXNUYk/edit). Suivez le guide de création des fichiers ci-dessus pour mettre en place le projet complet.

Créé avec ❤️ pour Groupe Regenord Inc. | Version 1.0 | Janvier 2026


## 🔐 V1 Auth (API-only admin)

Admin approval is API-only (no admin UI). Use the seed script once to create the initial admin.

### Seed admin user

```bash
ADMIN_SEED_PASSWORD="YourStrongAdminPassword!" python3 scripts/seed_admin.py
```

Admin account:
- email: `admin@beyonders.tech`
- role: `admin`
- status: `active`

### Request access (public)

```bash
BASE="http://localhost:8000"

curl -X POST "$BASE/api/auth/request-access"   -H "Content-Type: application/json"   -d '{
    "company_name": "Regenord GROUP",
    "requester_name": "John Doe",
    "email": "john@example.com",
    "phone": "+1 506-000-0000",
    "message": "I want to test PDF mode."
  }'
```

### Admin login

```bash
curl -X POST "$BASE/api/auth/login"   -H "Content-Type: application/json"   -d '{
    "email": "admin@beyonders.tech",
    "password": "YourStrongAdminPassword!"
  }'
```

### Approve request (admin only)

```bash
curl -X POST "$BASE/api/auth/admin/approve-request"   -H "Authorization: Bearer YOUR_ADMIN_ACCESS_TOKEN"   -H "Content-Type: application/json"   -d '{
    "request_id": 1,
    "role": "client"
  }'
```

Response includes a `temp_password` (V1). Share it manually with the user.

### User sets a new password (first login)

```bash
curl -X POST "$BASE/api/auth/set-password"   -H "Authorization: Bearer USER_ACCESS_TOKEN"   -H "Content-Type: application/json"   -d '{
    "new_password": "MyNewStrongPassword123!"
  }'
```

## 📊 Assumptions V1 + Simulation Runs

Ces endpoints sont protégés par JWT et scoped par `company_id`.

### Create assumption set (draft)

```bash
curl -X POST "$BASE/api/aia/assumptions" \
  -H "Authorization: Bearer USER_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": 1,
    "name": "V1 Baseline",
    "scenario_key": "realistic",
    "payload_json": {
      "company_id": 1,
      "scenario_default": "realistic",
      "horizon": { "months_1": 12, "years_2_3": 2 }
    }
  }'
```

### List assumption sets

```bash
curl -X GET "$BASE/api/aia/assumptions?company_id=1" \
  -H "Authorization: Bearer USER_ACCESS_TOKEN"
```

### Get assumption set detail

```bash
curl -X GET "$BASE/api/aia/assumptions/1" \
  -H "Authorization: Bearer USER_ACCESS_TOKEN"
```

### Validate assumption set

```bash
curl -X POST "$BASE/api/aia/assumptions/1/validate" \
  -H "Authorization: Bearer USER_ACCESS_TOKEN"
```

### Run simulation (placeholder output)

```bash
curl -X POST "$BASE/api/aia/simulate" \
  -H "Authorization: Bearer USER_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": 1,
    "assumption_set_id": 1,
    "period_start": "2026-01-01",
    "horizon_months": 12,
    "horizon_years": 2
  }'
```

### List simulation runs

```bash
curl -X GET "$BASE/api/aia/runs?company_id=1" \
  -H "Authorization: Bearer USER_ACCESS_TOKEN"
```

### Get simulation run detail

```bash
curl -X GET "$BASE/api/aia/runs/1" \
  -H "Authorization: Bearer USER_ACCESS_TOKEN"
```

## 📄 PDF Analyze V1

Analyse des PDF QuickBooks (P&L + Balance Sheet) pour générer une vue client et une vue AIA.

### Analyze PDFs

```bash
curl -X POST "$BASE/api/aia/pdf/analyze" \
  -H "Authorization: Bearer USER_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": 1,
    "pl_upload_id": 10,
    "bs_upload_id": 11,
    "loans_upload_id": 12
  }'
```

### Latest analysis

```bash
curl -X GET "$BASE/api/aia/pdf/analysis/latest?company_id=1" \
  -H "Authorization: Bearer USER_ACCESS_TOKEN"
```
