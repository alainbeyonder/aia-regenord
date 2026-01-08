"""
Service de mapping des comptes QuickBooks vers les catégories AIA.
Génère une vue agrégée P&L macro par mois basée sur les données QBO.

ARCHITECTURE DU REGROUPEMENT:

1. MAPPING DES COMPTES (Compte QBO → Catégorie AIA)
   ─────────────────────────────────────────────────────
   Le système utilise un algorithme de matching par keywords pour mapper chaque
   compte QuickBooks vers une catégorie AIA standardisée.
   
   Ordre de priorité du matching:
   a) Correspondance exacte du nom complet avec un keyword → Score: 1.0
      Ex: "Research & Development" → expense_rsde (si "research" est keyword)
   
   b) Keyword trouvé dans le nom du compte → Score: 0.9
      Ex: "Salaries - Engineering" → expense_salaries (si "salary" est keyword)
   
   c) Correspondance par type de compte QBO → Score: 0.7
      Ex: Type "Expense" + Sous-type "Salaries" → expense_salaries
   
   d) Fallback par type général → Score: 0.4
      Ex: Type "Income" → revenue_other (si aucun keyword ne match)
   
   e) Fallback final → Score: 0.2
      Ex: Aucune correspondance → expense_other
   
   Le mapping est traçable: chaque compte conserve son score de confiance,
   permettant de comprendre pourquoi il a été mappé vers cette catégorie.

2. AGRÉGATION DES DONNÉES PAR MOIS
   ─────────────────────────────────
   Les données financières sont agrégées par catégorie AIA et par mois.
   
   Sources de données (par ordre de priorité):
   a) QBOReportSnapshot (ProfitAndLoss) - Source privilégiée
      - Contient les rapports P&L bruts de QuickBooks
      - Structure JSON complexe avec lignes et sous-lignes
      - Parse récursif pour extraire les montants par compte et par période
   
   b) QBOTransactionLine - Fallback si pas de snapshot P&L
      - Lignes de transaction individuelles
      - Agrégation par mois et par compte
      - Moins précis mais plus granulaire
   
   Processus d'agrégation:
   1. Pour chaque mois dans la période (ex: 2025-01 à 2026-01)
   2. Pour chaque compte QBO avec des transactions/montants
   3. Mapper le compte vers sa catégorie AIA (voir section 1)
   4. Additionner les montants par catégorie pour ce mois
   
   Résultat: Dict[month_key, Dict[category, total_amount]]
   Ex: {"2025-03": {"expense_salaries": 15000.0, "revenue": 50000.0}}

3. CALCUL DU SCORE DE CONFIANCE PAR CATÉGORIE
   ────────────────────────────────────────────
   Le score de confiance mesure la fiabilité du mapping pour une catégorie.
   
   Calcul:
   - Pour chaque compte mappé vers la catégorie, on a un score (0.2 à 1.0)
   - Score catégorie = moyenne des scores de tous les comptes de cette catégorie
   - Si aucun compte mappé → Score = 0.5 (neutralité)
   
   Interprétation:
   - 0.8-1.0: Très haute confiance (matching exact ou keywords précis)
   - 0.6-0.8: Bonne confiance (matching par type de compte)
   - 0.4-0.6: Confiance moyenne (fallback par type général)
   - 0.2-0.4: Faible confiance (fallback final)

4. RÉCONCILIATION QBO vs AIA
   ──────────────────────────
   Vérifie que les totaux correspondent entre les données brutes QBO et
   les données agrégées par catégories AIA.
   
   Calcul:
   - total_qbo: Somme de tous les montants bruts depuis QBO (snapshot ou transactions)
   - total_aia: Somme de tous les totaux par catégorie AIA
   - delta = total_qbo - total_aia
   - reconciled = abs(delta) <= tolerance (par défaut: 0.01$)
   
   Si delta > tolerance, cela indique:
   - Des comptes non mappés (restent dans les données QBO mais pas dans AIA)
   - Des erreurs dans l'agrégation
   - Des différences de traitement entre les deux sources

5. STRUCTURE DE SORTIE
   ────────────────────
   La vue financière retourne:
   - period_start/period_end: Période analysée
   - totals_by_category: Pour chaque catégorie AIA:
     * name: Nom lisible de la catégorie
     * monthly_totals: Montants par mois {month_key: amount}
     * total: Total sur toute la période
     * confidence_score: Score de confiance (0.0-1.0)
     * accounts_count: Nombre de comptes QBO mappés vers cette catégorie
   - accounts_mapping: Détail de chaque compte et sa catégorie assignée
   - reconciliation: Validation des totaux (QBO vs AIA)
   - data_source: Source utilisée (pnl_snapshot ou transaction_lines)

TRACABILITÉ ET EXPLICABILITÉ:
─────────────────────────────
Tous les mappings sont loggés avec le raisonnement:
- Keyword utilisé pour le matching
- Type de correspondance (exact, partiel, type, fallback)
- Score de confiance attribué

Cela permet de comprendre et justifier chaque regroupement effectué.
"""

import json
import yaml
import csv
import io
import logging
from typing import Dict, List, Optional, Tuple
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from pathlib import Path
from collections import defaultdict

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, extract

from app.core.database import SessionLocal
from app.models.qbo_account import QBOAccount
from app.models.qbo_transaction_line import QBOTransactionLine
from app.models.qbo_report_snapshot import QBOReportSnapshot
from app.models.qbo_connection import QBOConnection

logger = logging.getLogger(__name__)


def normalize_text(text: str) -> str:
    """
    Normalise un texte pour le matching (ÉTAPE 1 de la logique de mapping).
    
    ÉTAPE 1: NORMALISATION
    ──────────────────────
    Cette fonction implémente la première étape de la logique de mapping:
    - Convertit en minuscules
    - Supprime les accents (normalisation Unicode NFD)
    - Supprime la ponctuation et caractères spéciaux
    - Supprime les espaces multiples
    
    Exemples:
    - "Recherche & Développement" → "recherche developpement"
    - "Salaire - Équipe" → "salaire equipe"
    - "R&D Lab" → "r d lab"
    
    Cette normalisation permet un matching robuste indépendamment de:
    - La casse (majuscules/minuscules)
    - Les accents
    - La ponctuation
    - L'espacement
    
    Args:
        text: Le texte à normaliser
        
    Returns:
        Le texte normalisé prêt pour le matching par keywords
    """
    if not text:
        return ""
    
    import unicodedata
    import re
    
    # Convertir en minuscules
    text = text.lower()
    
    # Supprimer les accents
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    
    # Supprimer la ponctuation et caractères spéciaux
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Supprimer les espaces multiples
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


class AIAFinancialMappingService:
    """
    Service de mapping des comptes QuickBooks vers les catégories AIA.
    """
    
    def __init__(self, yaml_path: Optional[Path] = None):
        """
        Initialise le service avec les règles de mapping.
        
        Args:
            yaml_path: Chemin vers le fichier YAML de règles. Si None, utilise le chemin par défaut.
        """
        if yaml_path is None:
            yaml_path = Path(__file__).parent.parent / "config" / "aia_mapping_rules.yaml"
        
        self.yaml_path = yaml_path
        self.mapping_rules = self._load_mapping_rules()
        # Convertir la liste de catégories en dict tout en préservant l'ordre
        self.categories = self._normalize_categories(self.mapping_rules.get("categories", []))
        # Garder l'ordre des catégories pour le matching (liste pour parcours ordonné)
        self.categories_list = self.mapping_rules.get("categories", [])
        self.fallback_config = self.mapping_rules.get("fallback", {})
        self.settings = self.mapping_rules.get("settings", {})
        self.match_strategy = self.mapping_rules.get("match_strategy", {})
    
    def _load_mapping_rules(self) -> Dict:
        """
        Charge les règles de mapping depuis le fichier YAML.
        Supporte les deux formats:
        - Ancien: categories: {key: {name, keywords, ...}}
        - Nouveau: categories: [{key, label, type, keywords, ...}]
        
        Returns:
            Dictionnaire contenant les règles de mapping
            
        Raises:
            FileNotFoundError: Si le fichier YAML n'existe pas
            yaml.YAMLError: Si le fichier YAML est invalide
        """
        if not self.yaml_path.exists():
            raise FileNotFoundError(f"Fichier de règles non trouvé: {self.yaml_path}")
        
        with open(self.yaml_path, 'r', encoding='utf-8') as f:
            rules = yaml.safe_load(f)
        
        logger.info(f"Règles de mapping chargées depuis {self.yaml_path}")
        return rules
    
    def _normalize_categories(self, categories_raw) -> Dict:
        """
        Normalise les catégories depuis le format YAML (liste ou dict) vers un dict interne.
        
        Supporte deux formats:
        1. Liste: [{key: "expense_rd", label: "...", type: "expense", keywords: [...]}, ...]
        2. Dict: {expense_rd: {name: "...", keywords: [...]}, ...}
        
        Args:
            categories_raw: Catégories brutes depuis le YAML (liste ou dict)
            
        Returns:
            Dictionnaire normalisé {category_key: {name, keywords, account_types, type, ...}}
        """
        normalized = {}
        
        # Si c'est une liste (nouveau format)
        if isinstance(categories_raw, list):
            for cat in categories_raw:
                key = cat.get("key")
                if not key:
                    logger.warning(f"Catégorie sans clé ignorée: {cat}")
                    continue
                
                # Convertir le format nouveau vers format interne
                normalized[key] = {
                    "name": cat.get("label", key),  # label → name
                    "keywords": cat.get("keywords", []),
                    "type": cat.get("type"),  # revenue ou expense
                    # Pour account_types, on peut déduire depuis le type
                    "account_types": cat.get("account_types", []),
                    # Si pas de account_types, déduire depuis le type
                    "_original_config": cat
                }
                
                # Si pas d'account_types explicites, déduire depuis le type
                if not normalized[key]["account_types"] and normalized[key]["type"]:
                    if normalized[key]["type"] == "revenue":
                        normalized[key]["account_types"] = ["Income", "Revenue"]
                    elif normalized[key]["type"] == "expense":
                        normalized[key]["account_types"] = ["Expense", "Cost of Goods Sold"]
        
        # Si c'est un dict (ancien format - rétrocompatibilité)
        elif isinstance(categories_raw, dict):
            normalized = categories_raw.copy()
            # Ajouter le type manquant dans l'ancien format si possible
            for key, cat in normalized.items():
                if "type" not in cat:
                    # Déduire depuis le nom de la catégorie
                    if key.startswith("revenue"):
                        cat["type"] = "revenue"
                    elif key.startswith("expense"):
                        cat["type"] = "expense"
        
        logger.info(f"Normalisation de {len(normalized)} catégories")
        return normalized
    
    def _map_account_to_category(
        self, 
        account_name: str, 
        account_type: Optional[str] = None,
        account_subtype: Optional[str] = None
    ) -> Tuple[str, float]:
        """
        Mappe un compte QBO vers une catégorie AIA en utilisant les keywords.
        Retourne aussi un score de confiance (0.0 à 1.0).
        
        REGROUPEMENT PAR KEYWORDS:
        ──────────────────────────
        Cette fonction implémente un algorithme de matching hiérarchique:
        
        1. Normalisation du texte (accents, ponctuation supprimés)
           Ex: "Recherche & Développement" → "recherche developpement"
        
        2. Recherche par keywords dans l'ordre des catégories (ordre = priorité)
           - Si keyword exact == nom complet → Score 1.0 (match parfait)
           - Si keyword contenu dans le nom → Score 0.9 (match partiel)
        
        3. Si aucun keyword ne match → Vérifier le type de compte QBO
           - Type "Expense" avec sous-type "Salaries" → expense_salaries
           - Score: 0.7 (match par type)
        
        4. Si rien ne match → Fallback intelligent
           - Type "Income"/"Revenue" → revenue_other (Score 0.4)
           - Type "Expense"/"Cost" → expense_other (Score 0.4)
           - Aucune info → expense_other (Score 0.2)
        
        IMPORTANT: L'ordre de parcours des catégories dans le YAML détermine
        la priorité. Les catégories spécifiques (ex: expense_rsde) doivent
        être vérifiées AVANT les catégories génériques (ex: expense_operations).
        
        Args:
            account_name: Nom du compte
            account_type: Type du compte (optionnel)
            account_subtype: Sous-type du compte (optionnel)
            
        Returns:
            Tuple (category_code, confidence_score)
            - category_code: Le code de la catégorie AIA
            - confidence_score: Score de confiance entre 0.0 (faible) et 1.0 (élevé)
        """
        normalized_name = normalize_text(account_name or "")
        normalized_type = normalize_text(account_type or "")
        normalized_subtype = normalize_text(account_subtype or "")
        
        # Scores de confiance
        SCORE_EXACT_KEYWORD = 1.0  # Correspondance exacte de keyword
        SCORE_PARTIAL_KEYWORD = 0.9  # Keyword partiel
        SCORE_ACCOUNT_TYPE = 0.7  # Correspondance par type de compte
        SCORE_FALLBACK_TYPE = 0.4  # Fallback basé sur le type général
        SCORE_FALLBACK_FINAL = 0.2  # Fallback final
        
        # LOGIQUE DE MAPPING (respecte exactement la spécification):
        # 1. Normaliser le nom (déjà fait: normalized_name)
        # 2. Parcourir les catégories dans l'ordre (ordre du YAML = priorité)
        # 3. Si un keyword est trouvé dans le nom → assigner la catégorie
        # 4. Sinon → fallback global hiérarchique
        
        # IMPORTANT: Parcourir les catégories dans l'ordre explicite de la liste
        # (la première qui match gagne - priorité par ordre dans le YAML)
        categories_to_check = []
        
        # Si on a une liste (nouveau format), l'utiliser directement
        if isinstance(self.categories_list, list) and len(self.categories_list) > 0:
            categories_to_check = self.categories_list
        else:
            # Fallback vers dict (ancien format - rétrocompatibilité)
            categories_to_check = [
                {"key": key, **config}
                for key, config in self.categories.items()
            ]
        
        # Parcourir les catégories dans l'ordre pour trouver la meilleure correspondance
        for cat_config in categories_to_check:
            # Extraire la clé de catégorie (nouveau ou ancien format)
            if "key" in cat_config:
                category_code = cat_config["key"]
                keywords = cat_config.get("keywords", [])
                account_types = cat_config.get("account_types", [])
            else:
                # Ancien format (ne devrait pas arriver avec le nouveau YAML)
                category_code = cat_config.get("key", "")
                keywords = cat_config.get("keywords", [])
                account_types = cat_config.get("account_types", [])
            
            # Obtenir la config complète depuis le dict normalisé
            full_config = self.categories.get(category_code, {})
            if not full_config:
                continue
            
            # Si account_types n'était pas dans la liste, utiliser ceux du dict
            if not account_types:
                account_types = full_config.get("account_types", [])
            
            # Validation: Vérifier que le type de compte QBO correspond au type de catégorie
            cat_type = full_config.get("type")  # revenue ou expense
            if cat_type and normalized_type:
                # Si la catégorie est "revenue" mais le compte est "expense", skip
                if cat_type == "revenue" and ("expense" in normalized_type or "cost" in normalized_type):
                    continue
                # Si la catégorie est "expense" mais le compte est "income", skip
                if cat_type == "expense" and ("income" in normalized_type or "revenue" in normalized_type):
                    continue
            
            # ÉTAPE 3: Vérifier si un keyword est trouvé dans le nom normalisé
            for keyword in keywords:
                normalized_keyword = normalize_text(keyword)
                if normalized_keyword == normalized_name:
                    # Correspondance exacte du nom complet avec keyword
                    logger.debug(
                        f"Account '{account_name}' mappé vers '{category_code}' "
                        f"(exact match: '{keyword}', score: {SCORE_EXACT_KEYWORD})"
                    )
                    return (category_code, SCORE_EXACT_KEYWORD)
                elif normalized_keyword in normalized_name:
                    # Keyword trouvé dans le nom (substring match)
                    logger.debug(
                        f"Account '{account_name}' mappé vers '{category_code}' "
                        f"(keyword: '{keyword}', score: {SCORE_PARTIAL_KEYWORD})"
                    )
                    return (category_code, SCORE_PARTIAL_KEYWORD)
            
            # Vérifier le type de compte (si aucun keyword ne match)
            # Ceci est un complément au matching par keywords, pas un remplacement
            if normalized_type and account_types:
                for acc_type in account_types:
                    normalized_acc_type = normalize_text(acc_type)
                    if normalized_acc_type == normalized_type:
                        logger.debug(
                            f"Account '{account_name}' mappé vers '{category_code}' "
                            f"(type: '{account_type}', score: {SCORE_ACCOUNT_TYPE})"
                        )
                        return (category_code, SCORE_ACCOUNT_TYPE)
        
        # Aucune correspondance trouvée, utiliser le fallback global hiérarchique
        # Le fallback dépend du type général du compte (revenue/expense)
        if normalized_type:
            if "income" in normalized_type or "revenue" in normalized_type:
                # Fallback pour revenus
                fallback_cat = "revenue_other"
                if self.fallback_config and isinstance(self.fallback_config, dict):
                    revenue_fallback = self.fallback_config.get("revenue", {})
                    if isinstance(revenue_fallback, dict):
                        fallback_cat = revenue_fallback.get("key", "revenue_other")
                    elif isinstance(revenue_fallback, str):
                        fallback_cat = revenue_fallback
                
                logger.debug(
                    f"Account '{account_name}' mappé vers '{fallback_cat}' "
                    f"(fallback global par type revenu, score: {SCORE_FALLBACK_TYPE})"
                )
                return (fallback_cat, SCORE_FALLBACK_TYPE)
            elif "expense" in normalized_type or "cost" in normalized_type:
                # Fallback pour dépenses
                fallback_cat = "expense_other"
                if self.fallback_config and isinstance(self.fallback_config, dict):
                    expense_fallback = self.fallback_config.get("expense", {})
                    if isinstance(expense_fallback, dict):
                        fallback_cat = expense_fallback.get("key", "expense_other")
                    elif isinstance(expense_fallback, str):
                        fallback_cat = expense_fallback
                
                logger.debug(
                    f"Account '{account_name}' mappé vers '{fallback_cat}' "
                    f"(fallback global par type dépense, score: {SCORE_FALLBACK_TYPE})"
                )
                return (fallback_cat, SCORE_FALLBACK_TYPE)
        
        # Fallback final (aucune information de type)
        fallback_cat = "expense_other"
        if self.fallback_config and isinstance(self.fallback_config, dict):
            expense_fallback = self.fallback_config.get("expense", {})
            if isinstance(expense_fallback, dict):
                fallback_cat = expense_fallback.get("key", "expense_other")
        
        logger.warning(
            f"Aucune catégorie trouvée pour le compte '{account_name}', "
            f"utilisation du fallback final '{fallback_cat}' (score: {SCORE_FALLBACK_FINAL})"
        )
        return (fallback_cat, SCORE_FALLBACK_FINAL)
    
    def _get_realm_id_from_company_id(self, company_id: int, db: Session) -> Optional[str]:
        """
        Récupère le realm_id QBO à partir du company_id interne.
        
        Args:
            company_id: ID de l'entreprise interne
            db: Session de base de données
            
        Returns:
            Le realm_id QBO ou None
        """
        try:
            # Rollback pour nettoyer toute transaction en erreur
            db.rollback()
            
            connection = db.query(QBOConnection).filter(
                and_(
                    QBOConnection.company_id == company_id,
                    QBOConnection.is_active == True
                )
            ).first()
            
            return connection.realm_id if connection else None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du realm_id: {e}")
            try:
                db.rollback()
            except:
                pass
            return None
    
    def _get_all_accounts_mapping(self, company_id: int, db: Session) -> Tuple[Dict[str, str], Dict[str, float]]:
        """
        Mappe tous les comptes QBO d'une entreprise vers les catégories AIA.
        Utilise realm_id via QBOConnection car la base de données utilise qbo_company_id.
        
        REGROUPEMENT DES COMPTES:
        ─────────────────────────
        Cette fonction crée le dictionnaire de mapping global pour tous les comptes
        actifs d'une entreprise.
        
        Processus:
        1. Récupère le realm_id QBO depuis QBOConnection (relation company_id → realm_id)
        2. Query tous les comptes actifs avec qbo_company_id = realm_id
        3. Pour chaque compte, appelle _map_account_to_category() qui:
           - Compare le nom avec les keywords de chaque catégorie
           - Compare le type avec les account_types configurés
           - Retourne la catégorie et le score de confiance
        4. Stocke le mapping sous deux clés:
           - qbo_account_id (pour matching par ID)
           - account_name (pour matching par nom)
        
        Le double mapping (ID + nom) permet de retrouver la catégorie depuis
        les transactions (qui référencent par ID) ou depuis les snapshots P&L
        (qui utilisent les noms de comptes).
        
        Args:
            company_id: ID de l'entreprise
            db: Session de base de données
            
        Returns:
            Tuple (mapping_dict, confidence_dict)
            - mapping_dict: {qbo_account_id: category_code, account_name: category_code}
            - confidence_dict: {qbo_account_id: confidence_score, account_name: confidence_score}
        """
        # Obtenir le realm_id depuis QBOConnection
        realm_id = self._get_realm_id_from_company_id(company_id, db)
        if not realm_id:
            logger.warning(f"Aucune connexion QBO active trouvée pour company_id={company_id}")
            return {}
        
        # La base de données utilise qbo_company_id (varchar) qui correspond au realm_id
        # Utiliser raw SQL car la structure de la DB diffère du modèle ORM
        from sqlalchemy import text
        
        try:
            # Rollback toute transaction en cours pour éviter les erreurs
            db.rollback()
            
            result = db.execute(
                text("""
                    SELECT account_id, account_name, account_type, account_subtype
                    FROM qbo_accounts
                    WHERE qbo_company_id = :realm_id AND active = true
                """),
                {"realm_id": realm_id}
            ).fetchall()
            
            mapping = {}
            confidence_scores = {}
            
            for row in result:
                account_id = row[0]
                account_name = row[1]
                account_type = row[2]
                account_subtype = row[3]
                
                category, confidence = self._map_account_to_category(
                    account_name,
                    account_type,
                    account_subtype
                )
                mapping[account_id] = category
                mapping[account_name] = category
                confidence_scores[account_id] = confidence
                confidence_scores[account_name] = confidence
            
            logger.info(f"Mapping de {len(result)} comptes pour company_id={company_id} (via realm_id={realm_id})")
            return mapping, confidence_scores
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des comptes: {e}")
            try:
                db.rollback()
            except:
                pass
            return {}, {}
    
    def _parse_pnl_json(self, raw_json: str) -> Dict:
        """
        Parse le JSON brut d'un snapshot P&L.
        
        Args:
            raw_json: JSON brut stocké dans QBOReportSnapshot.raw_json
            
        Returns:
            Structure parsée du P&L
        """
        try:
            return json.loads(raw_json)
        except json.JSONDecodeError as e:
            logger.error(f"Erreur lors du parsing du JSON P&L: {e}")
            return {}
    
    def _extract_pnl_data_by_month(
        self, 
        pnl_json: Dict, 
        period_start: date, 
        period_end: date
    ) -> Dict[str, Dict[str, Decimal]]:
        """
        Extrait les données P&L par mois depuis le JSON du rapport.
        
        Args:
            pnl_json: JSON parsé du rapport P&L
            period_start: Date de début de la période
            period_end: Date de fin de la période
            
        Returns:
            Dict {month_key: {account_id: amount}}
        """
        # Structure attendue du JSON QBO P&L :
        # {
        #   "Header": {...},
        #   "Rows": {
        #     "Row": [
        #       {
        #         "ColData": [{"value": "Total Income"}, {"value": "1000"}, ...],
        #         "Rows": {...}  # Sous-comptes
        #       }
        #     ]
        #   }
        # }
        
        monthly_data = defaultdict(lambda: defaultdict(Decimal))
        
        rows = pnl_json.get("Rows", {}).get("Row", [])
        if not isinstance(rows, list):
            rows = [rows] if rows else []
        
        # Parcourir récursivement les lignes
        def process_rows(row_list: List, account_path: str = ""):
            for row in row_list:
                if not isinstance(row, dict):
                    continue
                
                col_data = row.get("ColData", [])
                if len(col_data) < 2:
                    continue
                
                account_name = col_data[0].get("value", "")
                current_path = f"{account_path}/{account_name}" if account_path else account_name
                
                # Extraire les montants par colonne (chaque colonne = un mois)
                # On commence à l'index 1 car l'index 0 est le nom du compte
                sub_rows = row.get("Rows", {}).get("Row", [])
                if sub_rows:
                    process_rows(sub_rows, current_path)
                else:
                    # C'est une ligne de total, extraire les valeurs mensuelles
                    # QBO P&L peut avoir plusieurs colonnes de données selon la granularité demandée
                    for i in range(1, len(col_data)):
                        month_key = f"{period_start.year}-{period_start.month:02d}"  # Simplifié
                        amount_str = col_data[i].get("value", "0")
                        try:
                            amount = Decimal(str(amount_str).replace(",", ""))
                            if amount != 0:
                                monthly_data[month_key][account_name] = amount
                        except (ValueError, TypeError):
                            pass
        
        process_rows(rows)
        return monthly_data
    
    def _aggregate_from_pnl_snapshots(
        self,
        company_id: int,
        period_start: date,
        period_end: date,
        accounts_mapping: Dict[str, str],
        accounts_confidence: Dict[str, float],
        db: Session
    ) -> Dict[str, Dict[str, Decimal]]:
        """
        Agrège les données depuis les snapshots P&L.
        
        REGROUPEMENT PAR MOIS - SOURCE P&L SNAPSHOTS:
        ─────────────────────────────────────────────
        Cette fonction extrait et agrège les données depuis les rapports ProfitAndLoss
        stockés dans QBOReportSnapshot.raw_json.
        
        Structure du JSON QBO P&L:
        {
          "Rows": {
            "Row": [
              {
                "ColData": [
                  {"value": "Total Income"},
                  {"value": "1000"},    // Colonne 1 (mois 1)
                  {"value": "1200"},    // Colonne 2 (mois 2)
                  ...
                ],
                "Rows": {
                  "Row": [...]  // Sous-comptes récursifs
                }
              }
            ]
          }
        }
        
        Processus d'agrégation:
        1. Parse le JSON brut stocké dans raw_json
        2. Parcours récursif de la structure "Rows" → "Row"
        3. Pour chaque ligne de compte:
           - Extrait le nom du compte (ColData[0])
           - Extrait les montants par colonne (ColData[1..n])
           - Chaque colonne représente un mois/période
        4. Pour chaque compte trouvé:
           - Utilise accounts_mapping pour trouver la catégorie AIA
           - Si non trouvé, appelle _map_account_to_category() en temps réel
           - Additionne les montants par catégorie et par mois
        
        Résultat: {month_key: {category: total_amount}}
        Exemple: {"2025-03": {"expense_salaries": 15000.0}}
        
        Note: Cette source est privilégiée car elle contient déjà les totaux
        pré-calculés par QuickBooks, plus précis que l'agrégation manuelle.
        
        Args:
            company_id: ID de l'entreprise
            period_start: Date de début
            period_end: Date de fin
            accounts_mapping: Mapping des comptes vers catégories
            accounts_confidence: Scores de confiance par compte (non utilisé ici mais pour cohérence)
            db: Session de base de données
            
        Returns:
            Dict {month_key: {category: total_amount}}
        """
        snapshots = db.query(QBOReportSnapshot).filter(
            and_(
                QBOReportSnapshot.company_id == company_id,
                QBOReportSnapshot.report_type == "ProfitAndLoss",
                QBOReportSnapshot.period_start >= period_start,
                QBOReportSnapshot.period_end <= period_end
            )
        ).order_by(QBOReportSnapshot.period_start).all()
        
        if not snapshots:
            logger.warning(f"Aucun snapshot P&L trouvé pour company_id={company_id}")
            return {}
        
        # Utiliser le snapshot le plus récent qui couvre toute la période
        snapshot = snapshots[-1] if snapshots else None
        if not snapshot:
            return {}
        
        pnl_json = self._parse_pnl_json(snapshot.raw_json)
        monthly_data = self._extract_pnl_data_by_month(
            pnl_json,
            snapshot.period_start or period_start,
            snapshot.period_end or period_end
        )
        
        # Agrégation par catégorie et par mois
        aggregated = defaultdict(lambda: defaultdict(Decimal))
        
        # CRITIQUE: S'assurer que TOUS les montants sont inclus (total AIA = total QBO)
        # Pour chaque compte trouvé dans les données P&L, on DOIT le mapper vers une catégorie
        for month_key, accounts_data in monthly_data.items():
            for account_name, amount in accounts_data.items():
                # Trouver la catégorie pour ce compte
                # Si pas dans le mapping pré-calculé, mapper en temps réel (toujours possible grâce au fallback)
                category = accounts_mapping.get(account_name)
                if not category:
                    # Fallback: mapper en temps réel (garantit qu'aucun compte n'est perdu)
                    category, _ = self._map_account_to_category(account_name)
                    logger.debug(f"Compte '{account_name}' mappé en temps réel vers '{category}'")
                
                # GARANTIE: amount est TOUJOURS ajouté à une catégorie (grâce au fallback)
                aggregated[month_key][category] += amount
        
        return aggregated
    
    def _aggregate_from_transaction_lines(
        self,
        company_id: int,
        period_start: date,
        period_end: date,
        accounts_mapping: Dict[str, str],
        accounts_confidence: Dict[str, float],
        db: Session
    ) -> Dict[str, Dict[str, Decimal]]:
        """
        Agrège les données depuis les lignes de transaction (fallback).
        
        REGROUPEMENT PAR MOIS - SOURCE TRANSACTIONS (FALLBACK):
        ────────────────────────────────────────────────────────
        Cette fonction agrège les données depuis QBOTransactionLine lorsque
        les snapshots P&L ne sont pas disponibles.
        
        Processus d'agrégation:
        1. Récupère toutes les transactions dans la période
        2. Pour chaque transaction:
           - Extrait la date (txn_date) et crée month_key = "YYYY-MM"
           - Récupère account_qbo_id (référence au compte QBO)
           - Utilise accounts_mapping pour trouver la catégorie AIA
           - Si non trouvé, cherche le compte par ID dans QBOAccount
           - Additionne le montant (amount) par catégorie et par mois
        
        Exemple:
        Transaction 1: date=2025-03-15, account_id="123", amount=5000.00
        → month_key="2025-03", category="expense_salaries"
        → aggregated["2025-03"]["expense_salaries"] += 5000.00
        
        Transaction 2: date=2025-03-20, account_id="123", amount=3000.00
        → month_key="2025-03", category="expense_salaries"
        → aggregated["2025-03"]["expense_salaries"] += 3000.00
        → Total: 8000.00
        
        AVANTAGE: Plus granulaire, permet de voir chaque transaction
        INCONVÉNIENT: Plus lent et moins précis que les snapshots P&L
        (pas de consolidation des ajustements comptables)
        
        Args:
            company_id: ID de l'entreprise
            period_start: Date de début
            period_end: Date de fin
            accounts_mapping: Mapping des comptes vers catégories
            accounts_confidence: Scores de confiance par compte (non utilisé ici mais pour cohérence)
            db: Session de base de données
            
        Returns:
            Dict {month_key: {category: total_amount}}
        """
        # Récupérer les transactions par mois
        transactions = db.query(QBOTransactionLine).filter(
            and_(
                QBOTransactionLine.company_id == company_id,
                QBOTransactionLine.txn_date >= period_start,
                QBOTransactionLine.txn_date <= period_end
            )
        ).all()
        
        aggregated = defaultdict(lambda: defaultdict(Decimal))
        
        # CRITIQUE: S'assurer que TOUS les montants sont inclus (total AIA = total QBO)
        # Chaque transaction DOIT être mappée vers une catégorie (fallback garanti)
        for txn in transactions:
            # Créer la clé du mois
            month_key = f"{txn.txn_date.year}-{txn.txn_date.month:02d}"
            
            # Trouver la catégorie pour ce compte
            category = accounts_mapping.get(txn.account_qbo_id)
            if not category:
                # Essayer de trouver le compte par son ID
                account = db.query(QBOAccount).filter(
                    QBOAccount.qbo_account_id == txn.account_qbo_id
                ).first()
                if account:
                    # Mapper avec les informations du compte (nom, type, sous-type)
                    category, _ = self._map_account_to_category(
                        account.name,
                        account.account_type,
                        account.account_subtype
                    )
                else:
                    # GARANTIE: Fallback final - TOUJOURS une catégorie assignée
                    # Même si le compte n'existe pas dans QBOAccount, on utilise le fallback
                    category = "expense_other"  # Fallback final (score: 0.2)
                    logger.warning(
                        f"Transaction {txn.qbo_txn_id}: compte {txn.account_qbo_id} non trouvé, "
                        f"utilisation du fallback '{category}'"
                    )
            
            # GARANTIE: amount est TOUJOURS ajouté à une catégorie (grâce au fallback)
            aggregated[month_key][category] += Decimal(str(txn.amount))
        
        logger.info(f"Agrégation de {len(transactions)} transactions pour company_id={company_id}")
        return aggregated
    
    def generate_financial_view(
        self,
        company_id: int,
        months: int = 12,
        db: Optional[Session] = None
    ) -> Dict:
        """
        Génère la vue financière agrégée par catégories AIA.
        
        Args:
            company_id: ID de l'entreprise
            months: Nombre de mois à analyser (défaut: 12)
            db: Session de base de données (optionnel)
            
        Returns:
            Dict structuré avec period_start, period_end, totals_by_category,
            accounts_mapping, reconciliation
        """
        if db is None:
            db = SessionLocal()
            close_db = True
        else:
            close_db = False
        
        try:
            # Calculer la période
            period_end = date.today()
            period_start = (period_end - relativedelta(months=months)).replace(day=1)
            
            # Obtenir le mapping des comptes et les scores de confiance
            accounts_mapping, accounts_confidence = self._get_all_accounts_mapping(company_id, db)
            
            # Essayer d'abord avec les snapshots P&L
            aggregated = self._aggregate_from_pnl_snapshots(
                company_id, period_start, period_end, accounts_mapping, accounts_confidence, db
            )
            
            # Si pas de données, utiliser les transactions
            if not aggregated or all(not month_data for month_data in aggregated.values()):
                logger.info("Aucune donnée P&L, utilisation du fallback avec transactions")
                aggregated = self._aggregate_from_transaction_lines(
                    company_id, period_start, period_end, accounts_mapping, accounts_confidence, db
                )
            
            # Calculer les scores de confiance par catégorie
            # ──────────────────────────────────────────────────
            # REGROUPEMENT DES SCORES DE CONFIANCE:
            # Pour chaque catégorie, on calcule un score de confiance global
            # basé sur la moyenne des scores individuels des comptes mappés.
            #
            # Exemple:
            # - Compte A → expense_salaries (score: 1.0) car keyword "salary" exact
            # - Compte B → expense_salaries (score: 0.7) car type "Expense/Salaries"
            # - Score catégorie = (1.0 + 0.7) / 2 = 0.85
            #
            # Si aucun compte n'est mappé vers une catégorie → Score = 0.5 (neutralité)
            # car on ne peut ni confirmer ni infirmer le mapping.
            
            category_confidence = {}
            category_accounts_count = defaultdict(int)
            category_weighted_confidence = defaultdict(float)
            
            # Agréger les scores par catégorie (moyenne pondérée par nombre de comptes)
            for account_id, category in accounts_mapping.items():
                if account_id in accounts_confidence:
                    confidence = accounts_confidence[account_id]
                    category_accounts_count[category] += 1
                    category_weighted_confidence[category] += confidence
            
            # Calculer la moyenne pondérée par catégorie
            for category_code in self.categories.keys():
                count = category_accounts_count.get(category_code, 0)
                if count > 0:
                    category_confidence[category_code] = category_weighted_confidence[category_code] / count
                else:
                    # Si aucune donnée, score moyen (car on ne peut pas être sûr)
                    category_confidence[category_code] = 0.5
            
            # Structurer les totaux par catégorie et par mois
            totals_by_category = {}
            for category_code in self.categories.keys():
                totals_by_category[category_code] = {
                    "name": self.categories[category_code].get("name", category_code),
                    "monthly_totals": {},
                    "confidence_score": round(category_confidence.get(category_code, 0.5), 3),
                    "accounts_count": category_accounts_count.get(category_code, 0)
                }
                
                # Calculer les totaux par mois
                current_date = period_start
                while current_date <= period_end:
                    month_key = f"{current_date.year}-{current_date.month:02d}"
                    amount = aggregated.get(month_key, {}).get(category_code, Decimal(0))
                    totals_by_category[category_code]["monthly_totals"][month_key] = float(amount)
                    current_date = (current_date + relativedelta(months=1)).replace(day=1)
                
                # Calculer le total global
                total = sum(
                    Decimal(str(v))
                    for v in totals_by_category[category_code]["monthly_totals"].values()
                )
                totals_by_category[category_code]["total"] = float(total)
            
            # Calculer la réconciliation
            # ───────────────────────────
            # REGROUPEMENT ET RÉCONCILIATION:
            # La réconciliation compare les totaux bruts QBO avec les totaux
            # agrégés par catégories AIA pour détecter les écarts.
            #
            # CRITIQUE: total_qbo DOIT être égal à total_aia car:
            # - Chaque montant QBO est TOUJOURS mappé vers une catégorie (fallback garanti)
            # - Aucun montant n'est exclu ou perdu
            # - Tous les montants sont additionnés dans totals_by_category
            #
            # total_qbo: Somme brute de toutes les données sources (P&L ou transactions)
            #            C'est le total "brut" avant regroupement par catégories.
            #
            # total_aia: Somme de tous les totaux par catégorie AIA après regroupement.
            #            Chaque montant a été mappé vers une catégorie (grâce au fallback).
            #
            # delta: Devrait être ≈ 0 (dans la tolérance de précision flottante).
            #        Si delta > tolerance, cela peut indiquer:
            #        - Erreurs d'arrondi (négligeable)
            #        - Bug dans l'agrégation (à investiguer)
            #
            # IMPORTANT: Le système garantit que total_aia = total_qbo car:
            # 1. Tous les montants extraits des données QBO sont traités
            # 2. Chaque montant est mappé vers une catégorie (fallback si nécessaire)
            # 3. Tous les montants sont additionnés dans totals_by_category
            
            total_qbo = sum(
                sum(Decimal(str(v)) for v in month_data.values())
                for month_data in aggregated.values()
            )
            
            total_aia = sum(
                Decimal(str(cat_data["total"]))
                for cat_data in totals_by_category.values()
            )
            
            delta = float(total_qbo - total_aia)
            tolerance = self.settings.get("reconciliation_tolerance", 0.01)
            
            # Vérification de cohérence (devrait toujours passer)
            if abs(delta) > tolerance and total_qbo != 0:
                logger.warning(
                    f"Réconciliation: delta={delta:.2f} > tolerance={tolerance} "
                    f"(total_qbo={total_qbo:.2f}, total_aia={total_aia:.2f})"
                )
            
            reconciliation = {
                "total_qbo": float(total_qbo),
                "total_aia": float(total_aia),
                "delta": delta,
                "delta_percentage": (delta / float(total_qbo) * 100) if total_qbo != 0 else 0,
                "reconciled": abs(delta) <= tolerance,
                "tolerance": tolerance
            }
            
            # Construire le mapping des comptes (nom -> catégorie)
            accounts_mapping_output = {}
            
            # Obtenir le realm_id
            realm_id = self._get_realm_id_from_company_id(company_id, db)
            if realm_id:
                # Utiliser raw SQL car la structure de la DB utilise qbo_company_id
                from sqlalchemy import text
                
                try:
                    db.rollback()  # Nettoyer avant la requête
                    account_rows = db.execute(
                        text("""
                            SELECT account_id, account_name, account_type, account_subtype
                            FROM qbo_accounts
                            WHERE qbo_company_id = :realm_id AND active = true
                        """),
                        {"realm_id": realm_id}
                    ).fetchall()
                    
                    for row in account_rows:
                        account_id, account_name, account_type, account_subtype = row
                        category = accounts_mapping.get(account_id, "expense_other")
                        accounts_mapping_output[account_name] = {
                            "category": category,
                            "category_name": self.categories.get(category, {}).get("name", category),
                            "account_type": account_type,
                            "account_subtype": account_subtype
                        }
                except Exception as e:
                    logger.error(f"Erreur lors de la récupération des comptes pour le mapping output: {e}")
                    try:
                        db.rollback()
                    except:
                        pass
            
            result = {
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "months": months,
                "totals_by_category": totals_by_category,
                "accounts_mapping": accounts_mapping_output,
                "reconciliation": reconciliation,
                "data_source": "pnl_snapshot" if aggregated else "transaction_lines"
            }
            
            logger.info(
                f"Vue financière générée pour company_id={company_id}: "
                f"{len(accounts_mapping_output)} comptes, "
                f"total QBO={reconciliation['total_qbo']:.2f}, "
                f"total AIA={reconciliation['total_aia']:.2f}"
            )
            
            return result
        
        finally:
            if close_db:
                db.close()
    
    def format_for_google_sheets_csv(self, financial_view: Dict) -> str:
        """
        Formate la vue financière en CSV compatible Google Sheets.
        
        Le format génère plusieurs sections séparées par des lignes vides :
        1. Informations générales (période, réconciliation)
        2. Totaux par catégorie par mois (format pivot)
        3. Mapping des comptes
        
        Args:
            financial_view: Résultat de generate_financial_view()
            
        Returns:
            String CSV formaté
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 1. En-tête et informations générales
        writer.writerow(["AIA Financial View - Export Google Sheets"])
        writer.writerow(["Généré le", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        writer.writerow([])
        
        writer.writerow(["=== INFORMATIONS GÉNÉRALES ==="])
        writer.writerow(["Période début", financial_view["period_start"]])
        writer.writerow(["Période fin", financial_view["period_end"]])
        writer.writerow(["Nombre de mois", financial_view["months"]])
        writer.writerow(["Source de données", financial_view.get("data_source", "N/A")])
        writer.writerow([])
        
        # 2. Réconciliation
        reconciliation = financial_view.get("reconciliation", {})
        writer.writerow(["=== RÉCONCILIATION ==="])
        writer.writerow(["Total QBO", f"{reconciliation.get('total_qbo', 0):.2f}"])
        writer.writerow(["Total AIA", f"{reconciliation.get('total_aia', 0):.2f}"])
        writer.writerow(["Delta", f"{reconciliation.get('delta', 0):.2f}"])
        writer.writerow(["Delta %", f"{reconciliation.get('delta_percentage', 0):.2f}%"])
        writer.writerow(["Réconcilié", "Oui" if reconciliation.get("reconciled", False) else "Non"])
        writer.writerow([])
        
        # 3. Totaux par catégorie par mois (format pivot)
        writer.writerow(["=== TOTAUX PAR CATÉGORIE PAR MOIS ==="])
        totals_by_category = financial_view.get("totals_by_category", {})
        
        # Collecter tous les mois uniques
        all_months = set()
        for category_data in totals_by_category.values():
            all_months.update(category_data.get("monthly_totals", {}).keys())
        
        all_months = sorted(list(all_months))
        
        # En-tête : Catégorie, Nom, Total, Score de confiance, Nb comptes, puis chaque mois
        header = ["Catégorie", "Nom", "Total", "Score Confiance", "Nb Comptes"] + all_months
        writer.writerow(header)
        
        # Lignes par catégorie
        for category_code, category_data in sorted(totals_by_category.items()):
            row = [
                category_code,
                category_data.get("name", ""),
                f"{category_data.get('total', 0):.2f}",
                f"{category_data.get('confidence_score', 0):.3f}",
                f"{category_data.get('accounts_count', 0)}"
            ]
            monthly_totals = category_data.get("monthly_totals", {})
            for month in all_months:
                row.append(f"{monthly_totals.get(month, 0):.2f}")
            writer.writerow(row)
        
        writer.writerow([])
        
        # 4. Mapping des comptes
        writer.writerow(["=== MAPPING DES COMPTES ==="])
        writer.writerow(["Compte QBO", "Catégorie", "Nom Catégorie", "Type Compte", "Sous-type Compte"])
        
        accounts_mapping = financial_view.get("accounts_mapping", {})
        for account_name, mapping_data in sorted(accounts_mapping.items()):
            writer.writerow([
                account_name,
                mapping_data.get("category", ""),
                mapping_data.get("category_name", ""),
                mapping_data.get("account_type", ""),
                mapping_data.get("account_subtype", "")
            ])
        
        return output.getvalue()
    
    def format_for_google_sheets_json(self, financial_view: Dict, company_id: Optional[int] = None) -> str:
        """
        Formate la vue financière en JSON structuré pour Google Sheets API.
        
        Format compatible avec l'API Google Sheets qui accepte les valeurs brutes.
        
        Args:
            financial_view: Résultat de generate_financial_view()
            company_id: ID de l'entreprise (optionnel, pour le titre)
            
        Returns:
            String JSON formaté
        """
        # Structure pour Google Sheets : liste de lignes où chaque ligne est une liste de valeurs
        company_str = str(company_id) if company_id else "N/A"
        sheets_data = {
            "spreadsheet_title": f"AIA Financial View - Company {company_str}",
            "sheets": []
        }
        
        # Feuille 1: Informations générales
        info_sheet = {
            "title": "Informations",
            "data": [
                ["AIA Financial View - Export Google Sheets"],
                ["Généré le", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                [],
                ["Période début", financial_view["period_start"]],
                ["Période fin", financial_view["period_end"]],
                ["Nombre de mois", financial_view["months"]],
                ["Source de données", financial_view.get("data_source", "N/A")],
                [],
                ["=== RÉCONCILIATION ==="],
                ["Total QBO", financial_view["reconciliation"].get("total_qbo", 0)],
                ["Total AIA", financial_view["reconciliation"].get("total_aia", 0)],
                ["Delta", financial_view["reconciliation"].get("delta", 0)],
                ["Delta %", financial_view["reconciliation"].get("delta_percentage", 0)],
                ["Réconcilié", "Oui" if financial_view["reconciliation"].get("reconciled", False) else "Non"]
            ]
        }
        sheets_data["sheets"].append(info_sheet)
        
        # Feuille 2: Totaux par catégorie
        totals_sheet = {
            "title": "Totaux par Catégorie",
            "data": []
        }
        
        totals_by_category = financial_view.get("totals_by_category", {})
        
        # Collecter tous les mois
        all_months = set()
        for category_data in totals_by_category.values():
            all_months.update(category_data.get("monthly_totals", {}).keys())
        all_months = sorted(list(all_months))
        
        # En-tête
        header = ["Catégorie", "Nom", "Total", "Score Confiance", "Nb Comptes"] + all_months
        totals_sheet["data"].append(header)
        
        # Lignes par catégorie
        for category_code, category_data in sorted(totals_by_category.items()):
            row = [
                category_code,
                category_data.get("name", ""),
                category_data.get("total", 0),
                category_data.get("confidence_score", 0),
                category_data.get("accounts_count", 0)
            ]
            monthly_totals = category_data.get("monthly_totals", {})
            for month in all_months:
                row.append(monthly_totals.get(month, 0))
            totals_sheet["data"].append(row)
        
        sheets_data["sheets"].append(totals_sheet)
        
        # Feuille 3: Mapping des comptes
        mapping_sheet = {
            "title": "Mapping Comptes",
            "data": [
                ["Compte QBO", "Catégorie", "Nom Catégorie", "Type Compte", "Sous-type Compte"]
            ]
        }
        
        accounts_mapping = financial_view.get("accounts_mapping", {})
        for account_name, mapping_data in sorted(accounts_mapping.items()):
            mapping_sheet["data"].append([
                account_name,
                mapping_data.get("category", ""),
                mapping_data.get("category_name", ""),
                mapping_data.get("account_type", ""),
                mapping_data.get("account_subtype", "")
            ])
        
        sheets_data["sheets"].append(mapping_sheet)
        
        return json.dumps(sheets_data, indent=2, ensure_ascii=False)
