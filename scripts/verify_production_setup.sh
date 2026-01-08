#!/bin/bash

# Script de vérification de la configuration production
# Usage: ./scripts/verify_production_setup.sh

echo "============================================"
echo "🔍 Vérification Configuration Production"
echo "============================================"
echo ""

ERRORS=0
WARNINGS=0

# 1. Vérifier backend/.env
echo "📋 1. Vérification backend/.env..."
if [ -f "backend/.env" ]; then
    echo "   ✅ Fichier backend/.env existe"
    
    # Vérifier les clés essentielles
    if grep -q "QBO_CLIENT_ID=ABhjTWUsPqScOqpWeCghMKHpx85MbL0fM9JQnt4uXpD4Wynk" backend/.env; then
        echo "   ✅ QBO_CLIENT_ID configuré"
    else
        echo "   ❌ QBO_CLIENT_ID non trouvé ou incorrect"
        ((ERRORS++))
    fi
    
    if grep -q "APP_BASE_URL=https://api.regenord.com" backend/.env; then
        echo "   ✅ APP_BASE_URL configuré"
    else
        echo "   ⚠️  APP_BASE_URL non configuré correctement"
        ((WARNINGS++))
    fi
    
    if grep -q "AIA_TOKEN_ENCRYPTION_KEY=" backend/.env && ! grep -q "AIA_TOKEN_ENCRYPTION_KEY=YOUR_FERNET_KEY_HERE" backend/.env; then
        echo "   ✅ AIA_TOKEN_ENCRYPTION_KEY générée"
    else
        echo "   ❌ AIA_TOKEN_ENCRYPTION_KEY non générée"
        ((ERRORS++))
    fi
    
    if grep -q "SECRET_KEY=" backend/.env && ! grep -q "SECRET_KEY=YOUR_SECRET_KEY_HERE" backend/.env; then
        echo "   ✅ SECRET_KEY générée"
    else
        echo "   ❌ SECRET_KEY non générée"
        ((ERRORS++))
    fi
    
    if grep -q "DATABASE_URL=postgresql://" backend/.env && ! grep -q "DATABASE_URL=postgresql://user:password@host:5432/aia_regenord" backend/.env; then
        echo "   ✅ DATABASE_URL configuré"
    else
        echo "   ⚠️  DATABASE_URL doit être configuré avec vos credentials PostgreSQL"
        ((WARNINGS++))
    fi
else
    echo "   ❌ Fichier backend/.env n'existe pas"
    ((ERRORS++))
fi

echo ""

# 2. Vérifier code Squarespace
echo "📋 2. Vérification code Squarespace..."
if [ -f "SQUARESPACE_CODE_INJECTION_READY.html" ]; then
    echo "   ✅ Fichier SQUARESPACE_CODE_INJECTION_READY.html existe"
    
    if grep -q "const BACKEND_URL = 'https://api.regenord.com';" SQUARESPACE_CODE_INJECTION_READY.html; then
        echo "   ✅ BACKEND_URL configuré correctement"
    else
        echo "   ⚠️  BACKEND_URL peut ne pas être correct"
        ((WARNINGS++))
    fi
else
    echo "   ❌ Fichier SQUARESPACE_CODE_INJECTION_READY.html n'existe pas"
    ((ERRORS++))
fi

echo ""

# 3. Vérifier Redirect URI
echo "📋 3. Vérification Redirect URI..."
if [ -f "backend/.env" ]; then
    if grep -q "QBO_REDIRECT_URI=https://www.regenord.com/quickbooks-integration/callback" backend/.env; then
        echo "   ✅ QBO_REDIRECT_URI configuré correctement"
    else
        echo "   ⚠️  QBO_REDIRECT_URI peut ne pas être correct"
        ((WARNINGS++))
    fi
fi

echo ""

# 4. Vérifier que .env n'est pas dans Git
echo "📋 4. Vérification sécurité Git..."
if [ -f ".gitignore" ]; then
    if grep -q "backend/.env" .gitignore || grep -q "^\.env" .gitignore; then
        echo "   ✅ backend/.env est dans .gitignore"
    else
        echo "   ⚠️  backend/.env n'est peut-être pas dans .gitignore"
        ((WARNINGS++))
    fi
else
    echo "   ⚠️  Fichier .gitignore non trouvé"
    ((WARNINGS++))
fi

echo ""

# Résumé
echo "============================================"
echo "📊 Résumé"
echo "============================================"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "✅ Configuration parfaite! Tout est prêt."
    echo ""
    echo "🚀 Prochaines étapes:"
    echo "   1. Configurer DATABASE_URL dans backend/.env (si pas déjà fait)"
    echo "   2. Injecter SQUARESPACE_CODE_INJECTION_READY.html dans Squarespace"
    echo "   3. Tester la connexion OAuth sur https://www.regenord.com/quickbooks-integration"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo "⚠️  Configuration presque complète avec $WARNINGS avertissement(s)"
    echo ""
    echo "🔧 Actions recommandées:"
    if [ $WARNINGS -gt 0 ]; then
        echo "   - Vérifier les avertissements ci-dessus"
    fi
    exit 0
else
    echo "❌ Configuration incomplète: $ERRORS erreur(s), $WARNINGS avertissement(s)"
    echo ""
    echo "🔧 Actions requises:"
    echo "   - Corriger les erreurs ci-dessus"
    exit 1
fi
