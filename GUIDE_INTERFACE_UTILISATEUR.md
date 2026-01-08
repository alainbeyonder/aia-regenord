# Guide de l'Interface Utilisateur - AIA Regenord

## 📱 Vue d'ensemble de l'interface

L'interface utilisateur est accessible sur **http://localhost:3000** et propose une expérience complète pour la gestion financière avec QuickBooks Online.

---

## 🏠 Page d'accueil - Dashboard

### En-tête
- **Titre**: 📊 AIA Regenord
- **Sous-titre**: Agent IA Financier - Projections Financières 3 Ans
- **Organisation**: Groupe Regenord

### Bannière de statut
- Indicateur de connexion au backend (✅/❌)
- Message de statut

### Cartes principales (grille responsive)

#### 1. 🔗 QuickBooks Online
**Fonctionnalités:**
- Statut de connexion (Connecté/En attente)
- Bouton "Connecter QBO" (redirection OAuth)
- Affichage du Realm ID si connecté

**Expérience utilisateur:**
1. Cliquer sur "Connecter QBO"
2. Redirection vers Intuit OAuth Sandbox
3. Autoriser l'application
4. Retour automatique avec connexion confirmée

---

#### 2. 📈 Projections Financières
**Fonctionnalités:**
- Statut: "Données disponibles" ou "Non générées"
- **3 boutons:**
  - 🚀 **Simuler Projections** → Ouvre le simulateur interactif
  - 📊 **Voir Vue AIA** → Affiche la vue financière agrégée avec graphiques
  - 📋 **Voir Vue QBO** → Affiche les données QBO brutes et anomalies

**Expérience utilisateur:**
- Les données AIA sont chargées automatiquement au démarrage
- Le bouton "Simuler Projections" est activé si les données sont disponibles

---

#### 3. 📊 Visualisations
**Fonctionnalité:** (À venir)
- Graphiques de revenus, dépenses et profits projetés

---

#### 4. 💾 Export Google Sheets
**Fonctionnalité:**
- Export automatique des projections vers Google Sheets

---

#### 5. ⚙️ Configuration
**Fonctionnalité:**
- Gestion des paramètres et hypothèses de croissance

---

#### 6. 📝 Documentation API
**Fonctionnalité:**
- Lien vers la documentation Swagger de l'API

---

## 📊 Vue AIA - Modal avec Graphiques

### Ouvrir la vue
Cliquer sur **"📊 Voir Vue AIA"** dans la carte "Projections Financières"

### Contenu affiché

#### 1. Informations de période
- Date de début et fin de la période analysée

#### 2. Réconciliation financière
- **Total QBO**: Somme brute des données QuickBooks
- **Total AIA**: Somme après regroupement par catégories
- **Delta**: Différence (devrait être ≈ 0)
- **Statut**: ✅ Réconcilié ou ⚠️ Écart

#### 3. Graphique d'évolution mensuelle
- **Type**: Graphique en lignes (LineChart)
- **Données**: Évolution par mois pour chaque catégorie
- **Interactivité**: 
  - Tooltip au survol montrant les montants
  - Légende cliquable pour afficher/masquer des catégories
  - Zoom possible

#### 4. Graphique par catégorie
- **Type**: Graphique en barres (BarChart)
- **Données**: Totaux par catégorie AIA
- **Affichage**: Top 10 catégories par montant

#### 5. Tableau détaillé
- Colonnes: Catégorie | Total | Confiance | Nb Comptes
- **Badges de confiance**:
  - 🟢 Vert (>70%): Haute confiance
  - 🟠 Orange (50-70%): Confiance moyenne
  - 🔴 Rouge (<50%): Faible confiance
- Tri par montant (décroissant)

---

## 🚀 Simulateur de Projections - Modal interactif

### Ouvrir le simulateur
Cliquer sur **"🚀 Simuler Projections"** dans la carte "Projections Financières"

### Contrôles du simulateur

#### Paramètres ajustables:
1. **Croissance des revenus** (%/an)
   - Slider/Input numérique
   - Valeur par défaut: 10%
   - Plage: 0-100%

2. **Croissance des dépenses** (%/an)
   - Slider/Input numérique
   - Valeur par défaut: 5%
   - Plage: 0-100%

3. **Période de projection** (mois)
   - Options: 12, 24, 36 mois
   - Valeur par défaut: 36 mois

### Visualisations affichées

#### 1. Graphique des projections
- **Type**: Graphique en lignes multi-séries
- **Séries**:
  - 💚 Revenus (ligne verte)
  - ❤️ Dépenses (ligne rouge)
  - 💙 Profit (ligne bleue)
- **Axe X**: Mois de projection (1-36)
- **Axe Y**: Montants ($)
- **Interactivité**: Tooltip au survol

#### 2. Graphique profit cumulatif
- **Type**: Graphique en barres
- **Données**: Profit cumulé mois par mois
- **Couleur**: Bleu (#2196f3)
- Visualise la croissance du profit total dans le temps

#### 3. Tableau des projections
- Colonnes: Période | Revenus | Dépenses | Profit | Profit Cumulatif
- Affiche les 12 premiers mois
- **Codes couleur**:
  - Vert pour les montants positifs
  - Rouge pour les montants négatifs

#### 4. Résumé des projections
**4 cartes de résumé:**
- Revenus Total (période)
- Dépenses Total (période)
- Profit Total
- Profit Final (dernier mois)

### Expérience utilisateur
1. **Modifier les paramètres** → Les graphiques se mettent à jour en temps réel
2. **Visualiser les tendances** → Voir l'impact des hypothèses de croissance
3. **Comparer les scénarios** → Changer les paramètres et observer les différences

---

## 📋 Vue QBO - Modal avec Analyse d'Anomalies

### Ouvrir la vue
Cliquer sur **"📋 Voir Vue QBO"** dans la carte "Projections Financières"

### Contenu affiché

#### 1. Statistiques globales
**4 cartes:**
- Total comptes (actifs/inactifs)
- Total transactions
- Total snapshots
- Montant total

#### 2. Analyse d'anomalies
**3 niveaux de sévérité:**
- 🔴 **Critiques**: Problèmes majeurs à corriger immédiatement
- 🟡 **Avertissements**: Problèmes à surveiller
- ℹ️ **Informations**: Points d'attention

**Types d'anomalies détectées:**
- Transactions avec dates futures
- Comptes sans type défini
- Transactions sur comptes inactifs
- Montants anormalement élevés (outliers)
- Transactions sans compte associé
- Comptes référencés mais absents
- Transactions en double
- Transactions avec montant zéro
- Snapshots manquants

**Détails expandables** pour chaque anomalie

#### 3. Tableau des comptes
- Colonnes: Nom | Type | Sous-type | Classification | Statut
- Limité à 20 premiers (avec indication du total)
- Badges de statut (Actif/Inactif)

#### 4. Tableau des transactions
- Colonnes: Date | Type | Montant | Contrepartie | Mémo
- Limité à 20 premières
- Codes couleur pour montants positifs/négatifs

#### 5. Snapshots disponibles
- Type de rapport (P&L, Balance Sheet)
- Période couverte
- Date de création
- Indicateur de présence de données

---

## 🎨 Design et UX

### Style visuel
- **Couleurs principales**: 
  - Violet/bleu (#667eea) pour les éléments principaux
  - Dégradés modernes pour les cartes
- **Responsive**: S'adapte à toutes les tailles d'écran
- **Animations**: Transitions douces au survol
- **Modales**: Overlay avec fermeture par clic extérieur

### Accessibilité
- Boutons avec états visuels (hover, disabled)
- Contrastes de couleurs suffisants
- Textes lisibles et hiérarchie claire
- Messages d'erreur explicites

---

## 🔄 Flux utilisateur typique

### Scénario 1: Nouvel utilisateur
1. Ouvrir http://localhost:3000
2. Vérifier la connexion backend (✅)
3. Cliquer "Connecter QBO" → Autoriser dans Intuit
4. Retour automatique avec connexion confirmée
5. Cliquer "Voir Vue AIA" → Visualiser les données agrégées
6. Cliquer "Simuler Projections" → Ajuster les paramètres et voir les projections

### Scénario 2: Utilisateur existant
1. Ouvrir http://localhost:3000
2. Les données AIA sont chargées automatiquement
3. Cliquer "Voir Vue QBO" → Vérifier les anomalies
4. Cliquer "Simuler Projections" → Tester différents scénarios
5. Exporter les données si nécessaire

---

## 📊 Exemples de visualisations

### Graphique d'évolution mensuelle (Vue AIA)
```
Évolution par catégorie sur 12 mois
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  $50k │                    ╱╲
       │                  ╱  ╲
  $40k │                ╱    ╲    ╱╲
       │              ╱      ╲  ╱  ╲
  $30k │            ╱        ╲╱    ╲
       │          ╱              ╱╲
  $20k │        ╱              ╱  ╲
       │      ╱              ╱    ╲
  $10k │    ╱              ╱      ╲
       │  ╱              ╱        ╲
   $0k └──────────────────────────────
       Jan  Feb  Mar  Apr  May  Jun ...
       
   Légende: Revenus | Dépenses | Profit
```

### Simulateur de projections
```
Projections 3 ans avec croissance 10% revenus / 5% dépenses
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  $200k │                                    ╱╲ Revenus
        │                                  ╱  ╲
  $150k │                                ╱    ╲
        │                              ╱      ╲
  $100k │                            ╱        ╲
        │                          ╱          ╲
   $50k │                        ╱            ╲
        │                      ╱              ╲
    $0k │                    ╱                ╲
        │                  ╱  Dépenses         ╲
  -$50k └──────────────────────────────────────────────
        0   6   12  18  24  30  36 Mois
```

---

## ✅ Points forts de l'interface

1. **Visualisation claire**: Graphiques interactifs pour comprendre rapidement les données
2. **Simulation interactive**: Ajustement en temps réel des paramètres de projection
3. **Détection d'anomalies**: Identification automatique des problèmes dans les données
4. **Réconciliation transparente**: Vérification que total QBO = total AIA
5. **Export facilité**: Données prêtes pour Google Sheets
6. **Responsive**: Fonctionne sur desktop, tablette et mobile

---

## 🚀 Pour tester

1. Ouvrir: http://localhost:3000
2. Explorer les différents boutons et modales
3. Tester le simulateur avec différents paramètres
4. Vérifier les graphiques interactifs (tooltips, légendes)
5. Consulter l'analyse d'anomalies dans la Vue QBO

---

**Interface prête pour les utilisateurs finaux!** 🎉
