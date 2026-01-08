#!/bin/bash
# Script de vérification de la configuration QBO

echo "🔍 Vérification de la configuration QuickBooks Online"
echo "=================================================="
echo ""

API_URL="${API_URL:-http://localhost:8000}"

# Vérifier que l'API répond
echo "1. Vérification de l'API..."
if curl -s "${API_URL}/health" > /dev/null 2>&1; then
    echo "   ✅ API accessible"
else
    echo "   ❌ API non accessible à ${API_URL}"
    echo "   Assurez-vous que le backend est démarré"
    exit 1
fi

# Vérifier la configuration
echo ""
echo "2. Vérification de la configuration QBO..."
CONFIG=$(curl -s "${API_URL}/api/qbo/config/check")

ENV=$(echo "$CONFIG" | python3 -c "import sys, json; print(json.load(sys.stdin)['configuration']['environment'])" 2>/dev/null)
STATUS=$(echo "$CONFIG" | python3 -c "import sys, json; print(json.load(sys.stdin)['configuration']['status'])" 2>/dev/null)

if [ "$STATUS" = "ok" ]; then
    echo "   ✅ Configuration complète"
    echo "   📊 Environnement: $ENV"
    
    if [ "$ENV" = "sandbox" ]; then
        echo "   ℹ️  Mode Sandbox activé (prêt pour les tests)"
    elif [ "$ENV" = "production" ]; then
        echo "   ⚠️  Mode Production activé"
    fi
else
    echo "   ❌ Configuration incomplète"
    echo "   Détails:"
    echo "$CONFIG" | python3 -m json.tool 2>/dev/null || echo "$CONFIG"
    exit 1
fi

# Vérifier le statut de connexion
echo ""
echo "3. Vérification de la connexion QBO (company_id=1)..."
STATUS_RESPONSE=$(curl -s "${API_URL}/api/qbo/status?company_id=1")

CONNECTED=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('connected', False))" 2>/dev/null)

if [ "$CONNECTED" = "True" ]; then
    REALM_ID=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('realm_id', 'N/A'))" 2>/dev/null)
    echo "   ✅ Connecté à QuickBooks"
    echo "   📋 Realm ID: $REALM_ID"
else
    echo "   ⚠️  Non connecté à QuickBooks"
    echo "   Utilisez le bouton 'Connecter QBO' dans l'interface"
fi

echo ""
echo "=================================================="
echo "✅ Vérification terminée"
echo ""
echo "Prochaines étapes:"
if [ "$CONNECTED" != "True" ]; then
    echo "1. Connecter QuickBooks: http://localhost:3000"
fi
echo "2. Tester la synchronisation"
echo "3. Vérifier les données: http://localhost:3000 (Voir Vue QBO)"
echo "4. Vérifier la vue AIA: http://localhost:3000 (Voir Vue AIA)"
