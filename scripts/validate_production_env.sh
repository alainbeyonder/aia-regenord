#!/bin/bash

# Script de validation avancée de la configuration production
# Vérifie toutes les variables d'environnement et leur cohérence

echo "============================================"
echo "🔍 Validation Avancée - Configuration Production"
echo "============================================"
echo ""

ERRORS=0
WARNINGS=0

ENV_FILE="backend/.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Fichier $ENV_FILE non trouvé"
    exit 1
fi

# Source du fichier .env pour validation
set -a
source "$ENV_FILE"
set +a

echo "📋 1. Variables QuickBooks Online..."
echo ""

# QBO_ENVIRONMENT
if [ -z "$QBO_ENVIRONMENT" ]; then
    echo "   ❌ QBO_ENVIRONMENT non défini"
    ((ERRORS++))
elif [ "$QBO_ENVIRONMENT" != "production" ]; then
    echo "   ⚠️  QBO_ENVIRONMENT=$QBO_ENVIRONMENT (devrait être 'production')"
    ((WARNINGS++))
else
    echo "   ✅ QBO_ENVIRONMENT=$QBO_ENVIRONMENT"
fi

# QBO_CLIENT_ID
if [ -z "$QBO_CLIENT_ID" ]; then
    echo "   ❌ QBO_CLIENT_ID non défini"
    ((ERRORS++))
elif [ "$QBO_CLIENT_ID" != "ABhjTWUsPqScOqpWeCghMKHpx85MbL0fM9JQnt4uXpD4Wynk" ]; then
    echo "   ⚠️  QBO_CLIENT_ID ne correspond pas à la valeur attendue"
    ((WARNINGS++))
else
    echo "   ✅ QBO_CLIENT_ID configuré"
fi

# QBO_CLIENT_SECRET
if [ -z "$QBO_CLIENT_SECRET" ]; then
    echo "   ❌ QBO_CLIENT_SECRET non défini"
    ((ERRORS++))
elif [ "$QBO_CLIENT_SECRET" = "YOUR_CLIENT_SECRET_HERE" ] || [ "$QBO_CLIENT_SECRET" = "" ]; then
    echo "   ❌ QBO_CLIENT_SECRET n'est pas configuré correctement"
    ((ERRORS++))
else
    echo "   ✅ QBO_CLIENT_SECRET configuré"
fi

# QBO_REDIRECT_URI
EXPECTED_REDIRECT_URI="https://www.regenord.com/quickbooks-integration/callback"
if [ -z "$QBO_REDIRECT_URI" ]; then
    echo "   ❌ QBO_REDIRECT_URI non défini"
    ((ERRORS++))
elif [ "$QBO_REDIRECT_URI" != "$EXPECTED_REDIRECT_URI" ]; then
    echo "   ⚠️  QBO_REDIRECT_URI=$QBO_REDIRECT_URI"
    echo "      Attendu: $EXPECTED_REDIRECT_URI"
    ((WARNINGS++))
else
    echo "   ✅ QBO_REDIRECT_URI=$QBO_REDIRECT_URI"
fi

echo ""
echo "📋 2. Variables Application..."
echo ""

# APP_BASE_URL
if [ -z "$APP_BASE_URL" ]; then
    echo "   ❌ APP_BASE_URL non défini"
    ((ERRORS++))
elif [ "$APP_BASE_URL" != "https://api.regenord.com" ]; then
    echo "   ⚠️  APP_BASE_URL=$APP_BASE_URL (devrait être https://api.regenord.com)"
    ((WARNINGS++))
else
    echo "   ✅ APP_BASE_URL=$APP_BASE_URL"
fi

# FRONTEND_URL
if [ -z "$FRONTEND_URL" ]; then
    echo "   ⚠️  FRONTEND_URL non défini"
    ((WARNINGS++))
elif [ "$FRONTEND_URL" != "https://www.regenord.com" ]; then
    echo "   ⚠️  FRONTEND_URL=$FRONTEND_URL (devrait être https://www.regenord.com)"
    ((WARNINGS++))
else
    echo "   ✅ FRONTEND_URL=$FRONTEND_URL"
fi

# DEBUG
if [ "$DEBUG" = "True" ] || [ "$DEBUG" = "true" ]; then
    echo "   ⚠️  DEBUG=$DEBUG (devrait être False en production)"
    ((WARNINGS++))
else
    echo "   ✅ DEBUG=$DEBUG"
fi

echo ""
echo "📋 3. Variables de Sécurité..."
echo ""

# AIA_TOKEN_ENCRYPTION_KEY
if [ -z "$AIA_TOKEN_ENCRYPTION_KEY" ]; then
    echo "   ❌ AIA_TOKEN_ENCRYPTION_KEY non défini"
    ((ERRORS++))
elif [ "$AIA_TOKEN_ENCRYPTION_KEY" = "YOUR_FERNET_KEY_HERE" ]; then
    echo "   ❌ AIA_TOKEN_ENCRYPTION_KEY n'est pas généré"
    ((ERRORS++))
else
    # Vérifier le format Fernet (doit se terminer par =)
    if [[ "$AIA_TOKEN_ENCRYPTION_KEY" =~ =$ ]]; then
        echo "   ✅ AIA_TOKEN_ENCRYPTION_KEY généré (format correct)"
    else
        echo "   ⚠️  AIA_TOKEN_ENCRYPTION_KEY format suspect"
        ((WARNINGS++))
    fi
fi

# SECRET_KEY
if [ -z "$SECRET_KEY" ]; then
    echo "   ❌ SECRET_KEY non défini"
    ((ERRORS++))
elif [ "$SECRET_KEY" = "YOUR_SECRET_KEY_HERE" ] || [ "$SECRET_KEY" = "CHANGE_ME_TO_A_LONG_RANDOM_STRING" ]; then
    echo "   ❌ SECRET_KEY n'est pas généré"
    ((ERRORS++))
else
    # Vérifier la longueur minimale
    if [ ${#SECRET_KEY} -lt 32 ]; then
        echo "   ⚠️  SECRET_KEY semble trop court (${#SECRET_KEY} caractères)"
        ((WARNINGS++))
    else
        echo "   ✅ SECRET_KEY généré (${#SECRET_KEY} caractères)"
    fi
fi

echo ""
echo "📋 4. Variables Base de Données..."
echo ""

# DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    echo "   ❌ DATABASE_URL non défini"
    ((ERRORS++))
elif [ "$DATABASE_URL" = "postgresql://user:password@host:5432/aia_regenord" ]; then
    echo "   ❌ DATABASE_URL utilise des valeurs par défaut (doit être configuré)"
    ((ERRORS++))
elif [[ "$DATABASE_URL" =~ ^postgresql:// ]]; then
    echo "   ✅ DATABASE_URL configuré (format correct)"
else
    echo "   ⚠️  DATABASE_URL format suspect: $DATABASE_URL"
    ((WARNINGS++))
fi

echo ""
echo "📋 5. Variables CORS..."
echo ""

# CORS_ORIGINS
if [ -z "$CORS_ORIGINS" ]; then
    echo "   ⚠️  CORS_ORIGINS non défini (utilisera les valeurs par défaut)"
    ((WARNINGS++))
elif [[ "$CORS_ORIGINS" =~ "https://www.regenord.com" ]]; then
    echo "   ✅ CORS_ORIGINS inclut https://www.regenord.com"
else
    echo "   ⚠️  CORS_ORIGINS ne contient pas https://www.regenord.com"
    echo "      Valeur actuelle: $CORS_ORIGINS"
    ((WARNINGS++))
fi

echo ""
echo "============================================"
echo "📊 Résumé de Validation"
echo "============================================"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "✅ Configuration parfaite! Toutes les validations sont passées."
    echo ""
    echo "🚀 Vous êtes prêt pour le déploiement!"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo "⚠️  Configuration valide avec $WARNINGS avertissement(s)"
    echo ""
    echo "🔧 Actions recommandées:"
    echo "   - Vérifier les avertissements ci-dessus"
    echo "   - Les avertissements n'empêchent pas le déploiement"
    exit 0
else
    echo "❌ Configuration incomplète: $ERRORS erreur(s), $WARNINGS avertissement(s)"
    echo ""
    echo "🔧 Actions requises:"
    echo "   - Corriger les erreurs ci-dessus avant de déployer"
    exit 1
fi
