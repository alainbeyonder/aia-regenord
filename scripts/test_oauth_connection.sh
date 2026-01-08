#!/bin/bash

# Script de test pour vérifier la connexion OAuth après injection Squarespace
# Usage: ./scripts/test_oauth_connection.sh

BACKEND_URL="https://api.regenord.com"
COMPANY_ID=1
PAGE_URL="https://www.regenord.com/quickbooks-integration"

echo "============================================"
echo "🧪 Test de Connexion OAuth - Production"
echo "============================================"
echo ""

ERRORS=0

# Test 1: Backend accessible
echo "📋 1. Test d'accessibilité du backend..."
if curl -s --max-time 5 "${BACKEND_URL}/api/health" > /dev/null 2>&1; then
    echo "   ✅ Backend accessible: ${BACKEND_URL}"
else
    echo "   ❌ Backend non accessible: ${BACKEND_URL}"
    echo "      Vérifiez que le backend est déployé et en cours d'exécution"
    ((ERRORS++))
fi

echo ""

# Test 2: Configuration QBO
echo "📋 2. Test de configuration QuickBooks..."
CONFIG_RESPONSE=$(curl -s --max-time 5 "${BACKEND_URL}/api/qbo/config/check" 2>&1)
if echo "$CONFIG_RESPONSE" | grep -q "production"; then
    echo "   ✅ Configuration QBO détectée (production)"
    if echo "$CONFIG_RESPONSE" | grep -q "\"status\":\"ok\""; then
        echo "   ✅ Configuration QBO complète"
    else
        echo "   ⚠️  Configuration QBO incomplète"
        echo "      Vérifiez backend/.env"
        ((ERRORS++))
    fi
else
    echo "   ❌ Impossible de vérifier la configuration QBO"
    echo "      Réponse: ${CONFIG_RESPONSE:0:100}..."
    ((ERRORS++))
fi

echo ""

# Test 3: Statut de connexion
echo "📋 3. Test du statut de connexion..."
STATUS_RESPONSE=$(curl -s --max-time 5 "${BACKEND_URL}/api/qbo/status?company_id=${COMPANY_ID}" 2>&1)
if echo "$STATUS_RESPONSE" | grep -q "connected"; then
    if echo "$STATUS_RESPONSE" | grep -q "\"connected\":true"; then
        echo "   ✅ QuickBooks est connecté"
        REALM_ID=$(echo "$STATUS_RESPONSE" | grep -o '"realm_id":"[^"]*"' | cut -d'"' -f4)
        if [ -n "$REALM_ID" ]; then
            echo "      Realm ID: ${REALM_ID}"
        fi
    else
        echo "   ⏳ QuickBooks non connecté (normal si première connexion)"
    fi
else
    echo "   ⚠️  Impossible de vérifier le statut"
    echo "      Réponse: ${STATUS_RESPONSE:0:100}..."
fi

echo ""

# Test 4: Page Squarespace accessible
echo "📋 4. Test d'accessibilité de la page Squarespace..."
if curl -s --max-time 10 "${PAGE_URL}" | grep -q "QuickBooks\|quickbooks" 2>/dev/null; then
    echo "   ✅ Page Squarespace accessible"
    echo "      URL: ${PAGE_URL}"
else
    echo "   ⚠️  Page Squarespace peut ne pas être accessible ou code non injecté"
    echo "      Vérifiez que le code est injecté dans Squarespace"
fi

echo ""

# Test 5: Vérification Redirect URI
echo "📋 5. Vérification Redirect URI..."
EXPECTED_REDIRECT_URI="https://www.regenord.com/quickbooks-integration/callback"
if [ -f "backend/.env" ]; then
    ENV_REDIRECT=$(grep "QBO_REDIRECT_URI" backend/.env | cut -d'=' -f2)
    if [ "$ENV_REDIRECT" == "$EXPECTED_REDIRECT_URI" ]; then
        echo "   ✅ Redirect URI correct dans backend/.env"
        echo "      ${EXPECTED_REDIRECT_URI}"
    else
        echo "   ⚠️  Redirect URI peut être incorrect"
        echo "      Attendu: ${EXPECTED_REDIRECT_URI}"
        echo "      Trouvé: ${ENV_REDIRECT}"
    fi
else
    echo "   ⚠️  backend/.env non trouvé"
fi

echo ""
echo "============================================"
echo "📊 Résumé"
echo "============================================"
echo ""

if [ $ERRORS -eq 0 ]; then
    echo "✅ Tous les tests de base sont passés!"
    echo ""
    echo "🚀 Prochaines étapes:"
    echo "   1. Aller sur: ${PAGE_URL}"
    echo "   2. Vérifier que l'interface s'affiche"
    echo "   3. Cliquer sur 'Connecter QuickBooks'"
    echo "   4. Autoriser l'accès dans Intuit"
    echo "   5. Vérifier le retour sur la page avec message de succès"
    echo ""
    echo "💡 Si vous rencontrez des problèmes:"
    echo "   - Vérifiez la console du navigateur (F12)"
    echo "   - Vérifiez les logs du backend"
    echo "   - Vérifiez que le Redirect URI est configuré dans Intuit Developer"
    exit 0
else
    echo "⚠️  ${ERRORS} erreur(s) détectée(s)"
    echo ""
    echo "🔧 Actions requises:"
    echo "   - Corriger les erreurs ci-dessus"
    echo "   - Relancer ce script pour vérifier"
    exit 1
fi
