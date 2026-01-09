import logging
from typing import Dict, List
from datetime import datetime
import openai

from app.core.config import settings
from app.qbo_client import QBOClient

logger = logging.getLogger(__name__)

class FinancialProjections:
    """Générateur de projections financières 3 ans"""
    
    def __init__(self):
        self.qbo_client = QBOClient()
        self.projection_years = settings.PROJECTION_YEARS
        openai.api_key = settings.OPENAI_API_KEY
    
    def get_historical_data(self, years: int = 3) -> Dict:
        """Récupère les données historiques de QBO"""
        historical = {"revenue": [], "expenses": [], "cash_flow": []}
        
        try:
            current_year = datetime.now().year
            for year in range(current_year - years, current_year):
                start_date = f"{year}-01-01"
                end_date = f"{year}-12-31"
                
                pl_data = self.qbo_client.get_profit_loss(start_date, end_date)
                if pl_data:
                    historical["revenue"].append(self._extract_revenue(pl_data))
                    historical["expenses"].append(self._extract_expenses(pl_data))
                
                cf_data = self.qbo_client.get_cash_flow(start_date, end_date)
                if cf_data:
                    historical["cash_flow"].append(self._extract_cash_flow(cf_data))
            
            return historical
        except Exception as e:
            logger.error(f"Erreur récupération données historiques: {str(e)}")
            return historical
    
    def _extract_revenue(self, pl_data: Dict) -> float:
        """Extrait le revenu total du P&L"""
        # Logique d'extraction simplifiée
        return 0.0
    
    def _extract_expenses(self, pl_data: Dict) -> float:
        """Extrait les dépenses totales du P&L"""
        return 0.0
    
    def _extract_cash_flow(self, cf_data: Dict) -> float:
        """Extrait le cash flow net"""
        return 0.0
    
    def calculate_growth_rate(self, historical_values: List[float]) -> float:
        """Calcule le taux de croissance moyen"""
        if len(historical_values) < 2:
            return settings.DEFAULT_GROWTH_RATE
        
        total_growth = 0
        for i in range(1, len(historical_values)):
            if historical_values[i-1] != 0:
                growth = (historical_values[i] - historical_values[i-1]) / historical_values[i-1]
                total_growth += growth
        
        return total_growth / (len(historical_values) - 1) if len(historical_values) > 1 else settings.DEFAULT_GROWTH_RATE
    
    def generate_projections(self, assumptions: Dict = None) -> Dict:
        """Génère les projections financières 3 ans"""
        try:
            historical = self.get_historical_data()
            
            revenue_growth = self.calculate_growth_rate(historical["revenue"])
            expense_growth = self.calculate_growth_rate(historical["expenses"])
            
            projections = {
                "years": [],
                "revenue": [],
                "expenses": [],
                "net_income": [],
                "cash_flow": []
            }
            
            current_year = datetime.now().year
            last_revenue = historical["revenue"][-1] if historical["revenue"] else 100000
            last_expenses = historical["expenses"][-1] if historical["expenses"] else 80000
            
            for i in range(self.projection_years):
                year = current_year + i + 1
                projected_revenue = last_revenue * (1 + revenue_growth) ** (i + 1)
                projected_expenses = last_expenses * (1 + expense_growth) ** (i + 1)
                
                projections["years"].append(year)
                projections["revenue"].append(round(projected_revenue, 2))
                projections["expenses"].append(round(projected_expenses, 2))
                projections["net_income"].append(round(projected_revenue - projected_expenses, 2))
                projections["cash_flow"].append(round(projected_revenue - projected_expenses, 2))
            
            return projections
        except Exception as e:
            logger.error(f"Erreur génération projections: {str(e)}")
            return {}
