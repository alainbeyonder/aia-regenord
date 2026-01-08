#!/bin/bash

# Script pour tester la configuration production

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_ENV="$PROJECT_ROOT/backend/.env"

echo "=========================================="
echo "🧪 Test Configuration Production"
echo "=========================================="
echo ""

# Vérifier si .env existe
if [ ! -f "$BACKEND_ENV" ]; then
    echo "❌ Le fichier backend/.env n'existe pas!"
    echo "   Exécutez d'abord: ./scripts/setup_production_env.sh"
    exit 1
fi

# Extraire les variables
BACKEND_URL=$(grep "^APP_BASE_URL=" "$BACKEND_ENV" | cut -d'=' -f2 | sed 's/^"//;s/"$//' || echo "")
QBO_ENV=$(grep "^QBO_ENVIRONMENT=" "$BACKEND_ENV" | cut -d'=' -f2 || echo "")
CLIENT_ID=$(grep "^QBO_CLIENT_ID=" "$BACKEND_ENV" | cut -d'=' -f2 || echo "")
REDIRECT_URI=$(grep "^QBO_REDIRECT_URI=" "$BACKEND_ENV" | cut -d'=' -f2 || echo "")
FERNET_KEY=$(grep "^AIA_TOKEN_ENCRYPTION_KEY=" "$BACKEND_ENV" | cut -d'=' -f2 || echo "")
SECRET_KEY=$(grep "^SECRET_KEY=" "$BACKEND_ENV" | cut -d'=' -f2 || echo "")

echo "📋 Vérification des variables d'environnement:"
echo ""

ERRORS=0

# Vérifier BACKEND_URL
if [ -z "$BACKEND_URL" ] || [ "$BACKEND_URL" = "YOUR_BACKEND_URL" ]; then
    echo "❌ APP_BASE_URL non configuré ou utilise la valeur par défaut"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ APP_BASE_URL: $BACKEND_URL"
fi

# Vérifier QBO_ENVIRONMENT
if [ "$QBO_ENV" != "production" ]; then
    echo "⚠️  QBO_ENVIRONMENT n'est pas 'production': $QBO_ENV"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ QBO_ENVIRONMENT: $QBO_ENV"
fi

# Vérifier CLIENT_ID
if [ -z "$CLIENT_ID" ] || [ "$CLIENT_ID" != "ABhjTWUsPqScOqpWeCghMKHpx85MbL0fM9JQnt4uXpD4Wynk" ]; then
    echo "⚠️  QBO_CLIENT_ID ne correspond pas aux credentials production"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ QBO_CLIENT_ID: configuré"
fi

# Vérifier REDIRECT_URI
if [ "$REDIRECT_URI" != "https://www.regenord.com/quickbooks-integration/callback" ]; then
    echo "⚠️  QBO_REDIRECT_URI incorrect: $REDIRECT_URI"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ QBO_REDIRECT_URI: $REDIRECT_URI"
fi

# Vérifier FERNET_KEY
if [ -z "$FERNET_KEY" ] || [ "$FERNET_KEY" = "YOUR_FERNET_KEY_HERE" ]; then
    echo "❌ AIA_TOKEN_ENCRYPTION_KEY non configuré"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ AIA_TOKEN_ENCRYPTION_KEY: configuré (${#FERNET_KEY} caractères)"
fi

# Vérifier SECRET_KEY
if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "YOUR_SECRET_KEY_HERE" ]; then
    echo "❌ SECRET_KEY non configuré"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ SECRET_KEY: configuré (${#SECRET_KEY} caractères)"
fi

echo ""
echo "=========================================="

if [ $ERRORS -eq 0 ]; then
    echo "✅ Configuration OK!"
    echo ""
    
    # Tester si le backend est accessible
    if [ -n "$BACKEND_URL" ]; then
        echo "🔍 Test de connectivité au backend..."
        if curl -s -f "${BACKEND_URL}/api/qbo/config/check" > /dev/null 2>&1; then
            echo "✅ Backend accessible: $BACKEND_URL"
            echo ""
            echo "📊 Configuration QBO:"
            curl -s "${BACKEND_URL}/api/qbo/config/check" | python3 -m json.tool 2>/dev/null || curl -s "${BACKEND_URL}/api/qbo/config/check"
        else
            echo "⚠️  Backend non accessible à: $BACKEND_URL"
            echo "   Vérifiez que le backend est déployé et en cours d'exécution"
        fi
    fi
else
    echo "❌ Configuration incomplète ($ERRORS erreur(s))"
    echo ""
    echo "📝 Actions à prendre:"
    echo "   1. Exécuter: ./scripts/setup_production_env.sh"
    echo "   2. Vérifier backend/.env"
    exit 1
fi
