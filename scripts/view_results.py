#!/usr/bin/env python3
"""
Script pour afficher un rapport détaillé des données QBO synchronisées
"""

import json
import urllib.request
import urllib.error
from datetime import datetime
from collections import defaultdict

API_URL = "http://localhost:8000"
COMPANY_ID = 1
MONTHS = 12

def print_section(title, char="="):
    print(f"\n{char * 60}")
    print(f"{title}")
    print(f"{char * 60}\n")

def get_json(url):
    """Récupère du JSON depuis l'API"""
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = response.read().decode('utf-8')
            return json.loads(data)
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return None

print("📊 RAPPORT DÉTAILLÉ - QUICKBOOKS ONLINE SANDBOX")
print("=" * 60)

# 1. Statut de connexion
print_section("1️⃣  STATUT DE CONNEXION", "-")
status = get_json(f"{API_URL}/api/qbo/status?company_id={COMPANY_ID}")
if status:
    print(f"   Connecté: {'✅ Oui' if status.get('connected') else '❌ Non'}")
    if status.get('connected'):
        print(f"   Realm ID: {status.get('realm_id', 'N/A')}")
        print(f"   Dernière sync: {status.get('last_sync_at', 'N/A')}")
        print(f"   Token expire: {status.get('token_expires_at', 'N/A')}")

# 2. Statistiques générales
print_section("2️⃣  STATISTIQUES GÉNÉRALES", "-")
qbo_data = get_json(f"{API_URL}/api/qbo/data?company_id={COMPANY_ID}&months={MONTHS}")
if qbo_data:
    stats = qbo_data.get("statistics", {})
    print(f"   Comptes: {stats.get('total_accounts', 0)} ({stats.get('active_accounts', 0)} actifs, {stats.get('inactive_accounts', 0)} inactifs)")
    print(f"   Transactions: {stats.get('total_transactions', 0)}")
    print(f"   Snapshots: {stats.get('total_snapshots', 0)}")
    print(f"   Période: {stats.get('period_start', 'N/A')} à {stats.get('period_end', 'N/A')}")
    print(f"   Montant total: ${stats.get('total_amount', 0):,.2f}")
    print(f"   Transactions positives: {stats.get('positive_amounts', 0)}")
    print(f"   Transactions négatives: {stats.get('negative_amounts', 0)}")

# 3. Comptes
print_section("3️⃣  COMPTES QBO (premiers 20)", "-")
if qbo_data:
    accounts = qbo_data.get("accounts", [])[:20]
    print(f"   Total comptes: {len(qbo_data.get('accounts', []))}")
    if accounts:
        print("\n   Nom" + " " * 30 + "Type" + " " * 15 + "Statut")
        print("   " + "-" * 70)
        for acc in accounts:
            name = (acc.get("name", "N/A") or "N/A")[:30]
            a_type = (acc.get("account_type", "-") or "-")[:15]
            status = "✅ Actif" if acc.get("active", True) else "❌ Inactif"
            print(f"   {name:<30} {a_type:<15} {status}")

# 4. Transactions récentes
print_section("4️⃣  TRANSACTIONS RÉCENTES (10 dernières)", "-")
if qbo_data:
    transactions = qbo_data.get("transactions", [])[:10]
    print(f"   Total transactions: {len(qbo_data.get('transactions', []))}")
    if transactions:
        print("\n   Date       | Type           | Montant        | Contrepartie")
        print("   " + "-" * 70)
        for txn in transactions:
            date_str = txn.get("txn_date", "N/A")
            try:
                date_obj = datetime.fromisoformat(date_str)
                date_display = date_obj.strftime("%Y-%m-%d")
            except:
                date_display = date_str[:10] if date_str else "N/A"
            
            txn_type = (txn.get("txn_type", "-") or "-")[:15]
            amount = txn.get("amount", 0) or 0
            if amount < 0:
                amount_str = f"-${abs(amount):,.2f}"
            elif amount > 0:
                amount_str = f"+${amount:,.2f}"
            else:
                amount_str = "$0.00"
            
            counterparty = (txn.get("counterparty", "-") or "-")[:25]
            print(f"   {date_display} | {txn_type:<15} | {amount_str:>14} | {counterparty}")

# 5. Vue financière AIA
print_section("5️⃣  VUE FINANCIÈRE AIA", "-")
aia_view = get_json(f"{API_URL}/api/aia/view?company_id={COMPANY_ID}&months={MONTHS}")
if aia_view:
    totals = aia_view.get("totals_by_category", {})
    reconciliation = aia_view.get("reconciliation", {})
    
    print(f"   Période: {aia_view.get('period_start')} à {aia_view.get('period_end')}")
    print(f"   Source: {aia_view.get('data_source', 'N/A')}")
    print(f"   Catégories: {len(totals)}")
    print("\n   Réconciliation:")
    print(f"      Total QBO: ${reconciliation.get('total_qbo', 0):,.2f}")
    print(f"      Total AIA: ${reconciliation.get('total_aia', 0):,.2f}")
    print(f"      Delta: ${reconciliation.get('delta', 0):,.2f}")
    print(f"      Statut: {'✅ Réconcilié' if reconciliation.get('reconciled', False) else '⚠️  Écart'}")
    
    # Catégories avec montants
    categories_with_amounts = [(k, v) for k, v in totals.items() if abs(v.get('total', 0)) > 0.01]
    if categories_with_amounts:
        print("\n   Catégories avec montants:")
        print("   " + "-" * 70)
        print("   Nom" + " " * 35 + "Total" + " " * 12 + "Confiance | Comptes")
        print("   " + "-" * 70)
        for key, cat in sorted(categories_with_amounts, key=lambda x: abs(x[1].get('total', 0)), reverse=True):
            name = cat.get('name', key)[:40]
            total = cat.get('total', 0)
            confidence = cat.get('confidence_score', 0)
            count = cat.get('accounts_count', 0)
            print(f"   {name:<40} ${total:>12,.2f} {confidence:>8.2f}  {count:>7}")
    else:
        print("\n   ℹ️  Aucune catégorie avec montants (données vides)")

# 6. Anomalies
print_section("6️⃣  ANALYSE D'ANOMALIES", "-")
if qbo_data:
    anomalies = qbo_data.get("anomalies", {})
    summary = anomalies.get("summary", {})
    
    print(f"   Total: {summary.get('total', 0)} anomalies détectées")
    print(f"   🔴 Critiques: {summary.get('critical_count', 0)}")
    print(f"   🟡 Avertissements: {summary.get('warning_count', 0)}")
    print(f"   ℹ️  Informations: {summary.get('info_count', 0)}")
    
    if anomalies.get("critical"):
        print("\n   🔴 ANOMALIES CRITIQUES:")
        for anomaly in anomalies["critical"]:
            print(f"      • {anomaly.get('title', 'N/A')}")
            print(f"        {anomaly.get('description', '')}")
            if anomaly.get('details'):
                print(f"        Détails: {len(anomaly['details'])} éléments")
    
    if anomalies.get("warning"):
        print("\n   🟡 AVERTISSEMENTS:")
        for anomaly in anomalies["warning"][:5]:
            print(f"      • {anomaly.get('title', 'N/A')}")
            print(f"        {anomaly.get('description', '')}")
            if anomaly.get('count', 0) > 5:
                print(f"        ({anomaly['count']} éléments au total)")
    
    if anomalies.get("info"):
        print("\n   ℹ️  INFORMATIONS:")
        for anomaly in anomalies["info"]:
            print(f"      • {anomaly.get('title', 'N/A')}: {anomaly.get('description', '')}")

# 7. Mapping des comptes
print_section("7️⃣  MAPPING DES COMPTES VERS CATÉGORIES AIA", "-")
if aia_view:
    mapping = aia_view.get("accounts_mapping", {})
    print(f"   Total comptes mappés: {len(mapping)}")
    
    if mapping:
        # Grouper par catégorie
        categories = defaultdict(list)
        for account_name, details in mapping.items():
            category = details.get("category", "unknown")
            categories[category].append(account_name)
        
        print("\n   Top catégories par nombre de comptes:")
        print("   " + "-" * 70)
        for category, accounts in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            if accounts and mapping.get(accounts[0]):
                cat_name = mapping[accounts[0]].get("category_name", category)
            else:
                cat_name = category
            print(f"\n   {cat_name[:50]}: {len(accounts)} comptes")
            
            # Afficher quelques exemples
            for acc in accounts[:5]:
                print(f"      - {acc[:60]}")
            if len(accounts) > 5:
                print(f"      ... et {len(accounts) - 5} autres")

# 8. Snapshots
print_section("8️⃣  SNAPSHOTS DISPONIBLES", "-")
if qbo_data:
    snapshots = qbo_data.get("snapshots", [])
    print(f"   Total snapshots: {len(snapshots)}")
    if snapshots:
        print("\n   Type           | Période début  | Période fin    | Créé le          | Données")
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
            
            print(f"   {r_type:<15} | {start} | {end} | {created:<17} | {has_data}")
    else:
        print("\n   ℹ️  Aucun snapshot disponible")

print_section("✅ RAPPORT TERMINÉ", "=")
print("\n📄 Pour exporter les données:")
print(f"   - CSV: {API_URL}/api/aia/export/google-sheets?company_id={COMPANY_ID}&months={MONTHS}&format=csv")
print(f"   - JSON: {API_URL}/api/aia/export/google-sheets?company_id={COMPANY_ID}&months={MONTHS}&format=json")
print("\n🌐 Interface web: http://localhost:3000")
print()
