#!/bin/bash
# Script de test complet pour le sandbox QBO

API_URL="${API_URL:-http://localhost:8000}"

echo "🧪 TESTS SANDBOX QUICKBOOKS ONLINE"
echo "===================================="
echo ""

# Test 1: Configuration
echo "1️⃣  Vérification de la configuration..."
CONFIG=$(curl -s "${API_URL}/api/qbo/config/check")
echo "$CONFIG" | python3 -c "
import sys, json
data = json.load(sys.stdin)
config = data['configuration']
print(f\"   Environnement: {config['environment']}\")
print(f\"   Client ID configuré: {'✅' if config['client_id_configured'] else '❌'}\")
print(f\"   Client Secret configuré: {'✅' if config['client_secret_configured'] else '❌'}\")
print(f\"   Redirect URI: {config['redirect_uri']}\")
print(f\"   Statut: {'✅ OK' if config['status'] == 'ok' else '❌ Incomplet'}\")
"

# Test 2: Statut connexion
echo ""
echo "2️⃣  Vérification du statut de connexion QBO..."
STATUS=$(curl -s "${API_URL}/api/qbo/status?company_id=1")
echo "$STATUS" | python3 -c "
import sys, json
data = json.load(sys.stdin)
connected = data.get('connected', False)
if connected:
    print(f\"   ✅ Connecté à QuickBooks\")
    print(f\"   📋 Realm ID: {data.get('realm_id', 'N/A')}\")
else:
    print(f\"   ❌ Non connecté - Ouvrir http://localhost:3000 et cliquer sur 'Connecter QBO'\")
"

# Test 3: Santé API
echo ""
echo "3️⃣  Vérification de la santé de l'API..."
HEALTH=$(curl -s "${API_URL}/health")
if echo "$HEALTH" | grep -q "healthy"; then
    echo "   ✅ API: healthy"
else
    echo "   ❌ API non accessible"
fi

# Test 4: Données QBO
echo ""
echo "4️⃣  Test de récupération des données QBO..."
QBO_DATA=$(curl -s "${API_URL}/api/qbo/data?company_id=1&months=12")
if echo "$QBO_DATA" | grep -q "statistics"; then
    echo "$QBO_DATA" | python3 -c "
import sys, json
data = json.load(sys.stdin)
stats = data.get('statistics', {})
anomalies = data.get('anomalies', {}).get('summary', {})
print(f\"   ✅ Données récupérées\")
print(f\"   📊 Comptes: {stats.get('total_accounts', 0)} ({stats.get('active_accounts', 0)} actifs)\")
print(f\"   📊 Transactions: {stats.get('total_transactions', 0)}\")
print(f\"   📊 Snapshots: {stats.get('total_snapshots', 0)}\")
print(f\"   ⚠️  Anomalies: {anomalies.get('critical_count', 0)} critiques, {anomalies.get('warning_count', 0)} avertissements\")
" 2>/dev/null || echo "   ⚠️  Données vides ou erreur"
else
    echo "   ⚠️  Erreur lors de la récupération"
    echo "$QBO_DATA" | head -1
fi

# Test 5: Vue AIA
echo ""
echo "5️⃣  Test de la vue financière AIA..."
AIA_VIEW=$(curl -s "${API_URL}/api/aia/view?company_id=1&months=12")
if echo "$AIA_VIEW" | grep -q "totals_by_category"; then
    echo "$AIA_VIEW" | python3 -c "
import sys, json
data = json.load(sys.stdin)
totals = data.get('totals_by_category', {})
reconciliation = data.get('reconciliation', {})
print(f\"   ✅ Vue AIA générée\")
print(f\"   📈 Catégories: {len(totals)}\")
print(f\"   💰 Réconciliation: QBO=${reconciliation.get('total_qbo', 0):,.2f}, AIA=${reconciliation.get('total_aia', 0):,.2f}\")
print(f\"   Statut: {'✅ Réconcilié' if reconciliation.get('reconciled', False) else '⚠️  Écart'}\")
" 2>/dev/null || echo "   ⚠️  Erreur lors de la génération"
else
    echo "   ❌ Erreur lors de la génération"
fi

# Test 6: Export CSV
echo ""
echo "6️⃣  Test de l'export CSV..."
curl -s "${API_URL}/api/aia/export/google-sheets?company_id=1&months=12&format=csv" -o /tmp/test_export.csv > /dev/null 2>&1
if [ -s /tmp/test_export.csv ]; then
    LINES=$(wc -l < /tmp/test_export.csv)
    echo "   ✅ Export CSV généré: $LINES lignes"
else
    echo "   ⚠️  Export CSV vide"
fi

# Test 7: Frontend
echo ""
echo "7️⃣  Vérification du frontend..."
if curl -s "http://localhost:3000" > /dev/null 2>&1; then
    echo "   ✅ Frontend accessible sur http://localhost:3000"
else
    echo "   ⚠️  Frontend non accessible"
fi

echo ""
echo "===================================="
echo "✅ Tests terminés!"
echo ""
echo "Pour tester manuellement:"
echo "1. Interface: http://localhost:3000"
echo "2. API Docs: ${API_URL}/docs"
echo ""
