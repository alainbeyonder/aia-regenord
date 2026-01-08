import React, { useState, useEffect } from 'react';
import './App.css';

/**
 * Composant Questionnaire d'Hypothèses de Projection
 * Version améliorée avec wizard, valeurs par défaut intelligentes, et validation
 */
const QuestionnaireHypotheses = ({ aiaData, onAssumptionsComplete, onClose }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [assumptions, setAssumptions] = useState({
    // Step 0: Contexte
    context: '',
    contextOther: '',
    
    // Step 1: Revenus (par catégorie)
    revenueCategories: {},
    
    // Step 2: Coûts
    expenses: {
      evolution: 'stable',
      inflationRate: 2,
      optimizationRate: 0,
      fixedVsVariable: 'mixed',
      triggers: []
    },
    
    // Step 3: R&D
    rd: {
      hasRD: false, // Question initiale : faites-vous de la R&D/RS&DE ?
      allocationMethod: 'total-percentage',
      allocationValue: 0,
      creditInclude: true,
      creditCaution: false,
      creditCautionPercentage: 80,
      reimbursementDelay: 12
    },
    
    // Step 4: Dette
    debt: {
      currentProjection: 'normal',
      interestOnlyMonths: null,
      newDebts: []
    },
    
    // Step 5: Équité
    equity: {
      possible: false,
      maxAmount: 0,
      certainty: 'conditional'
    },
    
    // Step 6: Trésorerie
    cash: {
      minThreshold: 0,
      deficitTolerance: {
        acceptable: false,
        maxMonths: 0,
        ifPlanClear: false
      },
      priorityIfTight: 'reduce-costs'
    },
    
    // Step 7: Actifs incorporels & Amortissement (IAS 38)
    intangibles: {
      hasDevelopmentProjects: false,
      projects: [],
      globalSettings: {
        defaultSalaryCapitalizationShare: 80, // %
        applySalaryShareToOverheads: true,
        overheadAllocationShare: 80, // %
        capitalizeInterestWhenDirectlyAttributable: true,
        impairmentReviewFrequency: 'annual'
      },
      financialPresentation: 'both' // 'management' | 'fiscal' | 'both'
    },
    
    // Step 8: Scénarios
    scenarios: {
      default: 'realistic',
      compare: false,
      comparedScenarios: []
    }
  });

  // Calculer les valeurs par défaut basées sur les données historiques
  useEffect(() => {
    console.log('🔵 QuestionnaireHypotheses - aiaData reçu:', aiaData ? 'OUI' : 'NON');
    if (aiaData) {
      console.log('🔵 Catégories disponibles:', Object.keys(aiaData.totals_by_category || {}));
    }
    if (aiaData && Object.keys(assumptions.revenueCategories).length === 0) {
      initializeDefaults();
    }
  }, [aiaData]);

  const initializeDefaults = () => {
    if (!aiaData || !aiaData.totals_by_category) return;

    const revenueCategories = {};
    let totalRevenue = 0;
    let totalExpenses = 0;

    // Calculer la croissance historique pour chaque catégorie de revenus
    // Détecter le type depuis la clé (revenue_* ou expense_*)
    Object.keys(aiaData.totals_by_category).forEach(catKey => {
      const category = aiaData.totals_by_category[catKey];
      const isRevenue = catKey.startsWith('revenue_');
      const isExpense = catKey.startsWith('expense_');
      
      if (isRevenue) {
        totalRevenue += Math.abs(category.total);
        
        const monthlyTotals = category.monthly_totals || {};
        const months = Object.keys(monthlyTotals).sort();
        let historicalGrowth = 0;
        
        if (months.length >= 2) {
          const firstHalf = months.slice(0, Math.floor(months.length / 2));
          const secondHalf = months.slice(Math.floor(months.length / 2));
          const avgFirst = firstHalf.reduce((sum, m) => sum + Math.abs(monthlyTotals[m] || 0), 0) / firstHalf.length;
          const avgSecond = secondHalf.reduce((sum, m) => sum + Math.abs(monthlyTotals[m] || 0), 0) / secondHalf.length;
          if (avgFirst > 0) {
            historicalGrowth = ((avgSecond - avgFirst) / avgFirst) * 100;
          }
        }

        revenueCategories[catKey] = {
          type: 'recurrent',
          growth: {
            conservative: Math.max(0, historicalGrowth * 0.5),
            realistic: Math.max(0, historicalGrowth),
            optimistic: Math.max(0, historicalGrowth * 1.5)
          },
          triggers: [],
          riskConcentration: 'diversified'
        };
      } else if (isExpense) {
        totalExpenses += Math.abs(category.total);
      }
    });

    // Estimer le crédit RS&DE (généralement 35-41% des dépenses R&D éligibles)
    const rdExpense = aiaData.totals_by_category.expense_rd?.total || 0;
    const estimatedRDCredit = Math.abs(rdExpense) * 0.38; // 38% en moyenne

    // Calculer le seuil de trésorerie recommandé (2-3 mois de coûts)
    const monthlyAvgExpenses = Math.abs(totalExpenses) / 12;
    const recommendedCashThreshold = monthlyAvgExpenses * 2.5;

    setAssumptions(prev => ({
      ...prev,
      revenueCategories,
      rd: {
        ...prev.rd,
        hasRD: rdExpense > 0, // Définir hasRD = true si des dépenses R&D sont détectées
        allocationValue: rdExpense > 0 ? 15 : 0, // % des dépenses totales
        creditInclude: true,
        creditEstimated: estimatedRDCredit
      },
      cash: {
        ...prev.cash,
        minThreshold: recommendedCashThreshold
      }
    }));
  };

  const updateAssumption = (path, value) => {
    setAssumptions(prev => {
      const keys = path.split('.');
      const updated = { ...prev };
      let current = updated;
      
      for (let i = 0; i < keys.length - 1; i++) {
        if (!current[keys[i]]) current[keys[i]] = {};
        current[keys[i]] = { ...current[keys[i]] };
        current = current[keys[i]];
      }
      
      current[keys[keys.length - 1]] = value;
      return updated;
    });
  };

  const addRevenueTrigger = (catKey) => {
    const triggers = assumptions.revenueCategories[catKey]?.triggers || [];
    updateAssumption(`revenueCategories.${catKey}.triggers`, [
      ...triggers,
      { month: 6, amount: 0, description: '' }
    ]);
  };

  const addExpenseTrigger = () => {
    updateAssumption('expenses.triggers', [
      ...assumptions.expenses.triggers,
      { month: 6, amount: 0, description: '', type: 'other' }
    ]);
  };

  const addDebt = () => {
    updateAssumption('debt.newDebts', [
      ...assumptions.debt.newDebts,
      { amount: 0, month: 6, rate: 5, description: '' }
    ]);
  };

  const validateStep = (step) => {
    switch (step) {
      case 0:
        return assumptions.context !== '';
      case 1:
        return Object.keys(assumptions.revenueCategories).length > 0;
      case 7:
        // Actifs incorporels: optionnel, mais si hasDevelopmentProjects = true, doit avoir au moins un projet
        if (assumptions.intangibles.hasDevelopmentProjects) {
          return assumptions.intangibles.projects.length > 0;
        }
        return true;
      case 8:
        return assumptions.scenarios.default !== '';
      default:
        return true;
    }
  };

  const getStepTitle = (step) => {
    const titles = [
      'Contexte Général',
      'Hypothèses de Revenus',
      'Hypothèses de Coûts',
      'Hypothèses R&D / RS&DE',
      'Hypothèses de Dette & Financement',
      'Hypothèses de Trésorerie',
      'Actifs Incorporels & Amortissement (IAS 38)',
      'Scénarios Stratégiques',
      'Validation Finale'
    ];
    return titles[step] || 'Étape';
  };

  const renderStep0 = () => (
    <div className="questionnaire-step">
      <h3>🎯 Quelle est la finalité de ces projections ?</h3>
      <p className="step-description">L'AIA ajustera le niveau de prudence selon votre réponse.</p>
      <div className="radio-group">
        {['banking', 'strategic', 'investor', 'operational', 'other'].map(option => (
          <label key={option} className="radio-label">
            <input
              type="radio"
              name="context"
              value={option}
              checked={assumptions.context === option}
              onChange={(e) => updateAssumption('context', e.target.value)}
            />
            <span>
              {option === 'banking' && '💼 Discussion bancaire'}
              {option === 'strategic' && '🎯 Décision stratégique interne'}
              {option === 'investor' && '💰 Investisseurs / financement'}
              {option === 'operational' && '📊 Pilotage opérationnel'}
              {option === 'other' && '🔷 Autre'}
            </span>
          </label>
        ))}
      </div>
      {assumptions.context === 'other' && (
        <input
          type="text"
          placeholder="Précisez..."
          value={assumptions.contextOther}
          onChange={(e) => updateAssumption('contextOther', e.target.value)}
          className="text-input"
        />
      )}
    </div>
  );

  const renderStep1 = () => {
    // Détecter les catégories de revenus depuis la clé (revenue_*)
    // car le backend ne retourne pas le champ 'type' dans la structure
    const revenueKeys = Object.keys(aiaData?.totals_by_category || {}).filter(
      key => key.startsWith('revenue_')
    );

    console.log('🔵 renderStep1 - aiaData:', aiaData ? 'présent' : 'absent');
    console.log('🔵 renderStep1 - totals_by_category:', aiaData?.totals_by_category ? Object.keys(aiaData.totals_by_category) : 'absent');
    console.log('🔵 renderStep1 - revenueKeys trouvées:', revenueKeys);

    if (revenueKeys.length === 0) {
      return (
        <div className="questionnaire-step">
          <h3>💰 Hypothèses de Revenus</h3>
          <div className="error-box">
            ⚠️ Aucune catégorie de revenus détectée dans les données QBO.
          </div>
          <div className="info-box">
            <p><strong>Raisons possibles:</strong></p>
            <ul style={{ marginLeft: '20px', marginTop: '10px' }}>
              <li>QuickBooks n'est pas encore connecté ou le token a expiré</li>
              <li>Aucune donnée financière synchronisée</li>
              <li>Aucun compte de revenus dans QuickBooks</li>
            </ul>
            <p style={{ marginTop: '15px' }}><strong>Solutions:</strong></p>
            <ol style={{ marginLeft: '20px', marginTop: '10px' }}>
              <li>Retournez au tableau de bord et cliquez sur "Connecter QBO"</li>
              <li>Autorisez l'accès à vos données QuickBooks</li>
              <li>Attendez la synchronisation des données</li>
              <li>Relancez le questionnaire</li>
            </ol>
          </div>
          <div style={{ marginTop: '20px', textAlign: 'center' }}>
            <button className="btn-secondary" onClick={onClose}>
              ← Retour au tableau de bord
            </button>
          </div>
        </div>
      );
    }

    return (
      <div className="questionnaire-step">
        <h3>💰 Hypothèses de Revenus (par catégorie)</h3>
        {revenueKeys.map(catKey => {
          const category = aiaData.totals_by_category[catKey];
          const catAssumptions = assumptions.revenueCategories[catKey] || {
            type: 'recurrent',
            growth: { conservative: 0, realistic: 0, optimistic: 0 },
            triggers: [],
            riskConcentration: 'diversified'
          };

          const historicalTotal = Math.abs(category.total || 0);
          const monthlyTotals = category.monthly_totals || {};
          const hasData = Object.values(monthlyTotals).some(v => Math.abs(v || 0) > 0);
          const accountsCount = category.accounts_count || 0;
          const confidenceScore = (category.confidence_score || 0) * 100;

          return (
            <div key={catKey} className="revenue-category-card">
              <h4>{category.name}</h4>
              <div className="category-info">
                {historicalTotal > 0 ? (
                  <>
                    <p>
                      Historique: <strong>${historicalTotal.toLocaleString('fr-CA', { minimumFractionDigits: 2 })}</strong>
                      {' | '}
                      {accountsCount} compte{accountsCount !== 1 ? 's' : ''} mappé{accountsCount !== 1 ? 's' : ''}
                      {' | '}
                      Confiance: {confidenceScore.toFixed(0)}%
                    </p>
                  </>
                ) : (
                  <>
                    <p>
                      Historique: <span style={{ color: '#f44336', fontStyle: 'italic' }}>Aucune donnée disponible ($0.00)</span>
                    </p>
                    <p style={{ fontSize: '0.9em', color: '#666', marginTop: '8px' }}>
                      {accountsCount > 0 ? (
                        <>
                          ✅ {accountsCount} compte{accountsCount !== 1 ? 's' : ''} {accountsCount > 1 ? 'sont mappés' : 'est mappé'} vers cette catégorie
                          {' | '}
                          Confiance: {confidenceScore.toFixed(0)}%
                          <br />
                          <span style={{ fontStyle: 'italic' }}>
                            💡 Ces comptes n'ont pas de transactions avec montants dans la période analysée.
                            Vous pouvez saisir manuellement les valeurs de projection ci-dessous.
                          </span>
                        </>
                      ) : (
                        <>
                          ⚠️ Aucun compte n'est mappé vers cette catégorie.
                          <br />
                          <span style={{ fontStyle: 'italic' }}>
                            💡 Vérifiez le mapping des comptes ou ajoutez des transactions dans QuickBooks.
                            Vous pouvez saisir manuellement les valeurs de projection ci-dessous.
                          </span>
                        </>
                      )}
                    </p>
                  </>
                )}
              </div>

              {/* Type de revenus */}
              <div className="form-group">
                <label>Type de revenus pour cette catégorie</label>
                <div className="radio-group">
                  {['recurrent', 'one-time', 'hybrid'].map(type => (
                    <label key={type} className="radio-label">
                      <input
                        type="radio"
                        checked={catAssumptions.type === type}
                        onChange={() => {
                          const updated = { ...catAssumptions, type };
                          updateAssumption(`revenueCategories.${catKey}`, updated);
                        }}
                      />
                      <span>
                        {type === 'recurrent' && '🔄 Récurrent'}
                        {type === 'one-time' && '⚡ Ponctuel'}
                        {type === 'hybrid' && '🔀 Hybride'}
                      </span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Croissance */}
              <div className="form-group">
                <label>Croissance attendue (%)</label>
                <div className="growth-inputs">
                  {['conservative', 'realistic', 'optimistic'].map(level => (
                    <div key={level} className="growth-input">
                      <label className="growth-label">
                        {level === 'conservative' && '⚠️ Conservateur'}
                        {level === 'realistic' && '✅ Réaliste'}
                        {level === 'optimistic' && '🚀 Ambitieux'}
                      </label>
                      <input
                        type="number"
                        value={catAssumptions.growth[level] || ''}
                        onChange={(e) => {
                          const val = e.target.value;
                          const updated = {
                            ...catAssumptions,
                            growth: {
                              ...catAssumptions.growth,
                              [level]: val === '' ? null : parseFloat(val) || null
                            }
                          };
                          updateAssumption(`revenueCategories.${catKey}`, updated);
                        }}
                        step="0.1"
                        min="0"
                        max="1000"
                        className="number-input"
                      />
                      <span>%</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Déclencheurs */}
              <div className="form-group">
                <label>Déclencheurs futurs de revenus</label>
                <div className="info-box" style={{ marginTop: '10px', marginBottom: '15px' }}>
                  <p><strong>💡 Qu'est-ce qu'un déclencheur de revenu ?</strong></p>
                  <p style={{ marginTop: '8px' }}>
                    Les déclencheurs sont des événements futurs qui généreront des revenus supplémentaires 
                    à une date précise. Ils permettent de modéliser des revenus ponctuels ou des augmentations 
                    de revenus récurrents à partir d'un moment donné.
                  </p>
                  <p style={{ marginTop: '8px', fontWeight: 'bold' }}>Exemples concrets :</p>
                  <ul style={{ marginLeft: '20px', marginTop: '5px' }}>
                    <li><strong>Mois 6, 25 000$</strong> - "Nouveau contrat client ABC"</li>
                    <li><strong>Mois 12, 50 000$</strong> - "Lancement produit X"</li>
                    <li><strong>Mois 3, 15 000$</strong> - "Renouvellement licence annuelle"</li>
                    <li><strong>Mois 18, 100 000$</strong> - "Projet gouvernemental phase 2"</li>
                  </ul>
                  <p style={{ marginTop: '8px', fontSize: '0.9em', color: '#666' }}>
                    💡 <strong>Le mois</strong> correspond au nombre de mois à partir d'aujourd'hui (1 = le mois prochain).
                    <br />
                    💡 <strong>Le montant</strong> est le revenu supplémentaire attendu dans ce mois-là.
                    <br />
                    💡 <strong>La description</strong> vous aide à vous rappeler la source de ce revenu.
                  </p>
                </div>
                {catAssumptions.triggers.map((trigger, idx) => (
                  <div key={idx} className="trigger-row">
                    <div className="trigger-field">
                      <label className="trigger-label">Mois</label>
                      <input
                        type="number"
                        placeholder="Ex: 6"
                        value={trigger.month || ''}
                        onChange={(e) => {
                          const updated = [...catAssumptions.triggers];
                          const val = e.target.value;
                          updated[idx].month = val === '' ? null : parseInt(val) || null;
                          updateAssumption(`revenueCategories.${catKey}.triggers`, updated);
                        }}
                        className="number-input small"
                        min="1"
                        max="36"
                      />
                      <span className="trigger-hint" style={{ fontSize: '0.75em', color: '#999', marginTop: '2px' }}>
                        mois à partir d'aujourd'hui
                      </span>
                    </div>
                    <div className="trigger-field">
                      <label className="trigger-label">Montant ($)</label>
                      <input
                        type="number"
                        placeholder="Ex: 25000"
                        value={trigger.amount || ''}
                        onChange={(e) => {
                          const updated = [...catAssumptions.triggers];
                          const val = e.target.value;
                          updated[idx].amount = val === '' ? null : parseFloat(val) || null;
                          updateAssumption(`revenueCategories.${catKey}.triggers`, updated);
                        }}
                        className="number-input"
                        min="0"
                        step="0.01"
                      />
                      <span className="trigger-hint" style={{ fontSize: '0.75em', color: '#999', marginTop: '2px' }}>
                        revenu supplémentaire
                      </span>
                    </div>
                    <div className="trigger-field trigger-field-wide">
                      <label className="trigger-label">Description</label>
                      <input
                        type="text"
                        placeholder="Ex: Nouveau contrat client ABC"
                        value={trigger.description || ''}
                        onChange={(e) => {
                          const updated = [...catAssumptions.triggers];
                          updated[idx].description = e.target.value;
                          updateAssumption(`revenueCategories.${catKey}.triggers`, updated);
                        }}
                        className="text-input"
                      />
                      <span className="trigger-hint" style={{ fontSize: '0.75em', color: '#999', marginTop: '2px', visibility: 'hidden' }}>
                        {/* Hint invisible pour maintenir l'alignement */}
                      </span>
                    </div>
                    <button
                      className="btn-small"
                      onClick={() => {
                        const updated = catAssumptions.triggers.filter((_, i) => i !== idx);
                        updateAssumption(`revenueCategories.${catKey}.triggers`, updated);
                      }}
                      title="Supprimer ce déclencheur"
                      style={{ alignSelf: 'flex-start', marginTop: '28px' }}
                    >
                      ✕
                    </button>
                  </div>
                ))}
                <button className="btn-secondary" onClick={() => addRevenueTrigger(catKey)}>
                  + Ajouter un déclencheur de revenu
                </button>
                {catAssumptions.triggers.length === 0 && (
                  <p className="hint" style={{ marginTop: '10px', fontStyle: 'italic', color: '#666' }}>
                    💡 Si vous n'avez pas de revenus ponctuels prévus, vous pouvez laisser cette section vide 
                    et utiliser uniquement la croissance en pourcentage ci-dessus.
                  </p>
                )}
              </div>

              {/* Concentration du risque */}
              <div className="form-group">
                <label>Concentration du risque</label>
                <div className="radio-group">
                  {['diversified', 'major-clients', 'transition'].map(risk => (
                    <label key={risk} className="radio-label">
                      <input
                        type="radio"
                        checked={catAssumptions.riskConcentration === risk}
                        onChange={() => {
                          const updated = { ...catAssumptions, riskConcentration: risk };
                          updateAssumption(`revenueCategories.${catKey}`, updated);
                        }}
                      />
                      <span>
                        {risk === 'diversified' && '✅ Revenus diversifiés'}
                        {risk === 'major-clients' && '⚠️ Dépendance à 1–2 clients majeurs'}
                        {risk === 'transition' && '🔄 Transition en cours'}
                      </span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  const renderStep2 = () => (
    <div className="questionnaire-step">
      <h3>💸 Hypothèses de Coûts d'Exploitation (OPEX)</h3>
      
      <div className="form-group">
        <label>Évolution globale des coûts</label>
        <div className="radio-group">
          {['stable', 'inflation', 'optimization', 'growth-linked'].map(evo => (
            <label key={evo} className="radio-label">
              <input
                type="radio"
                checked={assumptions.expenses.evolution === evo}
                onChange={() => updateAssumption('expenses.evolution', evo)}
              />
              <span>
                {evo === 'stable' && '➡️ Stable'}
                {evo === 'inflation' && '📈 Inflation prévue'}
                {evo === 'optimization' && '📉 Optimisation prévue'}
                {evo === 'growth-linked' && '🔗 Hausse liée à la croissance'}
              </span>
            </label>
          ))}
        </div>
        {assumptions.expenses.evolution === 'inflation' && (
          <div className="form-group">
            <label>Taux d'inflation (%)</label>
            <input
              type="number"
              value={assumptions.expenses.inflationRate || ''}
              onChange={(e) => {
                const val = e.target.value;
                updateAssumption('expenses.inflationRate', val === '' ? null : parseFloat(val) || null);
              }}
              placeholder="Ex: 2.5"
              className="number-input"
              min="0"
              max="50"
              step="0.1"
            />
          </div>
        )}
        {assumptions.expenses.evolution === 'optimization' && (
          <div className="form-group">
            <label>Taux d'optimisation (%)</label>
            <input
              type="number"
              value={assumptions.expenses.optimizationRate || ''}
              onChange={(e) => {
                const val = e.target.value;
                updateAssumption('expenses.optimizationRate', val === '' ? null : parseFloat(val) || null);
              }}
              placeholder="Ex: 10"
              className="number-input"
              min="0"
              max="100"
              step="0.1"
            />
          </div>
        )}
      </div>

      <div className="form-group">
        <label>Coûts fixes vs variables</label>
        <div className="radio-group">
          {['mostly-fixed', 'mostly-variable', 'mixed'].map(type => (
            <label key={type} className="radio-label">
              <input
                type="radio"
                checked={assumptions.expenses.fixedVsVariable === type}
                onChange={() => updateAssumption('expenses.fixedVsVariable', type)}
              />
              <span>
                {type === 'mostly-fixed' && '🔒 Majoritairement fixes'}
                {type === 'mostly-variable' && '📊 Majoritairement variables'}
                {type === 'mixed' && '🔀 Mixte'}
              </span>
            </label>
          ))}
        </div>
      </div>

      <div className="form-group">
        <label>Déclencheurs de coûts futurs</label>
        {assumptions.expenses.triggers.map((trigger, idx) => (
          <div key={idx} className="trigger-row">
            <div className="trigger-field">
              <label className="trigger-label">Mois</label>
              <input
                type="number"
                placeholder="Ex: 6"
                value={trigger.month || ''}
                onChange={(e) => {
                  const val = e.target.value;
                  const updated = [...assumptions.expenses.triggers];
                  updated[idx].month = val === '' ? null : parseInt(val) || null;
                  updateAssumption('expenses.triggers', updated);
                }}
                className="number-input small"
                min="1"
                max="36"
              />
            </div>
            <div className="trigger-field">
              <label className="trigger-label">Montant ($)</label>
              <input
                type="number"
                placeholder="Ex: 5000"
                value={trigger.amount || ''}
                onChange={(e) => {
                  const val = e.target.value;
                  const updated = [...assumptions.expenses.triggers];
                  updated[idx].amount = val === '' ? null : parseFloat(val) || null;
                  updateAssumption('expenses.triggers', updated);
                }}
                className="number-input"
                min="0"
                step="0.01"
              />
            </div>
            <div className="trigger-field trigger-field-wide">
              <label className="trigger-label">Description</label>
              <input
                type="text"
                placeholder="Ex: Embauche, Nouveau local"
                value={trigger.description || ''}
                onChange={(e) => {
                  const updated = [...assumptions.expenses.triggers];
                  updated[idx].description = e.target.value;
                  updateAssumption('expenses.triggers', updated);
                }}
                className="text-input"
              />
              <span className="trigger-hint" style={{ fontSize: '0.75em', color: '#999', marginTop: '2px', visibility: 'hidden' }}>
                {/* Hint invisible pour maintenir l'alignement */}
              </span>
            </div>
            <button
              className="btn-small"
              onClick={() => {
                const updated = assumptions.expenses.triggers.filter((_, i) => i !== idx);
                updateAssumption('expenses.triggers', updated);
              }}
              title="Supprimer ce déclencheur"
              style={{ alignSelf: 'flex-start', marginTop: '28px' }}
            >
              ✕
            </button>
          </div>
        ))}
        <button className="btn-secondary" onClick={addExpenseTrigger}>
          + Ajouter un déclencheur de coût
        </button>
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div className="questionnaire-step">
      <h3>🔬 Hypothèses R&D / RS&DE</h3>
      
      {/* Question initiale */}
      <div className="form-group">
        <label>Faites-vous de la R&D/RS&DE (Recherche et développement / Recherche scientifique et développement expérimental) ?</label>
        <div className="radio-group">
          <label className="radio-label">
            <input
              type="radio"
              checked={!assumptions.rd.hasRD}
              onChange={() => {
                updateAssumption('rd.hasRD', false);
                // Réinitialiser les valeurs si "Non"
                updateAssumption('rd.allocationMethod', 'total-percentage');
                updateAssumption('rd.allocationValue', 0);
                updateAssumption('rd.creditInclude', false);
              }}
            />
            <span>❌ Non → passer à la section suivante</span>
          </label>
          <label className="radio-label">
            <input
              type="radio"
              checked={assumptions.rd.hasRD}
              onChange={() => updateAssumption('rd.hasRD', true)}
            />
            <span>✅ Oui → continuer</span>
          </label>
        </div>
        {assumptions.rd.hasRD && (
          <div className="info-box" style={{ marginTop: '15px' }}>
            <p><strong>💡 Explication AIA :</strong></p>
            <p>
              La R&D/RS&DE peut être éligible à des crédits d'impôt importants au Canada. 
              Cette section vous permet de configurer les hypothèses de projection pour vos activités de recherche et développement.
            </p>
          </div>
        )}
      </div>

      {assumptions.rd.hasRD && (
        <>
          <div className="form-group">
            <label>Part des ressources consacrées à la R&D</label>
        <div className="radio-group">
          {['salary-percentage', 'total-percentage', 'project', 'continuous'].map(method => (
            <label key={method} className="radio-label">
              <input
                type="radio"
                checked={assumptions.rd.allocationMethod === method}
                onChange={() => updateAssumption('rd.allocationMethod', method)}
              />
              <span>
                {method === 'salary-percentage' && '👥 % des salaires'}
                {method === 'total-percentage' && '💰 % des dépenses totales'}
                {method === 'project' && '📋 Projet ponctuel'}
                {method === 'continuous' && '🔄 R&D continue'}
              </span>
            </label>
          ))}
        </div>
        {(assumptions.rd.allocationMethod === 'salary-percentage' || assumptions.rd.allocationMethod === 'total-percentage') && (
          <div className="form-group">
            <label>Pourcentage</label>
            <input
              type="number"
              value={assumptions.rd.allocationValue || ''}
              onChange={(e) => {
                const val = e.target.value;
                updateAssumption('rd.allocationValue', val === '' ? null : parseFloat(val) || null);
              }}
              placeholder="Ex: 15"
              className="number-input"
              min="0"
              max="100"
              step="0.1"
            />
          </div>
        )}
          </div>

          <div className="form-group">
            <label>Crédit RS&DE attendu</label>
        {assumptions.rd.creditEstimated && (
          <p className="info-box">
            💡 L'AIA estime un crédit RS&DE de ${assumptions.rd.creditEstimated.toLocaleString('fr-CA', { minimumFractionDigits: 2 })}.
          </p>
        )}
        <div className="radio-group">
          <label className="radio-label">
            <input
              type="radio"
              checked={assumptions.rd.creditInclude && !assumptions.rd.creditCaution}
              onChange={() => {
                updateAssumption('rd.creditInclude', true);
                updateAssumption('rd.creditCaution', false);
              }}
            />
            <span>✅ L'inclure dans la trésorerie</span>
          </label>
          <label className="radio-label">
            <input
              type="radio"
              checked={assumptions.rd.creditInclude && assumptions.rd.creditCaution}
              onChange={() => {
                updateAssumption('rd.creditInclude', true);
                updateAssumption('rd.creditCaution', true);
              }}
            />
            <span>⚠️ L'inclure avec prudence</span>
          </label>
          <label className="radio-label">
            <input
              type="radio"
              checked={!assumptions.rd.creditInclude}
              onChange={() => updateAssumption('rd.creditInclude', false)}
            />
            <span>❌ L'exclure des projections</span>
          </label>
        </div>
        {assumptions.rd.creditCaution && (
          <div className="form-group">
            <label>% à inclure</label>
            <input
              type="number"
              value={assumptions.rd.creditCautionPercentage || ''}
              onChange={(e) => {
                const val = e.target.value;
                updateAssumption('rd.creditCautionPercentage', val === '' ? null : parseFloat(val) || null);
              }}
              placeholder="Ex: 80"
              className="number-input"
              min="0"
              max="100"
              step="0.1"
            />
          </div>
        )}
      </div>

          <div className="form-group">
            <label>Délai de remboursement estimé (mois)</label>
            <div className="radio-group">
              {[6, 9, 12, 18].map(delay => (
                <label key={delay} className="radio-label">
                  <input
                    type="radio"
                    checked={assumptions.rd.reimbursementDelay === delay}
                    onChange={() => updateAssumption('rd.reimbursementDelay', delay)}
                  />
                  <span>{delay} mois</span>
                </label>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );

  const renderStep4 = () => (
    <div className="questionnaire-step">
      <h3>🏦 Hypothèses de Dette & Financement</h3>
      
      <div className="form-group">
        <label>Situation actuelle des dettes</label>
        <p className="info-box">💡 Les dettes actuelles sont pré-remplies depuis QBO</p>
        <div className="radio-group">
          {['normal', 'interest-only', 'renegotiation', 'frozen'].map(proj => (
            <label key={proj} className="radio-label">
              <input
                type="radio"
                checked={assumptions.debt.currentProjection === proj}
                onChange={() => updateAssumption('debt.currentProjection', proj)}
              />
              <span>
                {proj === 'normal' && '✅ Paiement normal (capital + intérêts)'}
                {proj === 'interest-only' && '📅 Intérêts seulement'}
                {proj === 'renegotiation' && '🤝 Renégociation prévue'}
                {proj === 'frozen' && '⏸️ Dette gelée temporairement'}
              </span>
            </label>
          ))}
        </div>
        {assumptions.debt.currentProjection === 'interest-only' && (
          <div className="form-group">
            <label>Nombre de mois</label>
            <input
              type="number"
              value={assumptions.debt.interestOnlyMonths || ''}
              onChange={(e) => {
                const val = e.target.value;
                updateAssumption('debt.interestOnlyMonths', val === '' ? null : parseInt(val) || null);
              }}
              placeholder="Ex: 6"
              className="number-input"
              min="1"
              max="60"
            />
          </div>
        )}
      </div>

      <div className="form-group">
        <label>Nouvelles dettes prévues ?</label>
        {assumptions.debt.newDebts.map((debt, idx) => (
          <div key={idx} className="trigger-row">
            <div className="trigger-field">
              <label className="trigger-label">Montant ($)</label>
              <input
                type="number"
                placeholder="Ex: 50000"
                value={debt.amount || ''}
                onChange={(e) => {
                  const val = e.target.value;
                  const updated = [...assumptions.debt.newDebts];
                  updated[idx].amount = val === '' ? null : parseFloat(val) || null;
                  updateAssumption('debt.newDebts', updated);
                }}
                className="number-input"
                min="0"
                step="0.01"
              />
            </div>
            <div className="trigger-field">
              <label className="trigger-label">Mois</label>
              <input
                type="number"
                placeholder="Ex: 6"
                value={debt.month || ''}
                onChange={(e) => {
                  const val = e.target.value;
                  const updated = [...assumptions.debt.newDebts];
                  updated[idx].month = val === '' ? null : parseInt(val) || null;
                  updateAssumption('debt.newDebts', updated);
                }}
                className="number-input small"
                min="1"
                max="36"
              />
            </div>
            <div className="trigger-field">
              <label className="trigger-label">Taux (%)</label>
              <input
                type="number"
                placeholder="Ex: 5.5"
                value={debt.rate || ''}
                onChange={(e) => {
                  const val = e.target.value;
                  const updated = [...assumptions.debt.newDebts];
                  updated[idx].rate = val === '' ? null : parseFloat(val) || null;
                  updateAssumption('debt.newDebts', updated);
                }}
                className="number-input small"
                min="0"
                max="100"
                step="0.1"
              />
            </div>
            <div className="trigger-field trigger-field-wide">
              <label className="trigger-label">Description</label>
              <input
                type="text"
                placeholder="Ex: Prêt bancaire"
                value={debt.description || ''}
                onChange={(e) => {
                  const updated = [...assumptions.debt.newDebts];
                  updated[idx].description = e.target.value;
                  updateAssumption('debt.newDebts', updated);
                }}
                className="text-input"
              />
              <span className="trigger-hint" style={{ fontSize: '0.75em', color: '#999', marginTop: '2px', visibility: 'hidden' }}>
                {/* Hint invisible pour maintenir l'alignement */}
              </span>
            </div>
            <button
              className="btn-small"
              onClick={() => {
                const updated = assumptions.debt.newDebts.filter((_, i) => i !== idx);
                updateAssumption('debt.newDebts', updated);
              }}
              title="Supprimer cette dette"
              style={{ alignSelf: 'flex-start', marginTop: '28px' }}
            >
              ✕
            </button>
          </div>
        ))}
        <button className="btn-secondary" onClick={addDebt}>
          + Ajouter une nouvelle dette
        </button>
      </div>

      <div className="form-group">
        <label>Injection d'équité possible ?</label>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={assumptions.equity.possible}
            onChange={(e) => updateAssumption('equity.possible', e.target.checked)}
          />
          <span>Oui</span>
        </label>
        {assumptions.equity.possible && (
          <>
            <div className="form-group">
              <label>Montant maximum ($)</label>
              <input
                type="number"
                value={assumptions.equity.maxAmount || ''}
                onChange={(e) => {
                  const val = e.target.value;
                  updateAssumption('equity.maxAmount', val === '' ? null : parseFloat(val) || null);
                }}
                placeholder="Ex: 100000"
                className="number-input"
                min="0"
                step="0.01"
              />
            </div>
            <div className="radio-group">
              {['certain', 'conditional', 'last-resort'].map(cert => (
                <label key={cert} className="radio-label">
                  <input
                    type="radio"
                    checked={assumptions.equity.certainty === cert}
                    onChange={() => updateAssumption('equity.certainty', cert)}
                  />
                  <span>
                    {cert === 'certain' && '✅ Certain'}
                    {cert === 'conditional' && '⚠️ Conditionnel'}
                    {cert === 'last-resort' && '🚨 Dernier recours'}
                  </span>
                </label>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );

  const renderStep5 = () => (
    <div className="questionnaire-step">
      <h3>💰 Hypothèses de Trésorerie</h3>
      
      <div className="form-group">
        <label>Seuil minimal de trésorerie souhaité ($)</label>
        <input
          type="number"
          value={assumptions.cash.minThreshold}
          onChange={(e) => updateAssumption('cash.minThreshold', parseFloat(e.target.value) || 0)}
          placeholder="Recommandé: 2-3 mois de coûts"
          className="number-input"
        />
        <p className="hint">💡 Recommandé: 2-3 mois de coûts opérationnels</p>
      </div>

      <div className="form-group">
        <label>Tolérance au déficit temporaire</label>
        <div className="radio-group">
          <label className="radio-label">
            <input
              type="radio"
              checked={!assumptions.cash.deficitTolerance.acceptable}
              onChange={() => updateAssumption('cash.deficitTolerance.acceptable', false)}
            />
            <span>❌ Aucune (cash toujours positif)</span>
          </label>
          <label className="radio-label">
            <input
              type="radio"
              checked={assumptions.cash.deficitTolerance.acceptable && !assumptions.cash.deficitTolerance.ifPlanClear}
              onChange={() => {
                updateAssumption('cash.deficitTolerance.acceptable', true);
                updateAssumption('cash.deficitTolerance.ifPlanClear', false);
              }}
            />
            <span>⚠️ Acceptable pendant X mois</span>
          </label>
          <label className="radio-label">
            <input
              type="radio"
              checked={assumptions.cash.deficitTolerance.ifPlanClear}
              onChange={() => updateAssumption('cash.deficitTolerance.ifPlanClear', true)}
            />
            <span>✅ Acceptable si plan clair</span>
          </label>
        </div>
        {assumptions.cash.deficitTolerance.acceptable && !assumptions.cash.deficitTolerance.ifPlanClear && (
          <div className="form-group">
            <label>Nombre de mois</label>
            <input
              type="number"
              value={assumptions.cash.deficitTolerance.maxMonths || ''}
              onChange={(e) => {
                const val = e.target.value;
                const updated = {
                  ...assumptions.cash.deficitTolerance,
                  maxMonths: val === '' ? null : parseInt(val) || null
                };
                updateAssumption('cash.deficitTolerance', updated);
              }}
              placeholder="Ex: 3"
              className="number-input"
              min="1"
              max="24"
            />
          </div>
        )}
      </div>

      <div className="form-group">
        <label>Priorité en cas de tension de trésorerie</label>
        <div className="radio-group">
          {['reduce-costs', 'accelerate-revenue', 'inject-funds', 'renegotiate-debt'].map(priority => (
            <label key={priority} className="radio-label">
              <input
                type="radio"
                checked={assumptions.cash.priorityIfTight === priority}
                onChange={() => updateAssumption('cash.priorityIfTight', priority)}
              />
              <span>
                {priority === 'reduce-costs' && '✂️ Réduction des coûts'}
                {priority === 'accelerate-revenue' && '🚀 Accélération des revenus'}
                {priority === 'inject-funds' && '💉 Injection de fonds'}
                {priority === 'renegotiate-debt' && '🤝 Renégociation dette'}
              </span>
            </label>
          ))}
        </div>
      </div>
    </div>
  );

  // Fonction pour ajouter un nouveau projet incorporel
  const addIntangibleProject = () => {
    const newProject = {
      project_id: `IP-${Date.now()}`,
      project_name: '',
      status: 'in_development',
      phase: 'development',
      criteria_ias38: {
        identifiable: false,
        control: false,
        future_economic_benefits_probable: false,
        technical_feasibility: false,
        intention_to_complete: false,
        ability_to_use_or_sell: false,
        adequate_resources: false,
        cost_measurable_reliably: false
      },
      capitalization_policy: {
        capitalize: false,
        salary_capitalization_share: assumptions.intangibles.globalSettings.defaultSalaryCapitalizationShare / 100,
        apply_share_to_overheads: assumptions.intangibles.globalSettings.applySalaryShareToOverheads,
        overhead_allocation_share: assumptions.intangibles.globalSettings.overheadAllocationShare / 100,
        capitalize_interest: assumptions.intangibles.globalSettings.capitalizeInterestWhenDirectlyAttributable
      },
      amortization: {
        amortize: false,
        method: 'straight_line',
        useful_life_years: 5
      }
    };
    updateAssumption('intangibles.projects', [...assumptions.intangibles.projects, newProject]);
  };

  // Fonction pour calculer si les critères IAS 38 sont remplis
  const checkIAS38Criteria = (criteria) => {
    const allCriteria = Object.values(criteria);
    const trueCount = allCriteria.filter(v => v === true).length;
    if (trueCount === allCriteria.length) return 'yes';
    if (trueCount >= allCriteria.length * 0.7) return 'partial';
    return 'no';
  };

  const renderStep7 = () => {
    const { intangibles } = assumptions;

    return (
      <div className="questionnaire-step">
        <h3>🏛️ Actifs Incorporels & Amortissement (IAS 38)</h3>
        <p className="step-description">
          Section pédagogique guidée pour la capitalisation des dépenses de développement selon les normes IFRS* (IAS 38).
        </p>
        <div className="info-box" style={{ background: '#f5f7fa', borderLeftColor: '#667eea', marginTop: '15px', marginBottom: '20px' }}>
          <p style={{ margin: 0, fontSize: '0.9em' }}>
            <strong>📚 Note sur les IFRS (Normes internationales d'information financière) :</strong>
          </p>
          <p style={{ marginTop: '8px', marginBottom: 0, fontSize: '0.9em', lineHeight: '1.6' }}>
            Le <strong>Conseil des normes comptables (CNC)</strong> au Canada exige que les entreprises ayant une 
            <strong> obligation publique de rendre des comptes</strong> utilisent les normes internationales d'information financière 
            (IFRS) pour la préparation de tous les états financiers intermédiaires et annuels.
          </p>
          <p style={{ marginTop: '8px', marginBottom: 0, fontSize: '0.9em', lineHeight: '1.6' }}>
            La plupart des <strong>entreprises privées</strong> ont aussi la possibilité d'adopter les IFRS pour la préparation des états financiers.
          </p>
          <p style={{ marginTop: '8px', marginBottom: 0, fontSize: '0.85em', fontStyle: 'italic', color: '#666' }}>
            * Cette section utilise les normes IFRS (IAS 38) comme référence pour la capitalisation des actifs incorporels. 
            Consultez votre comptable pour déterminer si les IFRS s'appliquent à votre entreprise.
          </p>
        </div>

        {/* 7.1 - Avez-vous des projets de développement technologique ou d'IP ? */}
        <div className="form-group">
          <label>7.1 — Avez-vous des projets de développement technologique ou d'IP ?</label>
          <div className="radio-group">
            <label className="radio-label">
              <input
                type="radio"
                checked={!intangibles.hasDevelopmentProjects}
                onChange={() => {
                  updateAssumption('intangibles.hasDevelopmentProjects', false);
                  updateAssumption('intangibles.projects', []);
                }}
              />
              <span>❌ Non → passer à la section suivante</span>
            </label>
            <label className="radio-label">
              <input
                type="radio"
                checked={intangibles.hasDevelopmentProjects}
                onChange={() => updateAssumption('intangibles.hasDevelopmentProjects', true)}
              />
              <span>✅ Oui → continuer</span>
            </label>
          </div>
          {intangibles.hasDevelopmentProjects && (
            <div className="info-box" style={{ marginTop: '15px' }}>
              <p><strong>💡 Explication AIA :</strong></p>
              <p>
                Certains coûts peuvent être considérés comme des investissements plutôt que des dépenses, 
                selon les normes comptables IFRS (IAS 38). Cela permet de refléter la vraie valeur économique 
                de votre entreprise technologique.
              </p>
              <p style={{ marginTop: '8px', fontSize: '0.9em', fontStyle: 'italic', color: '#666' }}>
                <strong>Rappel :</strong> Les IFRS sont obligatoires pour les entreprises ayant une obligation publique 
                de rendre des comptes au Canada, et optionnelles pour la plupart des entreprises privées.
              </p>
            </div>
          )}
        </div>

        {intangibles.hasDevelopmentProjects && (
          <>
            {/* Paramètres globaux (avant les projets) */}
            <div className="form-group" style={{ marginTop: '20px', padding: '15px', background: '#f5f7fa', borderRadius: '8px' }}>
              <label><strong>Paramètres globaux de capitalisation</strong></label>
              <div className="form-group">
                <label>% par défaut des salaires affectés au développement</label>
                <input
                  type="number"
                  value={intangibles.globalSettings.defaultSalaryCapitalizationShare || ''}
                  onChange={(e) => {
                    const val = e.target.value;
                    const updated = {
                      ...intangibles.globalSettings,
                      defaultSalaryCapitalizationShare: val === '' ? null : parseInt(val) || null
                    };
                    updateAssumption('intangibles.globalSettings', updated);
                  }}
                  placeholder="Ex: 80"
                  className="number-input"
                  min="0"
                  max="100"
                  step="1"
                />
                <p className="hint">💡 Cette valeur sera utilisée par défaut pour tous les nouveaux projets.</p>
              </div>
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={intangibles.globalSettings.applySalaryShareToOverheads}
                  onChange={(e) => {
                    const updated = {
                      ...intangibles.globalSettings,
                      applySalaryShareToOverheads: e.target.checked
                    };
                    updateAssumption('intangibles.globalSettings', updated);
                  }}
                />
                <span>✅ Appliquer le même % aux frais indirects par défaut</span>
              </label>
            </div>

            {/* Bouton ajouter un projet */}
            <div className="form-group" style={{ marginTop: '20px' }}>
              <button className="btn-secondary" onClick={addIntangibleProject}>
                + Ajouter un projet de développement
              </button>
            </div>

            {/* 7.2 - Critères IAS 38 */}
            {intangibles.projects.map((project, projectIdx) => {
              const criteriaResult = checkIAS38Criteria(project.criteria_ias38);
              const allCriteriaMet = criteriaResult === 'yes';
              const partialCriteria = criteriaResult === 'partial';

              return (
                <div key={project.project_id} className="revenue-category-card" style={{ marginTop: '20px' }}>
                  <h4>
                    Projet {projectIdx + 1}
                    {project.project_name && `: ${project.project_name}`}
                  </h4>

                  {/* Nom du projet */}
                  <div className="form-group">
                    <label>Nom du projet</label>
                    <input
                      type="text"
                      value={project.project_name || ''}
                      onChange={(e) => {
                        const updated = [...intangibles.projects];
                        updated[projectIdx].project_name = e.target.value;
                        updateAssumption('intangibles.projects', updated);
                      }}
                      placeholder="Ex: Technology Platform A"
                      className="text-input"
                    />
                  </div>

                  {/* 7.2 - Critères IAS 38 */}
                  <div className="form-group">
                    <label>7.2 — Le projet satisfait-il les critères IAS 38 ?</label>
                    <div className="info-box" style={{ marginTop: '10px', marginBottom: '15px' }}>
                      <p><strong>Critères requis pour la capitalisation :</strong></p>
                    </div>
                    <div className="checkbox-group">
                      {[
                        { key: 'identifiable', label: '✅ Faisabilité technique démontrée' },
                        { key: 'technical_feasibility', label: '✅ Intention de compléter le projet' },
                        { key: 'intention_to_complete', label: '✅ Capacité de mise en marché (licence, vente, usage interne)' },
                        { key: 'ability_to_use_or_sell', label: '✅ Avantages économiques futurs probables' },
                        { key: 'future_economic_benefits_probable', label: '✅ Coûts mesurables de façon fiable' },
                        { key: 'cost_measurable_reliably', label: '✅ Ressources adéquates disponibles' },
                        { key: 'adequate_resources', label: '✅ Contrôle sur l\'actif' },
                        { key: 'control', label: '✅ Projet identifiable distinctement' }
                      ].map(({ key, label }) => (
                        <label key={key} className="checkbox-label">
                          <input
                            type="checkbox"
                            checked={project.criteria_ias38[key] || false}
                            onChange={(e) => {
                              const updated = [...intangibles.projects];
                              updated[projectIdx].criteria_ias38[key] = e.target.checked;
                              // Mettre à jour capitalize selon les critères
                              const newCriteriaResult = checkIAS38Criteria(updated[projectIdx].criteria_ias38);
                              updated[projectIdx].capitalization_policy.capitalize = newCriteriaResult === 'yes' || newCriteriaResult === 'partial';
                              updateAssumption('intangibles.projects', updated);
                            }}
                          />
                          <span>{label}</span>
                        </label>
                      ))}
                    </div>
                    <div style={{ marginTop: '15px' }}>
                      {allCriteriaMet && (
                        <div className="info-box" style={{ background: '#e8f5e9', borderLeftColor: '#4caf50' }}>
                          ✅ <strong>Oui, globalement</strong> - Tous les critères sont remplis. Capitalisation recommandée.
                        </div>
                      )}
                      {partialCriteria && (
                        <div className="info-box" style={{ background: '#fff3e0', borderLeftColor: '#ff9800' }}>
                          ⚠️ <strong>Partiellement</strong> - Certains critères manquent. Capitalisation possible avec prudence.
                        </div>
                      )}
                      {!allCriteriaMet && !partialCriteria && Object.values(project.criteria_ias38).some(v => v) && (
                        <div className="error-box">
                          ❌ <strong>Non (tout en charges)</strong> - Les critères ne sont pas suffisamment remplis. 
                          Les coûts devraient être comptabilisés en charges.
                        </div>
                      )}
                    </div>
                  </div>

                      {/* 7.3 - Part des salaires affectée au développement */}
                      {project.capitalization_policy.capitalize && (
                        <>
                          <div className="form-group">
                            <label>7.3 — Part des salaires affectée au développement (%)</label>
                            <input
                              type="number"
                              value={project.capitalization_policy.salary_capitalization_share ? (project.capitalization_policy.salary_capitalization_share * 100).toFixed(0) : (intangibles.globalSettings.defaultSalaryCapitalizationShare || '')}
                              onChange={(e) => {
                                const val = e.target.value;
                                const updated = [...intangibles.projects];
                                updated[projectIdx].capitalization_policy.salary_capitalization_share = val === '' ? null : (parseFloat(val) || 0) / 100;
                                updateAssumption('intangibles.projects', updated);
                              }}
                              placeholder={`Ex: ${intangibles.globalSettings.defaultSalaryCapitalizationShare || 80}`}
                              className="number-input"
                              min="0"
                              max="100"
                              step="1"
                            />
                            <p className="hint">
                              💡 AIA propose une valeur basée sur l'historique (RS&DE, temps réel, projets).
                              Valeur par défaut : {intangibles.globalSettings.defaultSalaryCapitalizationShare || 80}%
                            </p>
                            <div className="form-group" style={{ marginTop: '10px' }}>
                              <label>Période concernée</label>
                              <div className="radio-group">
                                {[
                                  { value: 'current_month', label: '📅 Mois en cours' },
                                  { value: 'full_year', label: '📆 Année complète' },
                                  { value: 'specific_project', label: '🎯 Projet spécifique' }
                                ].map(({ value, label }) => (
                                  <label key={value} className="radio-label">
                                    <input
                                      type="radio"
                                      checked={(project.capitalization_policy.period || 'full_year') === value}
                                      onChange={() => {
                                        const updated = [...intangibles.projects];
                                        updated[projectIdx].capitalization_policy.period = value;
                                        updateAssumption('intangibles.projects', updated);
                                      }}
                                    />
                                    <span>{label}</span>
                                  </label>
                                ))}
                              </div>
                            </div>
                          </div>

                      {/* 7.4 - Application aux autres coûts */}
                      <div className="form-group">
                        <label>7.4 — Application de ce pourcentage aux autres coûts</label>
                        <div className="info-box" style={{ marginBottom: '15px' }}>
                          <p><strong>💡 AIA précise :</strong> Seuls les coûts directement attribuables peuvent être capitalisés selon les normes IFRS (IAS 38.66).</p>
                        </div>
                        <label className="checkbox-label">
                          <input
                            type="checkbox"
                            checked={project.capitalization_policy.apply_share_to_overheads}
                            onChange={(e) => {
                              const updated = [...intangibles.projects];
                              updated[projectIdx].capitalization_policy.apply_share_to_overheads = e.target.checked;
                              updateAssumption('intangibles.projects', updated);
                            }}
                          />
                          <span>✅ Appliquer le même pourcentage aux frais indirects</span>
                        </label>
                        {project.capitalization_policy.apply_share_to_overheads && (
                          <div style={{ marginLeft: '25px', marginTop: '10px' }}>
                            <label className="checkbox-label">
                              <input
                                type="checkbox"
                                checked={project.capitalization_policy.capitalize_interest}
                                onChange={(e) => {
                                  const updated = [...intangibles.projects];
                                  updated[projectIdx].capitalization_policy.capitalize_interest = e.target.checked;
                                  updateAssumption('intangibles.projects', updated);
                                }}
                              />
                              <span>Intérêts liés au financement du projet</span>
                            </label>
                          </div>
                        )}
                      </div>

                      {/* 7.5 - Statut du projet */}
                      <div className="form-group">
                        <label>7.5 — Statut du projet</label>
                        <div className="radio-group">
                          {[
                            { value: 'in_development', label: '🔨 Projet en développement (non terminé)', effect: 'Aucun amortissement' },
                            { value: 'in_use', label: '✅ Projet terminé et exploitable', effect: 'Amortissement à définir' },
                            { value: 'abandoned', label: '❌ Projet abandonné / non viable', effect: 'Passage en charge' }
                          ].map(({ value, label, effect }) => (
                            <label key={value} className="radio-label">
                              <input
                                type="radio"
                                checked={project.status === value}
                                onChange={() => {
                                  const updated = [...intangibles.projects];
                                  updated[projectIdx].status = value;
                                  if (value === 'in_use') {
                                    updated[projectIdx].amortization.amortize = true;
                                  } else {
                                    updated[projectIdx].amortization.amortize = false;
                                  }
                                  updateAssumption('intangibles.projects', updated);
                                }}
                              />
                              <span>
                                {label}
                                <span style={{ fontSize: '0.85em', color: '#666', display: 'block', marginTop: '5px' }}>
                                  Effet automatique AIA : {effect}
                                </span>
                              </span>
                            </label>
                          ))}
                        </div>
                      </div>

                      {/* 7.6 - Politique d'amortissement (si projet terminé) */}
                      {project.status === 'in_use' && (
                        <div className="form-group">
                          <label>7.6 — Politique d'amortissement</label>
                          <div className="form-group">
                            <label>Méthode d'amortissement</label>
                            <div className="radio-group">
                              {['straight_line', 'other'].map(method => (
                                <label key={method} className="radio-label">
                                  <input
                                    type="radio"
                                    checked={project.amortization.method === method}
                                    onChange={() => {
                                      const updated = [...intangibles.projects];
                                      updated[projectIdx].amortization.method = method;
                                      updateAssumption('intangibles.projects', updated);
                                    }}
                                  />
                                  <span>
                                    {method === 'straight_line' ? '📉 Linéaire' : '📊 Autre (expliquer)'}
                                  </span>
                                </label>
                              ))}
                            </div>
                          </div>
                          <div className="form-group">
                            <label>Durée de vie utile estimée</label>
                            <div className="radio-group">
                              {[3, 5, 7].map(years => (
                                <label key={years} className="radio-label">
                                  <input
                                    type="radio"
                                    checked={project.amortization.useful_life_years === years}
                                    onChange={() => {
                                      const updated = [...intangibles.projects];
                                      updated[projectIdx].amortization.useful_life_years = years;
                                      updateAssumption('intangibles.projects', updated);
                                    }}
                                  />
                                  <span>{years} ans</span>
                                </label>
                              ))}
                              <label className="radio-label">
                                <input
                                  type="radio"
                                  checked={project.amortization.useful_life_years && ![3, 5, 7].includes(project.amortization.useful_life_years)}
                                  onChange={() => {
                                    // Ne rien faire ici, juste pour le style
                                  }}
                                />
                                <span>Autre :</span>
                                <input
                                  type="number"
                                  value={project.amortization.useful_life_years && ![3, 5, 7].includes(project.amortization.useful_life_years) ? project.amortization.useful_life_years : ''}
                                  onChange={(e) => {
                                    const val = e.target.value;
                                    const updated = [...intangibles.projects];
                                    updated[projectIdx].amortization.useful_life_years = val === '' ? null : parseInt(val) || null;
                                    updateAssumption('intangibles.projects', updated);
                                  }}
                                  placeholder="ans"
                                  className="number-input small"
                                  style={{ marginLeft: '10px', width: '80px' }}
                                  min="1"
                                  max="20"
                                />
                              </label>
                            </div>
                            <p className="hint">
                              💡 AIA rappelle : Cette décision peut être révisée annuellement.
                            </p>
                          </div>
                        </div>
                      )}

                      {/* Bouton supprimer le projet */}
                      <button
                        className="btn-small"
                        onClick={() => {
                          const updated = intangibles.projects.filter((_, i) => i !== projectIdx);
                          updateAssumption('intangibles.projects', updated);
                        }}
                        style={{ marginTop: '15px' }}
                      >
                        🗑️ Supprimer ce projet
                      </button>
                    </>
                  )}
                </div>
              );
            })}

            {/* 7.7 - Présentation souhaitée des états financiers */}
            <div className="form-group">
              <label>7.7 — Présentation souhaitée des états financiers</label>
              <div className="info-box" style={{ marginBottom: '15px' }}>
                <p><strong>💡 AIA affiche un avertissement clair :</strong></p>
                <p style={{ fontStyle: 'italic', marginTop: '5px' }}>
                  « La capitalisation selon les normes IFRS n'augmente pas l'impôt, elle reflète la valeur économique de votre entreprise. »
                </p>
                <p style={{ marginTop: '8px', fontSize: '0.9em', color: '#666' }}>
                  <strong>Note importante :</strong> Les normes IFRS peuvent être obligatoires ou optionnelles selon votre type d'entreprise. 
                  Consultez votre comptable pour déterminer si elles s'appliquent à votre situation.
                </p>
              </div>
              <div className="radio-group">
                {[
                  { value: 'management', label: '📊 États de gestion (bilan économique réel)' },
                  { value: 'fiscal', label: '📋 Vision fiscale simplifiée (pour information)' },
                  { value: 'both', label: '📈 Les deux, clairement séparées' }
                ].map(({ value, label }) => (
                  <label key={value} className="radio-label">
                    <input
                      type="radio"
                      checked={intangibles.financialPresentation === value}
                      onChange={() => updateAssumption('intangibles.financialPresentation', value)}
                    />
                    <span>{label}</span>
                  </label>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    );
  };

  const renderStep8 = () => (
    <div className="questionnaire-step">
      <h3>📊 Scénarios Stratégiques</h3>
      
      <div className="form-group">
        <label>Scénario par défaut à présenter</label>
        <div className="radio-group">
          {['conservative', 'realistic', 'optimistic'].map(scenario => (
            <label key={scenario} className="radio-label">
              <input
                type="radio"
                checked={assumptions.scenarios.default === scenario}
                onChange={() => updateAssumption('scenarios.default', scenario)}
              />
              <span>
                {scenario === 'conservative' && '⚠️ Conservateur'}
                {scenario === 'realistic' && '✅ Réaliste (recommandé AIA)'}
                {scenario === 'optimistic' && '🚀 Ambitieux'}
              </span>
            </label>
          ))}
        </div>
      </div>

      <div className="form-group">
        <label>Souhaitez-vous comparer plusieurs scénarios ?</label>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={assumptions.scenarios.compare}
            onChange={(e) => updateAssumption('scenarios.compare', e.target.checked)}
          />
          <span>Oui</span>
        </label>
        {assumptions.scenarios.compare && (
          <div className="checkbox-group">
            {['conservative', 'realistic', 'optimistic'].map(scenario => (
              <label key={scenario} className="checkbox-label">
                <input
                  type="checkbox"
                  checked={assumptions.scenarios.comparedScenarios?.includes(scenario)}
                  onChange={(e) => {
                    const current = assumptions.scenarios.comparedScenarios || [];
                    const updated = e.target.checked
                      ? [...current, scenario]
                      : current.filter(s => s !== scenario);
                    updateAssumption('scenarios.comparedScenarios', updated);
                  }}
                />
                <span>
                  {scenario === 'conservative' && '⚠️ Conservateur'}
                  {scenario === 'realistic' && '✅ Réaliste'}
                  {scenario === 'optimistic' && '🚀 Ambitieux'}
                </span>
              </label>
            ))}
          </div>
        )}
      </div>
    </div>
  );

  const renderStep9 = () => {
    const canComplete = validateStep(0) && validateStep(1) && validateStep(8);
    
    return (
      <div className="questionnaire-step">
        <h3>✅ Validation Finale</h3>
        <div className="validation-summary">
          <h4>Récapitulatif des hypothèses</h4>
          
          <div className="summary-section">
            <strong>Contexte:</strong> {
              assumptions.context === 'banking' && '💼 Discussion bancaire'
              || assumptions.context === 'strategic' && '🎯 Décision stratégique'
              || assumptions.context === 'investor' && '💰 Investisseurs'
              || assumptions.context === 'operational' && '📊 Opérationnel'
              || assumptions.context === 'other' && `🔷 ${assumptions.contextOther || 'Autre'}`
            }
          </div>

          <div className="summary-section">
            <strong>Catégories de revenus configurées:</strong> {Object.keys(assumptions.revenueCategories).length}
          </div>

          <div className="summary-section">
            <strong>Scénario par défaut:</strong> {
              assumptions.scenarios.default === 'conservative' && '⚠️ Conservateur'
              || assumptions.scenarios.default === 'realistic' && '✅ Réaliste'
              || assumptions.scenarios.default === 'optimistic' && '🚀 Ambitieux'
            }
          </div>

          {assumptions.scenarios.compare && assumptions.scenarios.comparedScenarios?.length > 0 && (
            <div className="summary-section">
              <strong>Scénarios comparés:</strong> {assumptions.scenarios.comparedScenarios.length}
            </div>
          )}

          {!canComplete && (
            <div className="error-box">
              ⚠️ Veuillez compléter les sections obligatoires avant de valider.
            </div>
          )}
        </div>

        <div className="form-group">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={assumptions.validated}
              onChange={(e) => updateAssumption('validated', e.target.checked)}
            />
            <span>Je valide ces hypothèses et souhaite lancer les projections</span>
          </label>
        </div>
      </div>
    );
  };

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 0: return renderStep0();
      case 1: return renderStep1();
      case 2: return renderStep2();
      case 3: return renderStep3();
      case 4: return renderStep4();
      case 5: return renderStep5();
      case 6: return null; // Étape supprimée (était Scénarios, maintenant à l'étape 8)
      case 7: return renderStep7();
      case 8: return renderStep8();
      case 9: return renderStep9();
      default: return null;
    }
  };

  const handleNext = () => {
    if (validateStep(currentStep) && currentStep < 9) {
      let nextStep = currentStep + 1;
      // Étape 6 supprimée - passer directement à l'étape 7
      if (nextStep === 6) {
        nextStep = 7;
      }
      setCurrentStep(nextStep);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = () => {
    if (assumptions.validated && validateStep(0) && validateStep(1) && validateStep(8)) {
      const finalAssumptions = {
        ...assumptions,
        metadata: {
          version: '1.0',
          createdAt: new Date().toISOString(),
          context: assumptions.context
        }
      };
      onAssumptionsComplete(finalAssumptions);
    } else {
      alert('Veuillez valider les hypothèses et compléter les sections obligatoires.');
    }
  };

  const totalSteps = 10;
  const progress = ((currentStep + 1) / totalSteps) * 100;

  const handleOverlayClick = (e) => {
    // Empêcher la fermeture accidentelle - demander confirmation
    if (e.target === e.currentTarget) {
      if (window.confirm('Êtes-vous sûr de vouloir fermer le questionnaire ? Vos réponses seront perdues.')) {
        onClose();
      }
    }
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="modal-content questionnaire-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>📋 Questionnaire AIA – Hypothèses de Projection</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        {/* Barre de progression */}
        <div className="progress-bar-container">
          <div className="progress-bar" style={{ width: `${progress}%` }}></div>
        </div>
        <div className="step-indicator">
          Étape {currentStep + 1} sur {totalSteps}: {getStepTitle(currentStep)}
        </div>

        <div className="modal-body questionnaire-body">
          {renderCurrentStep()}
        </div>

        <div className="modal-footer">
          <button className="button button-secondary" onClick={handlePrevious} disabled={currentStep === 0}>
            ← Précédent
          </button>
          <button className="button button-secondary" onClick={onClose}>
            Sauvegarder et continuer plus tard
          </button>
          {currentStep < 9 ? (
            <button className="button" onClick={handleNext} disabled={!validateStep(currentStep)}>
              Suivant →
            </button>
          ) : (
            <button className="button" onClick={handleComplete} disabled={!assumptions.validated}>
              ✅ Valider et Générer les Projections
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default QuestionnaireHypotheses;
