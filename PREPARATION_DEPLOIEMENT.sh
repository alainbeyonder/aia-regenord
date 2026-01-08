#!/bin/bash

# Script pour préparer le projet pour le déploiement Railway/Render
# Usage: ./PREPARATION_DEPLOIEMENT.sh

echo "============================================"
echo "🔧 Préparation pour Déploiement Railway/Render"
echo "============================================"
echo ""

# Vérifier que .gitignore existe
if [ ! -f ".gitignore" ]; then
    echo "📝 Création du fichier .gitignore..."
    cat > .gitignore << 'EOF'
# Environnement
.env
.env.*
*.env
backend/.env
backend/.env.*
!backend/.env.example

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv/

# Logs
*.log
logs/
backend/logs/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Build
dist/
build/
*.egg-info/

# PIDs
*.pid
backend.pid
frontend.pid

# Temporary files
*.tmp
*.temp
*.bak
EOF
    echo "✅ .gitignore créé"
else
    echo "✅ .gitignore existe déjà"
fi

echo ""

# Vérifier que .env n'est pas dans Git
echo "🔍 Vérification de la sécurité Git..."
if git ls-files | grep -q "\.env$"; then
    echo "⚠️  ATTENTION: .env est tracké par Git!"
    echo "   Exécuter: git rm --cached backend/.env"
    echo "   Puis: git commit -m 'Remove .env from tracking'"
else
    echo "✅ .env n'est pas tracké par Git (sécurisé)"
fi

echo ""

# Vérifier les fichiers nécessaires
echo "📋 Vérification des fichiers nécessaires..."
MISSING=0

if [ ! -f "backend/requirements.txt" ]; then
    echo "❌ backend/requirements.txt manquant"
    MISSING=1
else
    echo "✅ backend/requirements.txt"
fi

if [ ! -f "backend/Dockerfile" ]; then
    echo "❌ backend/Dockerfile manquant"
    MISSING=1
else
    echo "✅ backend/Dockerfile"
fi

if [ ! -f "backend/app/main.py" ]; then
    echo "❌ backend/app/main.py manquant"
    MISSING=1
else
    echo "✅ backend/app/main.py"
fi

echo ""

# Vérifier la configuration
echo "🔍 Vérification de la configuration backend/.env..."
if [ -f "backend/.env" ]; then
    echo "✅ backend/.env existe"
    
    if grep -q "QBO_ENVIRONMENT=production" backend/.env; then
        echo "✅ QBO_ENVIRONMENT=production"
    else
        echo "⚠️  QBO_ENVIRONMENT n'est pas en production"
    fi
    
    if grep -q "APP_BASE_URL=https://api.regenord.com" backend/.env; then
        echo "✅ APP_BASE_URL configuré"
    else
        echo "⚠️  APP_BASE_URL peut ne pas être correct pour Railway/Render"
        echo "   Note: Railway/Render donneront leur propre URL"
    fi
    
    if grep -q "DATABASE_URL=" backend/.env && ! grep -q "DATABASE_URL=postgresql://user:password@host" backend/.env; then
        echo "✅ DATABASE_URL configuré"
    else
        echo "⚠️  DATABASE_URL doit être configuré par Railway/Render"
        echo "   Railway/Render ajouteront automatiquement DATABASE_URL"
    fi
else
    echo "⚠️  backend/.env n'existe pas"
    echo "   Créer avec les variables nécessaires"
fi

echo ""

# Créer un fichier .env.example pour référence
echo "📝 Création de backend/.env.example..."
cat > backend/.env.example << 'EOF'
# ============================================
# Configuration Backend - PRODUCTION
# Copier vers .env et remplir les valeurs
# ⚠️ NE JAMAIS COMMITTER .env dans Git!
# ============================================

# QuickBooks Online - PRODUCTION
QBO_ENVIRONMENT=production
QBO_CLIENT_ID=YOUR_CLIENT_ID
QBO_CLIENT_SECRET=YOUR_CLIENT_SECRET
QBO_REDIRECT_URI=https://www.regenord.com/quickbooks-integration/callback

# Application
APP_NAME=AIA Regenord
APP_ENV=production
DEBUG=False
APP_BASE_URL=https://YOUR_RAILWAY_OR_RENDER_URL
FRONTEND_URL=https://www.regenord.com

# Sécurité (GÉNÉRER avec: python3 scripts/generate_security_keys.py)
AIA_TOKEN_ENCRYPTION_KEY=YOUR_FERNET_KEY
SECRET_KEY=YOUR_SECRET_KEY

# Base de données (SERA CONFIGURÉ PAR RAILWAY/RENDER)
DATABASE_URL=postgresql://user:password@host:5432/database

# CORS
CORS_ORIGINS=["https://www.regenord.com"]

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/aia-regenord.log
EOF

echo "✅ backend/.env.example créé"

echo ""
echo "============================================"
echo "📊 Résumé"
echo "============================================"
echo ""

if [ $MISSING -eq 0 ]; then
    echo "✅ Tous les fichiers nécessaires sont présents"
    echo ""
    echo "🚀 Prochaines étapes:"
    echo ""
    echo "1. Initialiser Git (si pas déjà fait):"
    echo "   git init"
    echo "   git add ."
    echo "   git commit -m 'Initial commit'"
    echo ""
    echo "2. Créer un repository GitHub:"
    echo "   https://github.com/new"
    echo ""
    echo "3. Pousser le code:"
    echo "   git remote add origin https://github.com/VOTRE_USERNAME/aia-regenord.git"
    echo "   git push -u origin main"
    echo ""
    echo "4. Déployer sur Railway ou Render:"
    echo "   → Voir DEPLOIEMENT_RAILWAY_RENDER.md"
    echo ""
    echo "✅ Projet prêt pour le déploiement!"
else
    echo "❌ Certains fichiers sont manquants"
    echo "   Corriger les erreurs ci-dessus"
    exit 1
fi
