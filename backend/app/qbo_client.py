import requests
import logging
from typing import Dict, List, Optional
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)

class QBOClient:
    """Client pour QuickBooks Online API"""
    
    def __init__(self):
        self.client_id = settings.QBO_CLIENT_ID
        self.client_secret = settings.QBO_CLIENT_SECRET
        self.company_id = settings.QBO_COMPANY_ID
        self.access_token = settings.QBO_ACCESS_TOKEN
        self.base_url = "https://quickbooks.api.intuit.com/v3/company"
    
    def get_profit_loss(self, start_date: str, end_date: str) -> Optional[Dict]:
        """Récupère le rapport P&L"""
        try:
            url = f"{self.base_url}/{self.company_id}/reports/ProfitAndLoss"
            params = {"start_date": start_date, "end_date": end_date}
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Erreur P&L: {str(e)}")
            return None
    
    def get_balance_sheet(self, as_of_date: str) -> Optional[Dict]:
        """Récupère le bilan"""
        try:
            url = f"{self.base_url}/{self.company_id}/reports/BalanceSheet"
            params = {"date": as_of_date}
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Erreur bilan: {str(e)}")
            return None
    
    def get_cash_flow(self, start_date: str, end_date: str) -> Optional[Dict]:
        """Récupère le cash flow"""
        try:
            url = f"{self.base_url}/{self.company_id}/reports/CashFlow"
            params = {"start_date": start_date, "end_date": end_date}
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Erreur cash flow: {str(e)}")
            return None
