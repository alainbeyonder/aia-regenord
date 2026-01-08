#!/bin/bash
# Script pour afficher les résultats de synchronisation QBO

API_URL="${API_URL:-http://localhost:8000}"
COMPANY_ID=1
MONTHS=12

echo "📊 RAPPORT DÉTAILLÉ - QUICKBOOKS ONLINE SANDBOX"
echo "================================================"
echo ""

# 1. Statut de connexion
echo "1️⃣  STATUT DE CONNEXION"
echo "----------------------"
curl -s "${API_URL}/api/qbo/status?company_id=${COMPANY_ID}" | python3 << 'EOF'
import sys, json
data = json.load(sys.stdin)
print(f"   Connecté: {'✅ Oui' if data.get('connected') else '❌ Non'}")
if data.get('connected'):
    print(f"   Realm ID: {data.get('realm_id', 'N/A')}")
    print(f"   Dernière sync: {data.get('last_sync_at', 'N/A')}")
    print(f"   Token expire: {data.get('token_expires_at', 'N/A')}")
EOF
echo ""

# 2. Statistiques générales
echo "2️⃣  STATISTIQUES GÉNÉRALES"
echo "----------------------"
curl -s "${API_URL}/api/qbo/data?company_id=${COMPANY_ID}&months=${MONTHS}" | python3 << 'EOF'
import sys, json
data = json.load(sys.stdin)
stats = data.get("statistics", {})
print(f"   Comptes: {stats.get('total_accounts', 0)} ({stats.get('active_accounts', 0)} actifs, {stats.get('inactive_accounts', 0)} inactifs)")
print(f"   Transactions: {stats.get('total_transactions', 0)}")
print(f"   Snapshots: {stats.get('total_snapshots', 0)}")
print(f"   Période: {stats.get('period_start', 'N/A')} à {stats.get('period_end', 'N/A')}")
print(f"   Montant total: ${stats.get('total_amount', 0):,.2f}")
print(f"   Transactions positives: {stats.get('positive_amounts', 0)}")
print(f"   Transactions négatives: {stats.get('negative_amounts', 0)}")
EOF
echo ""

# 3. Comptes (premiers 20)
echo "3️⃣  COMPTES QBO (premiers 20)"
echo "----------------------"
curl -s "${API_URL}/api/qbo/data?company_id=${COMPANY_ID}&months=${MONTHS}" | python3 << 'EOF'
import sys, json
data = json.load(sys.stdin)
accounts = data.get("accounts", [])[:20]
print(f"   Total comptes: {len(data.get('accounts', []))}")
print("")
print("   Nom | Type | Sous-type | Statut")
print("   " + "-" * 70)
for acc in accounts:
    name = acc.get("name", "N/A")[:30]
    a_type = acc.get("account_type", "-") or "-"
    a_subtype = acc.get("account_subtype", "-") or "-"
    status = "✅ Actif" if acc.get("active", True) else "❌ Inactif"
    print(f"   {name:<30} | {a_type:<15} | {a_subtype:<20} | {status}")
EOF
echo ""

# 4. Transactions récentes
echo "4️⃣  TRANSACTIONS RÉCENTES (10 dernières)"
echo "----------------------"
curl -s "${API_URL}/api/qbo/data?company_id=${COMPANY_ID}&months=${MONTHS}" | python3 << 'EOF'
import sys, json
from datetime import datetime

data = json.load(sys.stdin)
transactions = data.get("transactions", [])[:10]
print(f"   Total transactions: {len(data.get('transactions', []))}")
print("")
print("   Date | Type | Montant | Contrepartie")
print("   " + "-" * 80)

for txn in transactions:
    date_str = txn.get("txn_date", "N/A")
    try:
        date_obj = datetime.fromisoformat(date_str)
        date_display = date_obj.strftime("%Y-%m-%d")
    except:
        date_display = date_str[:10]
    
    txn_type = (txn.get("txn_type", "-") or "-")[:15]
    amount = txn.get("amount", 0)
    amount_str = f"${abs(amount):,.2f}"
    if amount < 0:
        amount_str = f"-{amount_str}"
    elif amount > 0:
        amount_str = f"+{amount_str}"
    
    counterparty = (txn.get("counterparty", "-") or "-")[:25]
    print(f"   {date_display} | {txn_type:<15} | {amount_str:>12} | {counterparty}")
EOF
echo ""

# 5. Vue financière AIA
echo "5️⃣  VUE FINANCIÈRE AIA"
echo "----------------------"
curl -s "${API_URL}/api/aia/view?company_id=${COMPANY_ID}&months=${MONTHS}" | python3 << 'EOF'
import sys, json
data = json.load(sys.stdin)
totals = data.get("totals_by_category", {})
reconciliation = data.get("reconciliation", {})

print(f"   Période: {data.get('period_start')} à {data.get('period_end')}")
print(f"   Source: {data.get('data_source', 'N/A')}")
print(f"   Catégories: {len(totals)}")
print("")
print("   Réconciliation:")
print(f"      Total QBO: ${reconciliation.get('total_qbo', 0):,.2f}")
print(f"      Total AIA: ${reconciliation.get('total_aia', 0):,.2f}")
print(f"      Delta: ${reconciliation.get('delta', 0):,.2f}")
print(f"      Statut: {'✅ Réconcilié' if reconciliation.get('reconciled', False) else '⚠️  Écart'}")
print("")

# Catégories avec montants
categories_with_amounts = [(k, v) for k, v in totals.items() if abs(v.get('total', 0)) > 0.01]
if categories_with_amounts:
    print("   Catégories avec montants:")
    print("   " + "-" * 70)
    print("   Nom | Total | Confiance | Comptes")
    print("   " + "-" * 70)
    for key, cat in sorted(categories_with_amounts, key=lambda x: abs(x[1].get('total', 0)), reverse=True):
        name = cat.get('name', key)[:40]
        total = cat.get('total', 0)
        confidence = cat.get('confidence_score', 0)
        count = cat.get('accounts_count', 0)
        print(f"   {name:<40} | ${total:>12,.2f} | {confidence:>8.2f} | {count:>7}")
else:
    print("   ℹ️  Aucune catégorie avec montants (données vides)")
EOF
echo ""

# 6. Anomalies détectées
echo "6️⃣  ANALYSE D'ANOMALIES"
echo "----------------------"
curl -s "${API_URL}/api/qbo/data?company_id=${COMPANY_ID}&months=${MONTHS}" | python3 << 'EOF'
import sys, json
data = json.load(sys.stdin)
anomalies = data.get("anomalies", {})
summary = anomalies.get("summary", {})

print(f"   Total: {summary.get('total', 0)} anomalies détectées")
print(f"   🔴 Critiques: {summary.get('critical_count', 0)}")
print(f"   🟡 Avertissements: {summary.get('warning_count', 0)}")
print(f"   ℹ️  Informations: {summary.get('info_count', 0)}")
print("")

# Afficher les anomalies critiques
if anomalies.get("critical"):
    print("   🔴 ANOMALIES CRITIQUES:")
    for anomaly in anomalies["critical"]:
        print(f"      • {anomaly.get('title', 'N/A')}")
        print(f"        {anomaly.get('description', '')}")
        if anomaly.get('details'):
            print(f"        Détails: {len(anomaly['details'])} éléments")
    print("")

# Afficher les avertissements
if anomalies.get("warning"):
    print("   🟡 AVERTISSEMENTS:")
    for anomaly in anomalies["warning"][:5]:  # Limiter à 5
        print(f"      • {anomaly.get('title', 'N/A')}")
        print(f"        {anomaly.get('description', '')}")
        if anomaly.get('count', 0) > 5:
            print(f"        ({anomaly['count']} éléments au total)")
    print("")

# Afficher les infos
if anomalies.get("info"):
    print("   ℹ️  INFORMATIONS:")
    for anomaly in anomalies["info"]:
        print(f"      • {anomaly.get('title', 'N/A')}: {anomaly.get('description', '')}")
EOF
echo ""

# 7. Mapping des comptes vers catégories AIA
echo "7️⃣  MAPPING DES COMPTES VERS CATÉGORIES AIA"
echo "----------------------"
curl -s "${API_URL}/api/aia/view?company_id=${COMPANY_ID}&months=${MONTHS}" | python3 << 'EOF'
import sys, json
data = json.load(sys.stdin)
mapping = data.get("accounts_mapping", {})

print(f"   Total comptes mappés: {len(mapping)}")
print("")

# Grouper par catégorie
categories = {}
for account_name, details in mapping.items():
    category = details.get("category", "unknown")
    if category not in categories:
        categories[category] = []
    categories[category].append(account_name)

# Afficher les catégories avec le plus de comptes
print("   Top catégories par nombre de comptes:")
print("   " + "-" * 70)
for category, accounts in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
    cat_name = details.get("category_name", category) if mapping else category
    if mapping and mapping.get(accounts[0] if accounts else None):
        cat_name = mapping[accounts[0]].get("category_name", category)
    print(f"   {cat_name[:50]:<50} : {len(accounts)} comptes")
    
    # Afficher quelques exemples
    if accounts:
        examples = accounts[:3]
        for acc in examples:
            print(f"      - {acc[:60]}")
        if len(accounts) > 3:
            print(f"      ... et {len(accounts) - 3} autres")
EOF
echo ""

# 8. Snapshots disponibles
echo "8️⃣  SNAPSHOTS DISPONIBLES"
echo "----------------------"
curl -s "${API_URL}/api/qbo/data?company_id=${COMPANY_ID}&months=${MONTHS}" | python3 << 'EOF'
import sys, json
from datetime import datetime

data = json.load(sys.stdin)
snapshots = data.get("snapshots", [])

print(f"   Total snapshots: {len(snapshots)}")
print("")
if snapshots:
    print("   Type | Période début | Période fin | Créé le | Données")
    print("   " + "-" * 90)
    for snap in snapshots:
        r_type = snap.get("report_type", "N/A")
        start = snap.get("period_start", "N/A")
        end = snap.get("period_end", "N/A")
        created = snap.get("created_at", "N/A")
        has_data = "✅ Oui" if snap.get("has_data") else "❌ Non"
        
        if created != "N/A":
            try:
                created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                created = created_dt.strftime("%Y-%m-%d %H:%M")
            except:
                pass
        
        print(f"   {r_type:<15} | {start} | {end} | {created} | {has_data}")
else:
    print("   ℹ️  Aucun snapshot disponible")
EOF
echo ""

echo "================================================"
echo "✅ Rapport terminé"
echo ""
echo "📄 Pour exporter les données:"
echo "   - CSV: ${API_URL}/api/aia/export/google-sheets?company_id=${COMPANY_ID}&months=${MONTHS}&format=csv"
echo "   - JSON: ${API_URL}/api/aia/export/google-sheets?company_id=${COMPANY_ID}&months=${MONTHS}&format=json"
echo ""
echo "🌐 Interface web: http://localhost:3000"
echo ""
