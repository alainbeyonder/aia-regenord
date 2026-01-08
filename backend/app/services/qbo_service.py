import base64
import json
import os
from dataclasses import dataclass
from datetime import datetime, date, timedelta
from typing import Any, Dict, Optional, Tuple, List

import requests
from cryptography.fernet import Fernet
from dateutil.relativedelta import relativedelta

from app.core.database import SessionLocal
from app.models.qbo_connection import QBOConnection
from app.models.qbo_account import QBOAccount
from app.models.qbo_transaction_line import QBOTransactionLine
from app.models.qbo_report_snapshot import QBOReportSnapshot

from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parents[2] / ".env"  # backend/.env
load_dotenv(dotenv_path=env_path)

@dataclass
class QBOConfig:
    client_id: str
    client_secret: str
    redirect_uri: str
    environment: str  # "sandbox" or "production"
    encryption_key: str
    app_base_url: str

    @property
    def auth_base(self) -> str:
        return "https://appcenter.intuit.com/connect/oauth2"

    @property
    def token_url(self) -> str:
        return "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"

    @property
    def api_base(self) -> str:
        if self.environment == "sandbox":
            return "https://sandbox-quickbooks.api.intuit.com"
        else:
            return "https://quickbooks.api.intuit.com"

    @property
    def discovery_base(self) -> str:
        # If you need it later; kept for clarity
        return self.api_base


class QBOService:
    """
    QBO integration: OAuth2 + read-only sync (12 months baseline).
    """

    # Minimal scopes for read-only accounting data
    # Note: Intuit scopes can vary by app config; this is typical.
    SCOPES = "com.intuit.quickbooks.accounting openid profile email"

    @staticmethod
    def _cfg(env: str = None) -> QBOConfig:
        environment = env or os.environ.get("QBO_ENVIRONMENT", "sandbox")
        client_id = os.environ.get(f"QBO_{environment.upper()}_CLIENT_ID", os.environ["QBO_CLIENT_ID"])
        client_secret = os.environ.get(f"QBO_{environment.upper()}_CLIENT_SECRET", os.environ["QBO_CLIENT_SECRET"])
        return QBOConfig(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=os.environ["QBO_REDIRECT_URI"],
            environment=environment,
            encryption_key=os.environ["AIA_TOKEN_ENCRYPTION_KEY"],
            app_base_url=os.environ.get("APP_BASE_URL", "http://localhost:8000"),
        )

    # ---------------------------
    # Encryption helpers
    # ---------------------------
    @staticmethod
    def _fernet() -> Fernet:
        key = QBOService._cfg().encryption_key.encode()
        return Fernet(key)

    @staticmethod
    def _encrypt(plaintext: str) -> str:
        return QBOService._fernet().encrypt(plaintext.encode()).decode()

    @staticmethod
    def _decrypt(ciphertext: str) -> str:
        return QBOService._fernet().decrypt(ciphertext.encode()).decode()

    # ---------------------------
    # OAuth2 flow
    # ---------------------------
    @staticmethod
    def get_authorization_url(company_id: int, env: str = None) -> str:
        """
        Redirect user to Intuit OAuth. `state` carries company_id.
        MVP: state is plain company_id. Production: sign it (JWT/HMAC).
        """
        cfg = QBOService._cfg(env)
        state = str(company_id)

        params = {
            "client_id": cfg.client_id,
            "response_type": "code",
            "scope": QBOService.SCOPES,
            "redirect_uri": cfg.redirect_uri,
            "state": state,
        }
        req = requests.Request("GET", cfg.auth_base, params=params).prepare()
        return req.url

    @staticmethod
    def handle_callback(code: str, realm_id: str, state: str) -> None:
        """
        Exchange auth code for tokens, store them encrypted.
        `state` contains company_id.
        """
        cfg = QBOService._cfg()
        company_id = int(state)

        token_data = QBOService._exchange_code_for_tokens(code=code)

        access_token = token_data["access_token"]
        refresh_token = token_data["refresh_token"]
        expires_in = int(token_data.get("expires_in", 3600))
        token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 60)

        scopes = token_data.get("scope", "")

        db = SessionLocal()
        try:
            existing = (
                db.query(QBOConnection)
                .filter(QBOConnection.company_id == company_id, QBOConnection.is_active == True)
                .one_or_none()
            )
            if existing:
                existing.realm_id = realm_id
                existing.access_token_encrypted = QBOService._encrypt(access_token)
                existing.refresh_token_encrypted = QBOService._encrypt(refresh_token)
                existing.token_expires_at = token_expires_at
                existing.scopes = scopes
                existing.is_active = True
                existing.last_error = None
            else:
                conn = QBOConnection(
                    company_id=company_id,
                    realm_id=realm_id,
                    access_token_encrypted=QBOService._encrypt(access_token),
                    refresh_token_encrypted=QBOService._encrypt(refresh_token),
                    token_expires_at=token_expires_at,
                    scopes=scopes,
                    is_active=True,
                )
                db.add(conn)

            db.commit()
        finally:
            db.close()

    @staticmethod
    def _exchange_code_for_tokens(code: str) -> Dict[str, Any]:
        cfg = QBOService._cfg()

        basic = base64.b64encode(f"{cfg.client_id}:{cfg.client_secret}".encode()).decode()
        headers = {
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": cfg.redirect_uri,
        }

        r = requests.post(cfg.token_url, headers=headers, data=data, timeout=30)
        if r.status_code >= 400:
            raise RuntimeError(f"QBO token exchange failed: {r.status_code} {r.text}")
        return r.json()

    @staticmethod
    def _refresh_tokens(refresh_token: str) -> Dict[str, Any]:
        cfg = QBOService._cfg()

        basic = base64.b64encode(f"{cfg.client_id}:{cfg.client_secret}".encode()).decode()
        headers = {
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }

        r = requests.post(cfg.token_url, headers=headers, data=data, timeout=30)
        if r.status_code >= 400:
            raise RuntimeError(f"QBO refresh failed: {r.status_code} {r.text}")
        return r.json()

    # ---------------------------
    # Connection helpers
    # ---------------------------
    @staticmethod
    def _get_active_connection(db, company_id: int) -> QBOConnection:
        conn = (
            db.query(QBOConnection)
            .filter(QBOConnection.company_id == company_id, QBOConnection.is_active == True)
            .one_or_none()
        )
        if not conn:
            raise RuntimeError("No active QBO connection for this company_id.")
        return conn

    @staticmethod
    def refresh_access_token_if_needed(company_id: int) -> None:
        db = SessionLocal()
        try:
            conn = QBOService._get_active_connection(db, company_id)

            if conn.token_expires_at and conn.token_expires_at > datetime.utcnow():
                return

            refresh_token = QBOService._decrypt(conn.refresh_token_encrypted)
            token_data = QBOService._refresh_tokens(refresh_token)

            access_token = token_data["access_token"]
            new_refresh = token_data.get("refresh_token", refresh_token)
            expires_in = int(token_data.get("expires_in", 3600))
            token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 60)

            conn.access_token_encrypted = QBOService._encrypt(access_token)
            conn.refresh_token_encrypted = QBOService._encrypt(new_refresh)
            conn.token_expires_at = token_expires_at
            conn.scopes = token_data.get("scope", conn.scopes)
            conn.last_error = None
            db.commit()
        finally:
            db.close()

    # ---------------------------
    # QBO API calls
    # ---------------------------
    @staticmethod
    def _qbo_headers(access_token: str) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    @staticmethod
    def _qbo_get(company_realm_id: str, path: str, params: Optional[Dict[str, Any]] = None, access_token: str = "") -> Dict[str, Any]:
        cfg = QBOService._cfg()
        url = f"{cfg.api_base}{path}"
        headers = QBOService._qbo_headers(access_token)
        r = requests.get(url, headers=headers, params=params or {}, timeout=30)
        if r.status_code >= 400:
            raise RuntimeError(f"QBO GET failed {r.status_code}: {r.text}")
        return r.json()

    # ---------------------------
    # Sync orchestration (12 months baseline)
    # ---------------------------
    @staticmethod
    def sync_company(company_id: int, months: int = 12) -> Dict[str, Any]:
        """
        Baseline sync:
        - Accounts
        - P&L report (12 months)
        - Balance Sheet report (end date)
        - Transaction lines (via Query API)
        """
        QBOService.refresh_access_token_if_needed(company_id)

        db = SessionLocal()
        try:
            conn = QBOService._get_active_connection(db, company_id)
            access_token = QBOService._decrypt(conn.access_token_encrypted)
            realm_id = conn.realm_id

            end = date.today()
            start = (end - relativedelta(months=months)).replace(day=1)

            # 1) Accounts
            accounts_json = QBOService._fetch_accounts(realm_id, access_token)
            upserted_accounts = QBOService._upsert_accounts(db, company_id, accounts_json)

            # 2) Reports snapshots (raw JSON for audit)
            pnl_json = QBOService._fetch_profit_and_loss(realm_id, access_token, start, end)
            bs_json = QBOService._fetch_balance_sheet(realm_id, access_token, start, end)

            QBOService._store_report_snapshot(db, company_id, "ProfitAndLoss", start, end, pnl_json)
            QBOService._store_report_snapshot(db, company_id, "BalanceSheet", start, end, bs_json)

            # 3) Transactions (12 months)
            txn_count = QBOService._sync_transaction_lines(db, company_id, realm_id, access_token, start, end)

            conn.last_sync_at = datetime.utcnow()
            conn.last_error = None
            db.commit()

            return {
                "company_id": company_id,
                "realm_id": realm_id,
                "period_start": start.isoformat(),
                "period_end": end.isoformat(),
                "accounts_upserted": upserted_accounts,
                "transaction_lines_upserted": txn_count,
                "reports_saved": ["ProfitAndLoss", "BalanceSheet"],
            }

        except Exception as e:
            # record last_error for banking-grade traceability
            try:
                conn = QBOService._get_active_connection(db, company_id)
                conn.last_error = str(e)
                db.commit()
            except Exception:
                pass
            raise
        finally:
            db.close()

    # ---------------------------
    # Fetchers
    # ---------------------------
    @staticmethod
    def _fetch_accounts(realm_id: str, access_token: str) -> Dict[str, Any]:
        # Query API: SELECT * FROM Account
        # Endpoint pattern: /v3/company/{realmId}/query?query=...
        query = "select * from Account maxresults 1000"
        path = f"/v3/company/{realm_id}/query"
        return QBOService._qbo_get(realm_id, path, params={"query": query}, access_token=access_token)

    @staticmethod
    def _fetch_profit_and_loss(realm_id: str, access_token: str, start: date, end: date) -> Dict[str, Any]:
        path = f"/v3/company/{realm_id}/reports/ProfitAndLoss"
        # Simplifier les paramètres - le summarize_column_by peut causer des erreurs selon la version API
        params = {
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
        }
        return QBOService._qbo_get(realm_id, path, params=params, access_token=access_token)

    @staticmethod
    def _fetch_balance_sheet(realm_id: str, access_token: str, start: date, end: date) -> Dict[str, Any]:
        path = f"/v3/company/{realm_id}/reports/BalanceSheet"
        params = {
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
        }
        return QBOService._qbo_get(realm_id, path, params=params, access_token=access_token)

    # ---------------------------
    # Persist helpers
    # ---------------------------
    @staticmethod
    def _upsert_accounts(db, company_id: int, accounts_json: Dict[str, Any]) -> int:
        """
        Upsert des comptes QBO dans la base de données.
        Utilise raw SQL car la structure de la DB utilise qbo_company_id au lieu de company_id.
        """
        accounts = accounts_json.get("QueryResponse", {}).get("Account", []) or []
        if not accounts:
            return 0
        
        # Obtenir le realm_id depuis la connexion
        conn = db.query(QBOConnection).filter(
            QBOConnection.company_id == company_id,
            QBOConnection.is_active == True
        ).first()
        if not conn:
            return 0
        
        realm_id = conn.realm_id
        count = 0
        
        from sqlalchemy import text
        
        for a in accounts:
            qbo_id = str(a.get("Id"))
            name = a.get("Name", "")
            a_type = a.get("AccountType")
            a_sub = a.get("AccountSubType")
            classification = a.get("Classification")
            active = bool(a.get("Active", True))
            
            # Vérifier si le compte existe déjà
            existing = db.execute(
                text("""
                    SELECT id FROM qbo_accounts 
                    WHERE account_id = :account_id AND qbo_company_id = :realm_id
                """),
                {"account_id": qbo_id, "realm_id": realm_id}
            ).fetchone()
            
            if existing:
                # Mettre à jour
                db.execute(
                    text("""
                        UPDATE qbo_accounts 
                        SET account_name = :name,
                            account_type = :type,
                            account_subtype = :subtype,
                            classification = :classification,
                            active = :active
                        WHERE account_id = :account_id AND qbo_company_id = :realm_id
                    """),
                    {
                        "account_id": qbo_id,
                        "name": name,
                        "type": a_type,
                        "subtype": a_sub,
                        "classification": classification,
                        "active": active,
                        "realm_id": realm_id
                    }
                )
            else:
                # Insérer
                db.execute(
                    text("""
                        INSERT INTO qbo_accounts (account_id, account_name, account_type, account_subtype, 
                                                classification, active, qbo_company_id)
                        VALUES (:account_id, :name, :type, :subtype, :classification, :active, :realm_id)
                    """),
                    {
                        "account_id": qbo_id,
                        "name": name,
                        "type": a_type,
                        "subtype": a_sub,
                        "classification": classification,
                        "active": active,
                        "realm_id": realm_id
                    }
                )
            count += 1
        
        db.commit()
        return count

    @staticmethod
    def _store_report_snapshot(db, company_id: int, report_type: str, start: date, end: date, raw: Dict[str, Any]) -> None:
        snap = QBOReportSnapshot(
            company_id=company_id,
            report_type=report_type,
            period_start=start,
            period_end=end,
            raw_json=json.dumps(raw),
        )
        db.add(snap)

    # ---------------------------
    # Transaction sync
    # ---------------------------
    @staticmethod
    def _sync_transaction_lines(db, company_id: int, realm_id: str, access_token: str, start: date, end: date) -> int:
        """
        MVP approach:
        - Pull JournalEntry lines via Query API (works well for accounting drill-down).
        - If you want broader coverage later, we add Bill/Invoice/Expense/VendorCredit queries.
        """
        total = 0
        # Pull journal entries updated/dated in range
        # Note: QBO SQL-like query is limited. We'll filter by TxnDate.
        query = (
            f"select * from JournalEntry "
            f"where TxnDate >= '{start.isoformat()}' and TxnDate <= '{end.isoformat()}' "
            f"maxresults 1000"
        )
        path = f"/v3/company/{realm_id}/query"
        data = QBOService._qbo_get(realm_id, path, params={"query": query}, access_token=access_token)

        entries = data.get("QueryResponse", {}).get("JournalEntry", []) or []
        for je in entries:
            txn_id = str(je.get("Id"))
            txn_date_str = je.get("TxnDate")
            if not txn_date_str:
                continue
            txn_dt = datetime.strptime(txn_date_str, "%Y-%m-%d").date()

            lines = je.get("Line", []) or []
            for ln in lines:
                amt = ln.get("Amount")
                if amt is None:
                    continue

                detail = ln.get("JournalEntryLineDetail", {}) or {}
                posting_type = detail.get("PostingType")  # Debit / Credit
                account_ref = (detail.get("AccountRef") or {}).get("value")
                memo = ln.get("Description")

                # Credit as negative, Debit as positive (simple standardization)
                amount = float(amt)
                if posting_type and posting_type.lower() == "credit":
                    amount = -amount

                # Upsert by (company_id, qbo_txn_id, account_qbo_id, amount, txn_date, memo) - MVP simplistic
                # For production, use unique keys + better idempotency.
                db.add(
                    QBOTransactionLine(
                        company_id=company_id,
                        qbo_txn_id=txn_id,
                        qbo_txn_type="JournalEntry",
                        txn_date=txn_dt,
                        account_qbo_id=str(account_ref) if account_ref else None,
                        amount=amount,
                        counterparty=None,
                        memo=memo,
                    )
                )
                total += 1

        return total

    # ---------------------------
    # Status / disconnect
    # ---------------------------
    @staticmethod
    def get_status(company_id: int) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            conn = (
                db.query(QBOConnection)
                .filter(QBOConnection.company_id == company_id, QBOConnection.is_active == True)
                .one_or_none()
            )
            if not conn:
                return {"connected": False, "company_id": company_id}

            return {
                "connected": True,
                "company_id": company_id,
                "realm_id": conn.realm_id,
                "last_sync_at": conn.last_sync_at.isoformat() if conn.last_sync_at else None,
                "last_error": conn.last_error,
                "token_expires_at": conn.token_expires_at.isoformat() if conn.token_expires_at else None,
            }
        finally:
            db.close()

    @staticmethod
    def disconnect(company_id: int) -> None:
        db = SessionLocal()
        try:
            conn = (
                db.query(QBOConnection)
                .filter(QBOConnection.company_id == company_id, QBOConnection.is_active == True)
                .one_or_none()
            )
            if conn:
                conn.is_active = False
                db.commit()
        finally:
            db.close()
