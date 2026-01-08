# Analyse et Améliorations du Questionnaire AIA - Hypothèses de Projection

## 📋 Structure Actuelle - Points Forts

✅ **Couverture complète** : Tous les aspects critiques sont couverts
✅ **Structuration logique** : Progression naturelle (contexte → revenus → coûts → R&D → financement → trésorerie)
✅ **Orientation utilisateur** : Questions claires et actionnables
✅ **Prudence ajustable** : L'AIA adapte selon le contexte (bancaire vs stratégique)

## 🎯 Améliorations Proposées

### 1. **VALEURS PAR DÉFAUT INTELLIGENTES** (Priorité Haute)

**Problème actuel** : L'utilisateur doit saisir toutes les valeurs manuellement

**Solution** :
- **Q1.2** : L'AIA pré-remplit les 3 scénarios basés sur l'historique
  - Conservateur : 50% de la croissance historique
  - Réaliste : 100% de la croissance historique
  - Ambitieux : 150% de la croissance historique
- **Q2.1** : Proposition d'inflation basée sur les indices économiques (ex: 2-3% par défaut)
- **Q3.2** : Calcul automatique du crédit RS&DE basé sur les dépenses R&D historiques
- **Q4.1** : Pré-remplissage automatique des dettes depuis QBO

**Code suggéré** :
```javascript
// Calcul automatique des scénarios de croissance
const historicalGrowth = calculateHistoricalGrowth(aiaData);
const scenarios = {
  conservative: historicalGrowth * 0.5,
  realistic: historicalGrowth,
  optimistic: historicalGrowth * 1.5
};
```

---

### 2. **PROGRESSION GUIDÉE (WIZARD)** (Priorité Haute)

**Problème actuel** : Toutes les questions en une seule page peut être intimidant

**Solution** :
- Interface en étapes (Step 0 → Step 6)
- Barre de progression visible
- Boutons "Précédent" / "Suivant" / "Sauvegarder et continuer plus tard"
- Aperçu récapitulatif avant validation finale

**Structure proposée** :
```
Step 0: Contexte (1 question)
Step 1: Revenus (4 questions)
Step 2: Coûts (3 questions)
Step 3: R&D (3 questions)
Step 4: Dette & Financement (3 questions)
Step 5: Trésorerie (3 questions)
Step 6: Scénarios (2 questions)
Step 7: Validation (récapitulatif)
```

---

### 3. **VALIDATION ET SUGGESTIONS EN TEMPS RÉEL** (Priorité Moyenne)

**Problème actuel** : Pas de validation avant la soumission finale

**Solution** :
- Validation de cohérence :
  - Si revenus croissent de 20% mais dépenses de 50% → Alerte "Attention: Dépenses croissent plus vite que revenus"
  - Si trésorerie minimale < 1 mois de coûts → Suggestion de hausse
  - Si crédit RS&DE > 50% des revenus → Vérification
- Suggestions contextuelles :
  - "Basé sur votre historique, nous suggérons X% pour la croissance des revenus"
  - "Attention: Vos dépenses R&D représentent Y% du total. Vérifiez l'éligibilité RS&DE"

---

### 4. **CATÉGORISATION PAR TYPE DE REVENUS** (Priorité Moyenne)

**Problème actuel** : Q1.1-Q1.4 sont génériques, pas spécifiques aux catégories AIA

**Solution** :
- Répéter Q1.1 à Q1.4 **pour chaque catégorie de revenus détectée** :
  - Revenus Licences (revenue_licenses)
  - Revenus Services (revenue_services)
  - Ventes de Produits (revenue_products)
  - Autres Revenus (revenue_other)
- Afficher l'historique de chaque catégorie pour aider la décision
- Permettre de "copier les hypothèses" d'une catégorie à l'autre

**Exemple** :
```
Q1.1 - Revenus Licences
Historique: $50k/mois, croissance +5%/an
☐ Récurrent ☐ Ponctuel ☐ Hybride

Q1.2 - Revenus Services
Historique: $30k/mois, croissance +15%/an
☐ Récurrent ☐ Ponctuel ☐ Hybride
```

---

### 5. **DÉCLENCHEURS AVANCÉS** (Priorité Moyenne)

**Problème actuel** : Q1.3 et Q2.3 permettent seulement un déclencheur à la fois

**Solution** :
- Permettre **plusieurs déclencheurs** :
  - Liste de déclencheurs (ajouter/supprimer)
  - Pour chaque déclencheur : Mois + Montant + Description
- Types de déclencheurs :
  - Nouveau contrat/licence
  - Nouveau produit/service
  - Embauche
  - Investissement équipement
  - Nouveau local
  - Restructuration

**Interface suggérée** :
```javascript
const triggers = [
  { type: 'revenue', month: 6, amount: 10000, description: 'Nouveau contrat Client X' },
  { type: 'expense', month: 9, amount: 5000, description: 'Embauche développeur' }
];
```

---

### 6. **SCÉNARIOS MULTIPLES AVEC COMPARAISON** (Priorité Haute)

**Problème actuel** : Q6.2 permet de comparer mais pas de visualiser la comparaison

**Solution** :
- Interface de comparaison côte-à-côte :
  - Graphiques superposés (3 courbes sur même graphique)
  - Tableau comparatif avec différences
  - Métriques clés comparées (trésorerie finale, profit cumulé, etc.)
- Export des scénarios en PDF/Excel pour présentation

---

### 7. **SAUVEGARDE ET VERSIONNEMENT** (Priorité Moyenne)

**Problème actuel** : Pas de sauvegarde mentionnée

**Solution** :
- Sauvegarde automatique en local (localStorage)
- Sauvegarde serveur (optionnel, nécessite authentification)
- Historique des versions :
  - Timestamp de chaque modification
  - Comparaison entre versions
  - Restauration d'une version antérieure
- Export des hypothèses en JSON/YAML pour traçabilité

---

### 8. **PRÉVISUALISATION DES IMPACTS** (Priorité Haute)

**Problème actuel** : L'utilisateur ne voit l'impact qu'après validation

**Solution** :
- **Aperçu en temps réel** pendant la saisie :
  - Graphique de prévisualisation mis à jour en live
  - Alertes visuelles (rouge/orange/vert) pour les risques
  - Calcul de la trésorerie finale estimée
- **Simulateur de scénarios** :
  - "Et si je change X à Y?" → Aperçu immédiat
  - Sensibilité (spider chart) : impact de chaque paramètre

---

### 9. **QUESTIONS CONDITIONNELLES** (Priorité Moyenne)

**Problème actuel** : Toutes les questions sont affichées, même si non applicables

**Solution** :
- **Q4.2** : Afficher seulement si Q4.1 = "Renégociation prévue" ou "Nouvelle dette"
- **Q4.3** : Afficher seulement si contexte = "Investisseurs / financement" ou trésorerie projetée négative
- **Q5.3** : Afficher seulement si Q5.2 = "Acceptable si plan clair"

---

### 10. **AMÉLIORATIONS UX/UI** (Priorité Basse mais Impact Élevé)

**Suggestions** :
- **Tooltips explicatifs** : "?" à côté de chaque question expliquant pourquoi c'est important
- **Exemples concrets** : "Exemple: Si vos revenus sont de $100k/mois et vous projetez +10%/an, vous aurez $110k/mois l'année prochaine"
- **Indicateurs visuels** :
  - ✅ Vert : Hypothèse réaliste
  - ⚠️ Orange : Hypothèse optimiste (prudence)
  - 🔴 Rouge : Hypothèse risquée (vérification recommandée)
- **Mode guidé vs Expert** :
  - Mode guidé : Questions simplifiées avec suggestions
  - Mode expert : Toutes les options avancées visibles

---

## 📊 Structure de Données Proposée

```typescript
interface ProjectionAssumptions {
  metadata: {
    version: string;
    createdAt: string;
    updatedAt: string;
    context: 'banking' | 'strategic' | 'investor' | 'operational' | 'other';
    prudenceLevel: 'low' | 'medium' | 'high'; // Calculé selon contexte
  };
  
  revenue: {
    categories: {
      [categoryKey: string]: {
        type: 'recurrent' | 'one-time' | 'hybrid';
        growth: {
          conservative: number;
          realistic: number;
          optimistic: number;
        };
        triggers: Array<{
          month: number;
          amount: number;
          description: string;
        }>;
        riskConcentration: 'diversified' | 'major-clients' | 'transition';
      };
    };
  };
  
  expenses: {
    globalEvolution: 'stable' | 'inflation' | 'optimization' | 'growth-linked';
    inflationRate?: number;
    optimizationRate?: number;
    fixedVsVariable: 'mostly-fixed' | 'mostly-variable' | 'mixed';
    triggers: Array<{
      month: number;
      amount: number;
      description: string;
      type: 'hiring' | 'equipment' | 'office' | 'other';
    }>;
  };
  
  rd: {
    allocation: {
      method: 'salary-percentage' | 'total-percentage' | 'project' | 'continuous';
      value: number;
    };
    credit: {
      estimated: number; // Calculé par AIA
      include: boolean;
      includeWithCaution?: boolean;
      cautionPercentage?: number;
    };
    reimbursementDelay: number; // mois
  };
  
  debt: {
    current: {
      projection: 'normal' | 'interest-only' | 'renegotiation' | 'frozen';
      interestOnlyMonths?: number;
    };
    new: Array<{
      amount: number;
      month: number;
      rate: number;
      description: string;
    }>;
  };
  
  equity: {
    possible: boolean;
    maxAmount?: number;
    certainty: 'certain' | 'conditional' | 'last-resort';
  };
  
  cash: {
    minThreshold: number;
    deficitTolerance: {
      acceptable: boolean;
      maxMonths?: number;
      ifPlanClear?: boolean;
    };
    priorityIfTight: 'reduce-costs' | 'accelerate-revenue' | 'inject-funds' | 'renegotiate-debt';
  };
  
  scenarios: {
    default: 'conservative' | 'realistic' | 'optimistic';
    compare: boolean;
    comparedScenarios?: Array<'conservative' | 'realistic' | 'optimistic'>;
  };
}
```

---

## 🚀 Plan d'Implémentation Recommandé

### Phase 1 (MVP - 2 semaines)
1. ✅ Structure de données
2. ✅ Interface wizard (étapes 0-7)
3. ✅ Valeurs par défaut intelligentes
4. ✅ Validation basique
5. ✅ Prévisualisation simple

### Phase 2 (Améliorations - 2 semaines)
6. ✅ Catégorisation par revenus
7. ✅ Déclencheurs multiples
8. ✅ Comparaison de scénarios
9. ✅ Sauvegarde locale

### Phase 3 (Avancé - 2 semaines)
10. ✅ Suggestions contextuelles (IA)
11. ✅ Analyse de sensibilité
12. ✅ Export PDF/Excel
13. ✅ Versionnement serveur

---

## 💡 Questions pour Affiner

1. **Priorité** : Quelle phase est la plus critique pour vous?
2. **Utilisateurs** : Principalement experts financiers ou non-experts?
3. **Intégration** : Souhaitez-vous intégrer ce questionnaire dans le simulateur existant ou le garder séparé?
4. **IA** : Souhaitez-vous que l'AIA génère automatiquement les hypothèses basées sur l'historique avec validation humaine?

---

## ✅ Conclusion

Le questionnaire est **excellent et bien structuré**. Les améliorations proposées visent à :
- 🎯 Réduire la friction (valeurs par défaut, progression guidée)
- 🧠 Aider la décision (suggestions, validation, prévisualisation)
- 📊 Faciliter l'analyse (comparaison de scénarios, export)
- 🔒 Assurer la traçabilité (versionnement, sauvegarde)

**Prochaine étape recommandée** : Implémenter Phase 1 (MVP) avec l'interface wizard et les valeurs par défaut intelligentes.
