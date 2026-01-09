from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Dict, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal
from collections import defaultdict

from app.services.qbo_service import QBOService
from app.core.config import settings
from app.core.database import get_db
from app.models.qbo_account import QBOAccount
from app.models.qbo_transaction_line import QBOTransactionLine
from app.models.qbo_report_snapshot import QBOReportSnapshot
from app.models.qbo_connection import QBOConnection

router = APIRouter(prefix="/qbo", tags=["qbo"])


class SyncRequest(BaseModel):
    company_id: int
    months: int = 12  # MVP: 12 derniers mois


@router.get("/connect")
def qbo_connect(company_id: int):
    """
    Redirige l'utilisateur vers Intuit OAuth pour connecter QuickBooks.
    """
    # TODO (prod): signer `state` (JWT/HMAC). MVP: state = company_id
    url = QBOService.get_authorization_url(company_id=company_id)
    return RedirectResponse(url=url)


@router.get("/connect/sandbox")
def qbo_connect_sandbox(company_id: int, redirect: bool = True):
    """
    Redirige l'utilisateur vers Intuit OAuth Sandbox.
    Si redirect=False, retourne l'URL en JSON.
    """
    url = QBOService.get_authorization_url(company_id=company_id, env="sandbox")
    if redirect:
        return RedirectResponse(url=url)
    else:
        return {"auth_url": url, "company_id": company_id}


@router.get("/connect/production")
def qbo_connect_production(company_id: int, redirect: bool = True):
    """
    Redirige l'utilisateur vers Intuit OAuth Production.
    Si redirect=False, retourne l'URL en JSON (pour Squarespace).
    """
    url = QBOService.get_authorization_url(company_id=company_id, env="production")
    if redirect:
        return RedirectResponse(url=url)
    else:
        return {"auth_url": url, "company_id": company_id}


@router.get("/callback")
def qbo_callback(code: str, realmId: str, state: str):
    """
    Reçoit le code OAuth et le realmId, échange contre tokens et sauvegarde.
    `state` contient le company_id (MVP).
    Redirige vers le frontend ou Squarespace après connexion réussie.
    """
    QBOService.handle_callback(code=code, realm_id=realmId, state=state)
    
    # Déterminer l'URL de redirection
    # Priorité: FRONTEND_URL > CORS_ORIGINS[0] > default
    frontend_url = "http://localhost:3000"
    if hasattr(settings, 'FRONTEND_URL') and settings.FRONTEND_URL:
        frontend_url = settings.FRONTEND_URL
    elif hasattr(settings, 'CORS_ORIGINS') and settings.CORS_ORIGINS and len(settings.CORS_ORIGINS) > 0:
        frontend_url = settings.CORS_ORIGINS[0]
    
    # Si l'URL contient "regenord.com", rediriger vers la page Squarespace
    if "regenord.com" in frontend_url:
        redirect_url = f"{frontend_url}/quickbooks-integration?qbo_connected=true&realm_id={realmId}"
    else:
        redirect_url = f"{frontend_url}?qbo_connected=true&realm_id={realmId}"
    
    return RedirectResponse(url=redirect_url)


@router.post("/sync")
def qbo_sync(payload: SyncRequest):
    """
    Lance une synchronisation manuelle (utile pour debug et banque).
    """
    result = QBOService.sync_company(company_id=payload.company_id, months=payload.months)
    return {"status": "ok", "result": result}


@router.get("/status")
def qbo_status(company_id: int):
    """
    Retourne l'état de la connexion et dernière sync.
    """
    return QBOService.get_status(company_id=company_id)


@router.post("/disconnect")
def qbo_disconnect(company_id: int):
    """
    Désactive la connexion QuickBooks (archive ou purge tokens).
    """
    QBOService.disconnect(company_id=company_id)
    return {"status": "disconnected"}


@router.get("/config/check")
def check_qbo_config():
    """
    Vérifie la configuration QBO (sandbox vs production).
    Utile pour diagnostiquer les problèmes de configuration.
    """
    import os
    from app.core.config import settings
    
    environment = os.environ.get("QBO_ENVIRONMENT", "production")  # Production par défaut - PAS de sandbox
    client_id = os.environ.get("QBO_CLIENT_ID", "")
    client_secret = os.environ.get("QBO_CLIENT_SECRET", "")
    redirect_uri = os.environ.get("QBO_REDIRECT_URI", "")
    
    # Vérifier si des credentials spécifiques à l'environnement existent
    env_specific_client_id = os.environ.get(f"QBO_{environment.upper()}_CLIENT_ID")
    env_specific_client_secret = os.environ.get(f"QBO_{environment.upper()}_CLIENT_SECRET")
    
    config_status = {
        "environment": environment,
        "client_id_configured": bool(client_id or env_specific_client_id),
        "client_secret_configured": bool(client_secret or env_specific_client_secret),
        "redirect_uri_configured": bool(redirect_uri),
        "using_env_specific_credentials": bool(env_specific_client_id),
        "redirect_uri": redirect_uri,
        "api_base_url": "https://sandbox-quickbooks.api.intuit.com" if environment == "sandbox" else "https://quickbooks.api.intuit.com",
        "auth_url": "https://appcenter.intuit.com/connect/oauth2",
        "status": "ok" if (client_id or env_specific_client_id) and (client_secret or env_specific_client_secret) and redirect_uri else "incomplete"
    }
    
    return {
        "configuration": config_status,
        "ready_for_production": environment == "production" and config_status["status"] == "ok",
        "ready_for_sandbox": environment == "sandbox" and config_status["status"] == "ok"
    }


@router.get("/data")
def get_qbo_raw_data(
    company_id: int = Query(..., description="ID de l'entreprise"),
    months: int = Query(12, ge=1, le=36, description="Nombre de mois à analyser"),
    db: Session = Depends(get_db)
):
    """
    Récupère les données QBO brutes et effectue une analyse d'anomalies.
    
    Retourne:
    - Liste des comptes QBO
    - Liste des transactions
    - Liste des snapshots de rapports
    - Analyse d'anomalies potentielles
    """
    try:
        # Obtenir le realm_id
        connection = db.query(QBOConnection).filter(
            and_(
                QBOConnection.company_id == company_id,
                QBOConnection.is_active == True
            )
        ).first()
        
        if not connection:
            raise HTTPException(status_code=404, detail="Aucune connexion QBO active trouvée")
        
        realm_id = connection.realm_id
        
        # Calculer la période
        period_end = date.today()
        period_start = (period_end - timedelta(days=30 * months)).replace(day=1)
        
        # Récupérer les comptes - utiliser raw SQL car la structure utilise qbo_company_id
        from sqlalchemy import text
        db.rollback()
        # Requête simplifiée avec seulement les colonnes essentielles
        accounts_result = db.execute(
            text("""
                SELECT account_id, account_name, account_type, account_subtype, 
                       classification, active
                FROM qbo_accounts
                WHERE qbo_company_id = :realm_id
                ORDER BY account_name
            """),
            {"realm_id": realm_id}
        ).fetchall()
        
        accounts = [
            {
                "qbo_account_id": row[0],
                "name": row[1],
                "account_type": row[2],
                "account_subtype": row[3],
                "classification": row[4],
                "active": row[5] if len(row) > 5 else True
            }
            for row in accounts_result
        ]
        
        # Récupérer les transactions
        transactions = db.query(QBOTransactionLine).filter(
            and_(
                QBOTransactionLine.company_id == company_id,
                QBOTransactionLine.txn_date >= period_start,
                QBOTransactionLine.txn_date <= period_end
            )
        ).order_by(QBOTransactionLine.txn_date.desc()).limit(1000).all()  # Limiter à 1000 pour performance
        
        transactions_data = [
            {
                "id": txn.id,
                "qbo_txn_id": txn.qbo_txn_id,
                "txn_type": txn.qbo_txn_type,
                "txn_date": txn.txn_date.isoformat() if txn.txn_date else None,
                "account_qbo_id": txn.account_qbo_id,
                "amount": float(txn.amount) if txn.amount else 0.0,
                "counterparty": txn.counterparty,
                "memo": txn.memo
            }
            for txn in transactions
        ]
        
        # Récupérer les snapshots
        snapshots = db.query(QBOReportSnapshot).filter(
            and_(
                QBOReportSnapshot.company_id == company_id,
                QBOReportSnapshot.period_start >= period_start,
                QBOReportSnapshot.period_end <= period_end
            )
        ).order_by(QBOReportSnapshot.created_at.desc()).all()
        
        snapshots_data = [
            {
                "id": snap.id,
                "report_type": snap.report_type,
                "period_start": snap.period_start.isoformat() if snap.period_start else None,
                "period_end": snap.period_end.isoformat() if snap.period_end else None,
                "created_at": snap.created_at.isoformat() if snap.created_at else None,
                "has_data": len(snap.raw_json) > 0 if snap.raw_json else False
            }
            for snap in snapshots
        ]
        
        # ANALYSE D'ANOMALIES
        anomalies = analyze_anomalies(accounts, transactions_data, snapshots_data, realm_id, db)
        
        # Statistiques globales
        stats = {
            "total_accounts": len(accounts),
            "active_accounts": sum(1 for acc in accounts if acc.get("active", True)),
            "inactive_accounts": sum(1 for acc in accounts if not acc.get("active", True)),
            "total_transactions": len(transactions_data),
            "total_snapshots": len(snapshots_data),
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "total_amount": sum(abs(t.get("amount", 0)) for t in transactions_data),
            "positive_amounts": sum(1 for t in transactions_data if t.get("amount", 0) > 0),
            "negative_amounts": sum(1 for t in transactions_data if t.get("amount", 0) < 0)
        }
        
        return {
            "company_id": company_id,
            "realm_id": realm_id,
            "statistics": stats,
            "accounts": accounts,
            "transactions": transactions_data,
            "snapshots": snapshots_data,
            "anomalies": anomalies
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des données QBO: {str(e)}")


def analyze_anomalies(
    accounts: List[Dict],
    transactions: List[Dict],
    snapshots: List[Dict],
    realm_id: str,
    db: Session
) -> Dict:
    """
    Analyse les données QBO pour détecter des anomalies potentielles.
    """
    anomalies = {
        "critical": [],
        "warning": [],
        "info": []
    }
    
    # 1. Comptes sans type
    accounts_without_type = [acc for acc in accounts if not acc.get("account_type")]
    if accounts_without_type:
        anomalies["warning"].append({
            "type": "accounts_without_type",
            "severity": "warning",
            "title": "Comptes sans type défini",
            "description": f"{len(accounts_without_type)} compte(s) n'ont pas de type de compte défini",
            "count": len(accounts_without_type),
            "details": [{"name": acc["name"], "qbo_account_id": acc["qbo_account_id"]} for acc in accounts_without_type[:5]]
        })
    
    # 2. Comptes inactifs avec des transactions récentes
    active_account_ids = {acc["qbo_account_id"] for acc in accounts if acc.get("active", True)}
    inactive_account_ids = {acc["qbo_account_id"] for acc in accounts if not acc.get("active", True)}
    
    transactions_on_inactive = [
        t for t in transactions
        if t.get("account_qbo_id") in inactive_account_ids
    ]
    
    if transactions_on_inactive:
        anomalies["warning"].append({
            "type": "transactions_on_inactive_accounts",
            "severity": "warning",
            "title": "Transactions sur comptes inactifs",
            "description": f"{len(transactions_on_inactive)} transaction(s) trouvée(s) sur des comptes inactifs",
            "count": len(transactions_on_inactive),
            "details": transactions_on_inactive[:5]
        })
    
    # 3. Transactions avec montants très élevés (outliers)
    if transactions:
        amounts = [abs(t.get("amount", 0)) for t in transactions if t.get("amount")]
        if amounts:
            import statistics
            mean_amount = statistics.mean(amounts)
            stdev_amount = statistics.stdev(amounts) if len(amounts) > 1 else 0
            
            # Montants > moyenne + 3 écarts-types
            threshold = mean_amount + (3 * stdev_amount)
            large_transactions = [
                t for t in transactions
                if abs(t.get("amount", 0)) > threshold
            ]
            
            if large_transactions:
                anomalies["warning"].append({
                    "type": "large_transactions",
                    "severity": "warning",
                    "title": "Transactions avec montants anormalement élevés",
                    "description": f"{len(large_transactions)} transaction(s) avec des montants > {threshold:,.2f} (moyenne: {mean_amount:,.2f})",
                    "count": len(large_transactions),
                    "threshold": threshold,
                    "details": sorted(large_transactions, key=lambda x: abs(x.get("amount", 0)), reverse=True)[:5]
                })
    
    # 4. Transactions avec dates futures
    future_transactions = [
        t for t in transactions
        if t.get("txn_date") and datetime.fromisoformat(t["txn_date"]).date() > date.today()
    ]
    
    if future_transactions:
        anomalies["critical"].append({
            "type": "future_transactions",
            "severity": "critical",
            "title": "Transactions avec dates futures",
            "description": f"{len(future_transactions)} transaction(s) avec des dates dans le futur",
            "count": len(future_transactions),
            "details": future_transactions[:5]
        })
    
    # 5. Transactions sans compte associé
    transactions_without_account = [
        t for t in transactions
        if not t.get("account_qbo_id")
    ]
    
    if transactions_without_account:
        anomalies["warning"].append({
            "type": "transactions_without_account",
            "severity": "warning",
            "title": "Transactions sans compte associé",
            "description": f"{len(transactions_without_account)} transaction(s) sans compte QBO associé",
            "count": len(transactions_without_account),
            "details": transactions_without_account[:5]
        })
    
    # 6. Comptes référencés dans transactions mais absents de la liste des comptes
    account_ids_in_transactions = {t.get("account_qbo_id") for t in transactions if t.get("account_qbo_id")}
    account_ids_known = {acc["qbo_account_id"] for acc in accounts}
    missing_accounts = account_ids_in_transactions - account_ids_known
    
    if missing_accounts:
        anomalies["warning"].append({
            "type": "missing_accounts",
            "severity": "warning",
            "title": "Comptes référencés mais absents",
            "description": f"{len(missing_accounts)} compte(s) référencé(s) dans les transactions mais absent(s) de la liste des comptes",
            "count": len(missing_accounts),
            "details": [{"qbo_account_id": acc_id} for acc_id in list(missing_accounts)[:5]]
        })
    
    # 7. Snapshots manquants
    if not snapshots:
        anomalies["info"].append({
            "type": "no_snapshots",
            "severity": "info",
            "title": "Aucun snapshot de rapport disponible",
            "description": "Aucun snapshot P&L ou Balance Sheet trouvé pour cette période",
            "count": 0
        })
    
    # 8. Duplicate transactions (même txn_id)
    if transactions:
        txn_ids = defaultdict(list)
        for txn in transactions:
            txn_ids[txn.get("qbo_txn_id")].append(txn)
        
        duplicates = {tid: txs for tid, txs in txn_ids.items() if len(txs) > 1}
        
        if duplicates:
            anomalies["warning"].append({
                "type": "duplicate_transactions",
                "severity": "warning",
                "title": "Transactions en double",
                "description": f"{len(duplicates)} transaction ID(s) apparaissant plusieurs fois",
                "count": len(duplicates),
                "details": [
                    {
                        "qbo_txn_id": tid,
                        "count": len(txs),
                        "sample": txs[0]
                    }
                    for tid, txs in list(duplicates.items())[:5]
                ]
            })
    
    # 9. Transactions avec montant zéro
    zero_amount_transactions = [
        t for t in transactions
        if t.get("amount") == 0.0
    ]
    
    if zero_amount_transactions:
        anomalies["info"].append({
            "type": "zero_amount_transactions",
            "severity": "info",
            "title": "Transactions avec montant zéro",
            "description": f"{len(zero_amount_transactions)} transaction(s) avec un montant de 0.00",
            "count": len(zero_amount_transactions),
            "details": zero_amount_transactions[:5]
        })
    
    # Résumé
    anomalies["summary"] = {
        "total": len(anomalies["critical"]) + len(anomalies["warning"]) + len(anomalies["info"]),
        "critical_count": len(anomalies["critical"]),
        "warning_count": len(anomalies["warning"]),
        "info_count": len(anomalies["info"])
    }
    
    return anomalies
