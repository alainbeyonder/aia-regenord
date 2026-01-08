import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import QuestionnaireHypotheses from './QuestionnaireHypotheses';
import './App.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [healthStatus, setHealthStatus] = useState('checking');
  const [apiMessage, setApiMessage] = useState('');
  const [qboStatus, setQboStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showQBOData, setShowQBOData] = useState(false);
  const [qboData, setQboData] = useState(null);
  const [loadingQBOData, setLoadingQBOData] = useState(false);
  const [showAIAData, setShowAIAData] = useState(false);
  const [aiaData, setAiaData] = useState(null);
  const [loadingAIAData, setLoadingAIAData] = useState(false);
  const [showProjections, setShowProjections] = useState(false);
  const [projectionParams, setProjectionParams] = useState({
    revenueGrowth: 10,
    expenseGrowth: 5,
    months: 36
  });
  const [showSettings, setShowSettings] = useState(false);
  const [exportLoading, setExportLoading] = useState(false);
  const [showQuestionnaire, setShowQuestionnaire] = useState(false);
  const [projectionAssumptions, setProjectionAssumptions] = useState(null);
  const [projectionsGenerated, setProjectionsGenerated] = useState(false);
  const [settings, setSettings] = useState({
    defaultMonths: 12,
    reconciliationTolerance: 0.01,
    projectionGrowth: {
      revenue: 10,
      expense: 5
    }
  });

  const checkQBOStatus = async (companyId) => {
    try {
      const response = await axios.get(`${API_URL}/api/qbo/status?company_id=${companyId}`);
      setQboStatus(response.data);
    } catch (error) {
      console.error('Erreur lors de la vérification du statut QBO:', error);
    }
  };

  useEffect(() => {
    // Vérifier la connexion au backend
    axios.get(`${API_URL}/health`)
      .then(response => {
        setHealthStatus('healthy');
        setApiMessage('Connexion au backend réussie');
      })
      .catch(error => {
        setHealthStatus('error');
        setApiMessage(`Erreur de connexion: ${error.message}`);
      });

    // Vérifier le statut QBO (company_id=1 par défaut)
    checkQBOStatus(1);

    // Charger automatiquement les données AIA
    const loadAIAData = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/aia/view?company_id=1&months=12`);
        setAiaData(response.data);
      } catch (error) {
        console.error('Erreur lors du chargement des données AIA:', error);
      }
    };
    loadAIAData();

    // Vérifier si on revient d'une connexion OAuth réussie
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('qbo_connected') === 'true') {
      const realmId = urlParams.get('realm_id');
      setApiMessage(`✅ QuickBooks connecté avec succès! Realm ID: ${realmId}`);
      // Rafraîchir le statut
      setTimeout(() => checkQBOStatus(1), 1000);
      // Nettoyer l'URL
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []);

  const handleSyncQBO = async () => {
    setLoading(true);
    const companyId = 1;
    
    try {
      const response = await axios.post(
        `${API_URL}/api/qbo/sync`,
        { company_id: companyId, months: 12 }
      );
      
      if (response.data && response.data.status === 'ok') {
        setApiMessage('✅ Synchronisation réussie! Rechargement des données...');
        // Recharger les données AIA
        setTimeout(async () => {
          try {
            const aiaResponse = await axios.get(`${API_URL}/api/aia/view?company_id=1&months=12`);
            setAiaData(aiaResponse.data);
            setApiMessage('✅ Données mises à jour');
          } catch (error) {
            console.error('Erreur lors du rechargement des données:', error);
            setApiMessage('⚠️ Synchronisation réussie mais erreur lors du rechargement');
          }
        }, 2000);
      }
    } catch (error) {
      console.error('Erreur lors de la synchronisation:', error);
      setApiMessage(`❌ Erreur de synchronisation: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleConnectQBO = async () => {
    setLoading(true);
    const companyId = 1; // Pour le MVP, utiliser company_id=1
    
    try {
      // Obtenir l'URL d'autorisation OAuth (Production)
      const response = await axios.get(
        `${API_URL}/api/qbo/connect/production?company_id=${companyId}&redirect=false`
      );
      
      if (response.data && response.data.auth_url) {
        // Rediriger vers l'URL OAuth d'Intuit
        window.location.href = response.data.auth_url;
      } else {
        alert('Erreur: Impossible d\'obtenir l\'URL de connexion QuickBooks');
        setLoading(false);
      }
    } catch (error) {
      console.error('Erreur lors de la connexion QuickBooks:', error);
      alert(`Erreur lors de la connexion QuickBooks: ${error.response?.data?.detail || error.message}`);
      setLoading(false);
    }
  };

  const handleViewAIA = async () => {
    setLoadingAIAData(true);
    setShowAIAData(true);
    const companyId = 1;
    const months = 12;
    
    try {
      const response = await axios.get(`${API_URL}/api/aia/view?company_id=${companyId}&months=${months}`);
      setAiaData(response.data);
    } catch (error) {
      console.error('Erreur lors de la récupération de la vue AIA:', error);
      alert(`Erreur: ${error.response?.data?.detail || error.message}`);
      setShowAIAData(false);
    } finally {
      setLoadingAIAData(false);
    }
  };

  const handleCloseAIAData = () => {
    setShowAIAData(false);
    setAiaData(null);
  };

  const handleGenerateProjections = async () => {
    // Recharger les données AIA avant d'ouvrir le questionnaire
    if (!aiaData) {
      try {
        const response = await axios.get(`${API_URL}/api/aia/view?company_id=1&months=12`);
        setAiaData(response.data);
      } catch (error) {
        console.error('Erreur lors du chargement des données AIA:', error);
      }
    }
    // Ouvrir le questionnaire d'hypothèses
    setShowQuestionnaire(true);
  };

  const handleAssumptionsComplete = (assumptions) => {
    setProjectionAssumptions(assumptions);
    setProjectionsGenerated(true); // Marquer les projections comme générées
    setShowQuestionnaire(false);
    setShowProjections(true);
    console.log('Hypothèses validées:', assumptions);
  };

  const handleCloseProjections = () => {
    setShowProjections(false);
  };

  const handleExportGoogleSheets = async (format = 'csv') => {
    setExportLoading(true);
    const companyId = 1;
    const months = 12;
    
    try {
      const url = `${API_URL}/api/aia/export/google-sheets?company_id=${companyId}&months=${months}&format=${format}`;
      console.log('🔵 Tentative d\'export:', format, 'vers', url);
      
      // Utiliser fetch avec gestion explicite
      const response = await fetch(url);
      console.log('🔵 Réponse reçue:', response.status, response.statusText);
      console.log('🔵 Headers:', {
        contentType: response.headers.get('content-type'),
        contentDisposition: response.headers.get('content-disposition')
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Erreur de réponse:', errorText);
        throw new Error(`Erreur ${response.status}: ${response.statusText}. ${errorText.substring(0, 200)}`);
      }
      
      // Pour CSV, obtenir le texte
      if (format === 'csv') {
        const text = await response.text();
        console.log('🔵 CSV reçu:', text.length, 'caractères');
        
        if (!text || text.length === 0) {
          throw new Error('Le fichier CSV est vide');
        }
        
        // Créer un blob avec le bon type MIME
        const blob = new Blob([text], { type: 'text/csv;charset=utf-8;' });
        const downloadUrl = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = `aia_financial_view_${companyId}_${new Date().toISOString().split('T')[0]}.csv`;
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        setTimeout(() => {
          document.body.removeChild(link);
          URL.revokeObjectURL(downloadUrl);
        }, 100);
      } else {
        // Pour JSON
        const jsonData = await response.json();
        console.log('🔵 JSON reçu:', Object.keys(jsonData));
        
        const jsonString = JSON.stringify(jsonData, null, 2);
        const blob = new Blob([jsonString], { type: 'application/json;charset=utf-8;' });
        const downloadUrl = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = `aia_financial_view_${companyId}_${new Date().toISOString().split('T')[0]}.json`;
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        setTimeout(() => {
          document.body.removeChild(link);
          URL.revokeObjectURL(downloadUrl);
        }, 100);
      }
      
      console.log(`✅ Export ${format.toUpperCase()} téléchargé avec succès!`);
    } catch (error) {
      console.error('❌ Erreur complète lors de l\'export:', error);
      console.error('❌ Stack:', error.stack);
      alert(`❌ Erreur lors de l'export ${format.toUpperCase()}:\n\n${error.message}\n\nVoir la console pour plus de détails.`);
    } finally {
      setExportLoading(false);
    }
  };

  const handleViewGraphs = async () => {
    // Ouvrir la Vue AIA qui contient déjà tous les graphiques
    if (!aiaData) {
      // Charger les données d'abord
      await handleViewAIA();
    } else {
      // Afficher directement si les données sont déjà chargées
      setLoadingAIAData(false); // S'assurer que le loading est à false
      setShowAIAData(true);
    }
  };

  const handleShowSettings = () => {
    setShowSettings(true);
  };

  const handleCloseSettings = () => {
    setShowSettings(false);
  };

  const calculateProjections = () => {
    if (!aiaData) return [];
    
    const projections = [];
    const baseDate = new Date(aiaData.period_end);
    const totals = aiaData.totals_by_category || {};
    
    // Calculer les totaux de base (dernière période)
    let baseRevenue = 0;
    let baseExpenses = 0;
    
    Object.values(totals).forEach(cat => {
      const total = cat.total || 0;
      const name = cat.name || '';
      if (name.toLowerCase().includes('revenu')) {
        baseRevenue += total;
      } else if (name.toLowerCase().includes('dépense') || name.toLowerCase().includes('expense')) {
        baseExpenses += total;
      }
    });
    
    // Si pas de données, utiliser des valeurs par défaut pour la démo
    if (baseRevenue === 0) baseRevenue = 100000;
    if (baseExpenses === 0) baseExpenses = 80000;
    
    // Calculer les projections mensuelles
    for (let month = 0; month < projectionParams.months; month++) {
      const date = new Date(baseDate);
      date.setMonth(date.getMonth() + month + 1);
      
      const revenueGrowth = (projectionParams.revenueGrowth / 100) / 12; // Mensuel
      const expenseGrowth = (projectionParams.expenseGrowth / 100) / 12; // Mensuel
      
      const projectedRevenue = baseRevenue * Math.pow(1 + revenueGrowth, month);
      const projectedExpenses = baseExpenses * Math.pow(1 + expenseGrowth, month);
      const projectedProfit = projectedRevenue - projectedExpenses;
      
      projections.push({
        month: date.toLocaleDateString('fr-CA', { month: 'short', year: 'numeric' }),
        revenue: projectedRevenue,
        expenses: projectedExpenses,
        profit: projectedProfit,
        period: month + 1
      });
    }
    
    return projections;
  };

  const handleViewQBO = async () => {
    setLoadingQBOData(true);
    setShowQBOData(true);
    const companyId = 1;
    const months = 12;
    
    try {
      const response = await axios.get(`${API_URL}/api/qbo/data?company_id=${companyId}&months=${months}`);
      setQboData(response.data);
    } catch (error) {
      console.error('Erreur lors de la récupération des données QBO:', error);
      alert(`Erreur lors de la récupération des données QBO: ${error.response?.data?.detail || error.message}`);
      setShowQBOData(false);
    } finally {
      setLoadingQBOData(false);
    }
  };

  const handleCloseQBOData = () => {
    setShowQBOData(false);
    setQboData(null);
  };

  // Composant pour afficher la Vue AIA avec graphiques
  const AIADataView = () => {
    if (!showAIAData) return null;
    
    if (loadingAIAData) {
      return (
        <div className="modal-overlay" onClick={handleCloseAIAData}>
          <div className="modal-content aia-data-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>📈 Vue Financière AIA</h2>
              <button className="close-button" onClick={handleCloseAIAData}>×</button>
            </div>
            <div className="modal-body">
              <p>Chargement des données...</p>
            </div>
          </div>
        </div>
      );
    }

    if (!aiaData) return null;

    const { totals_by_category, reconciliation, period_start, period_end } = aiaData;
    
    // Préparer les données pour les graphiques
    const chartData = [];
    const categoryKeys = Object.keys(totals_by_category);
    const firstCategory = categoryKeys.length > 0 ? totals_by_category[categoryKeys[0]] : null;
    const months = firstCategory && firstCategory.monthly_totals ? Object.keys(firstCategory.monthly_totals) : [];
    
    months.forEach(month => {
      const monthData = { month: month.substring(5) }; // Afficher seulement MM
      Object.entries(totals_by_category).forEach(([key, cat]) => {
        const amount = cat.monthly_totals?.[month] || 0;
        if (Math.abs(amount) > 0.01) {
          monthData[cat.name] = amount;
        }
      });
      if (Object.keys(monthData).length > 1) {
        chartData.push(monthData);
      }
    });

    // Données pour le graphique par catégorie (pie)
    const categoryTotals = Object.entries(totals_by_category)
      .map(([key, cat]) => ({
        name: cat.name,
        value: Math.abs(cat.total || 0),
        confidence: cat.confidence_score
      }))
      .filter(item => item.value > 0)
      .sort((a, b) => b.value - a.value);

    const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b', '#fa709a', '#fee140', '#30cfd0', '#a8edea'];

    // Données réconciliation
    const reconciliationData = [
      { name: 'Total QBO', value: reconciliation.total_qbo },
      { name: 'Total AIA', value: reconciliation.total_aia },
    ];

    return (
      <div className="modal-overlay" onClick={handleCloseAIAData}>
        <div className="modal-content aia-data-modal" onClick={(e) => e.stopPropagation()}>
          <div className="modal-header">
            <h2>📈 Vue Financière AIA - Analyse Agregée</h2>
            <button className="close-button" onClick={handleCloseAIAData}>×</button>
          </div>
          <div className="modal-body">
            {/* Période et réconciliation */}
            <div className="aia-section">
              <h3>📅 Période analysée</h3>
              <p><strong>Début:</strong> {period_start} | <strong>Fin:</strong> {period_end}</p>
              <div className="reconciliation-box">
                <h4>✅ Réconciliation</h4>
                <div className="reconciliation-stats">
                  <div className="recon-item">
                    <span className="label">Total QBO:</span>
                    <span className="value">${reconciliation.total_qbo.toLocaleString('fr-CA', { minimumFractionDigits: 2 })}</span>
                  </div>
                  <div className="recon-item">
                    <span className="label">Total AIA:</span>
                    <span className="value">${reconciliation.total_aia.toLocaleString('fr-CA', { minimumFractionDigits: 2 })}</span>
                  </div>
                  <div className="recon-item">
                    <span className="label">Delta:</span>
                    <span className={`value ${Math.abs(reconciliation.delta) < 0.01 ? 'ok' : 'warning'}`}>
                      ${Math.abs(reconciliation.delta).toLocaleString('fr-CA', { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                  <div className="recon-item">
                    <span className="label">Statut:</span>
                    <span className={`status ${reconciliation.reconciled ? 'reconciled' : 'not-reconciled'}`}>
                      {reconciliation.reconciled ? '✅ Réconcilié' : '⚠️ Écart'}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Graphique des tendances mensuelles */}
            {chartData.length > 0 && (
              <div className="aia-section">
                <h3>📊 Évolution Mensuelle par Catégorie</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip formatter={(value) => `$${value.toLocaleString('fr-CA', { minimumFractionDigits: 2 })}`} />
                    <Legend />
                    {categoryTotals.slice(0, 5).map((cat, idx) => (
                      <Line 
                        key={cat.name} 
                        type="monotone" 
                        dataKey={cat.name} 
                        stroke={COLORS[idx % COLORS.length]} 
                        strokeWidth={2}
                      />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* Graphique par catégorie (barres) */}
            {categoryTotals.length > 0 && (
              <div className="aia-section">
                <h3>📊 Totaux par Catégorie</h3>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={categoryTotals.slice(0, 10)}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                    <YAxis />
                    <Tooltip formatter={(value) => `$${value.toLocaleString('fr-CA', { minimumFractionDigits: 2 })}`} />
                    <Bar dataKey="value" fill="#667eea" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* Tableau des catégories */}
            <div className="aia-section">
              <h3>📋 Détails par Catégorie</h3>
              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Catégorie</th>
                      <th>Total</th>
                      <th>Confiance</th>
                      <th>Nb Comptes</th>
                    </tr>
                  </thead>
                  <tbody>
                    {categoryTotals.map((cat, idx) => (
                      <tr key={idx}>
                        <td>{cat.name}</td>
                        <td className={cat.value < 0 ? 'amount-negative' : 'amount-positive'}>
                          ${Math.abs(cat.value).toLocaleString('fr-CA', { minimumFractionDigits: 2 })}
                        </td>
                        <td>
                          <span className={`confidence-badge ${cat.confidence > 0.7 ? 'high' : cat.confidence > 0.5 ? 'medium' : 'low'}`}>
                            {(cat.confidence * 100).toFixed(0)}%
                          </span>
                        </td>
                        <td>{totals_by_category[Object.keys(totals_by_category).find(k => totals_by_category[k].name === cat.name)]?.accounts_count || 0}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Composant pour le simulateur de projections
  const ProjectionsSimulator = () => {
    if (!showProjections) return null;

    const projections = calculateProjections();
    
    // Données pour graphiques
    const projectionChartData = projections.map(p => ({
      période: p.period,
      revenus: p.revenue,
      dépenses: p.expenses,
      profit: p.profit
    }));

    const cumulativeData = [];
    let cumulativeProfit = 0;
    projections.forEach(p => {
      cumulativeProfit += p.profit;
      cumulativeData.push({
        période: p.period,
        'Profit cumulatif': cumulativeProfit
      });
    });

    return (
      <div className="modal-overlay" onClick={handleCloseProjections}>
        <div className="modal-content projections-modal" onClick={(e) => e.stopPropagation()}>
          <div className="modal-header">
            <h2>🚀 Simulateur de Projections Financières 3 Ans</h2>
            <button className="close-button" onClick={handleCloseProjections}>×</button>
          </div>
          <div className="modal-body">
            {/* Paramètres du simulateur */}
            <div className="simulator-section">
              <h3>⚙️ Paramètres de Projection</h3>
              <div className="simulator-controls">
                <div className="control-group">
                  <label>
                    Croissance des revenus (%/an):
                    <input
                      type="number"
                      value={projectionParams.revenueGrowth}
                      onChange={(e) => setProjectionParams({...projectionParams, revenueGrowth: parseFloat(e.target.value) || 0})}
                      min="0"
                      max="100"
                      step="1"
                    />
                    <span className="control-value">{projectionParams.revenueGrowth}%</span>
                  </label>
                </div>
                <div className="control-group">
                  <label>
                    Croissance des dépenses (%/an):
                    <input
                      type="number"
                      value={projectionParams.expenseGrowth}
                      onChange={(e) => setProjectionParams({...projectionParams, expenseGrowth: parseFloat(e.target.value) || 0})}
                      min="0"
                      max="100"
                      step="1"
                    />
                    <span className="control-value">{projectionParams.expenseGrowth}%</span>
                  </label>
                </div>
                <div className="control-group">
                  <label>
                    Période (mois):
                    <input
                      type="number"
                      value={projectionParams.months}
                      onChange={(e) => setProjectionParams({...projectionParams, months: parseInt(e.target.value) || 12})}
                      min="12"
                      max="36"
                      step="12"
                    />
                    <span className="control-value">{projectionParams.months} mois</span>
                  </label>
                </div>
              </div>
            </div>

            {/* Graphique des projections */}
            <div className="simulator-section">
              <h3>📈 Projections Revenus / Dépenses / Profit</h3>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={projectionChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="période" />
                  <YAxis />
                  <Tooltip formatter={(value) => `$${value.toLocaleString('fr-CA', { minimumFractionDigits: 2 })}`} />
                  <Legend />
                  <Line type="monotone" dataKey="revenus" stroke="#4caf50" strokeWidth={3} />
                  <Line type="monotone" dataKey="dépenses" stroke="#f44336" strokeWidth={3} />
                  <Line type="monotone" dataKey="profit" stroke="#2196f3" strokeWidth={3} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Graphique profit cumulatif */}
            <div className="simulator-section">
              <h3>💰 Profit Cumulatif</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={cumulativeData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="période" />
                  <YAxis />
                  <Tooltip formatter={(value) => `$${value.toLocaleString('fr-CA', { minimumFractionDigits: 2 })}`} />
                  <Bar dataKey="Profit cumulatif" fill="#2196f3" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Tableau des projections */}
            <div className="simulator-section">
              <h3>📋 Détails des Projections</h3>
              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Période</th>
                      <th>Revenus</th>
                      <th>Dépenses</th>
                      <th>Profit</th>
                      <th>Profit Cumulatif</th>
                    </tr>
                  </thead>
                  <tbody>
                    {projections.slice(0, 12).map((proj, idx) => {
                      const cumul = projections.slice(0, idx + 1).reduce((sum, p) => sum + p.profit, 0);
                      return (
                        <tr key={idx}>
                          <td>{proj.month}</td>
                          <td className="amount-positive">${proj.revenue.toLocaleString('fr-CA', { minimumFractionDigits: 2 })}</td>
                          <td className="amount-negative">${proj.expenses.toLocaleString('fr-CA', { minimumFractionDigits: 2 })}</td>
                          <td className={proj.profit >= 0 ? 'amount-positive' : 'amount-negative'}>
                            ${proj.profit.toLocaleString('fr-CA', { minimumFractionDigits: 2 })}
                          </td>
                          <td className={cumul >= 0 ? 'amount-positive' : 'amount-negative'}>
                            ${cumul.toLocaleString('fr-CA', { minimumFractionDigits: 2 })}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Résumé */}
            <div className="simulator-section">
              <h3>📊 Résumé des Projections</h3>
              <div className="summary-cards">
                <div className="summary-card">
                  <div className="summary-label">Revenus Total (période)</div>
                  <div className="summary-value positive">
                    ${projections.reduce((sum, p) => sum + p.revenue, 0).toLocaleString('fr-CA', { minimumFractionDigits: 2 })}
                  </div>
                </div>
                <div className="summary-card">
                  <div className="summary-label">Dépenses Total (période)</div>
                  <div className="summary-value negative">
                    ${projections.reduce((sum, p) => sum + p.expenses, 0).toLocaleString('fr-CA', { minimumFractionDigits: 2 })}
                  </div>
                </div>
                <div className="summary-card">
                  <div className="summary-label">Profit Total</div>
                  <div className={`summary-value ${projections.reduce((sum, p) => sum + p.profit, 0) >= 0 ? 'positive' : 'negative'}`}>
                    ${projections.reduce((sum, p) => sum + p.profit, 0).toLocaleString('fr-CA', { minimumFractionDigits: 2 })}
                  </div>
                </div>
                <div className="summary-card">
                  <div className="summary-label">Profit Final</div>
                  <div className={`summary-value ${projections[projections.length - 1]?.profit >= 0 ? 'positive' : 'negative'}`}>
                    ${projections[projections.length - 1]?.profit.toLocaleString('fr-CA', { minimumFractionDigits: 2 }) || '0.00'}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Gestionnaire de sauvegarde des paramètres
  const handleSaveSettings = () => {
    localStorage.setItem('aiaSettings', JSON.stringify(settings));
    alert('✅ Paramètres sauvegardés!');
    handleCloseSettings();
  };

  // Charger les paramètres depuis localStorage au démarrage
  useEffect(() => {
    const savedSettings = localStorage.getItem('aiaSettings');
    if (savedSettings) {
      try {
        setSettings(JSON.parse(savedSettings));
      } catch (error) {
        console.error('Erreur lors du chargement des paramètres:', error);
      }
    }
  }, []);

  // Composant pour les paramètres/configuration
  const SettingsView = () => {
    if (!showSettings) return null;

    return (
      <div className="modal-overlay" onClick={handleCloseSettings}>
        <div className="modal-content settings-modal" onClick={(e) => e.stopPropagation()}>
          <div className="modal-header">
            <h2>⚙️ Configuration et Paramètres</h2>
            <button className="close-button" onClick={handleCloseSettings}>×</button>
          </div>
          <div className="modal-body">
            <div className="settings-section">
              <h3>📊 Paramètres de Vue Financière</h3>
              <div className="settings-group">
                <label>
                  Période par défaut (mois):
                  <input
                    type="number"
                    value={settings.defaultMonths}
                    onChange={(e) => setSettings({...settings, defaultMonths: parseInt(e.target.value) || 12})}
                    min="1"
                    max="36"
                  />
                </label>
              </div>
              <div className="settings-group">
                <label>
                  Tolérance de réconciliation ($):
                  <input
                    type="number"
                    step="0.01"
                    value={settings.reconciliationTolerance}
                    onChange={(e) => setSettings({...settings, reconciliationTolerance: parseFloat(e.target.value) || 0.01})}
                    min="0"
                    max="1"
                  />
                </label>
              </div>
            </div>

            <div className="settings-section">
              <h3>🚀 Paramètres de Projections</h3>
              <div className="settings-group">
                <label>
                  Croissance revenus par défaut (%/an):
                  <input
                    type="number"
                    value={settings.projectionGrowth.revenue}
                    onChange={(e) => setSettings({
                      ...settings, 
                      projectionGrowth: {...settings.projectionGrowth, revenue: parseFloat(e.target.value) || 10}
                    })}
                    min="0"
                    max="100"
                  />
                </label>
              </div>
              <div className="settings-group">
                <label>
                  Croissance dépenses par défaut (%/an):
                  <input
                    type="number"
                    value={settings.projectionGrowth.expense}
                    onChange={(e) => setSettings({
                      ...settings, 
                      projectionGrowth: {...settings.projectionGrowth, expense: parseFloat(e.target.value) || 5}
                    })}
                    min="0"
                    max="100"
                  />
                </label>
              </div>
            </div>

            <div className="settings-section">
              <h3>📈 Informations Système</h3>
              <div className="info-group">
                <div className="info-item">
                  <span className="info-label">Version:</span>
                  <span className="info-value">AIA Regenord v1.0</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Backend API:</span>
                  <span className="info-value">{API_URL}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Environnement QBO:</span>
                  <span className="info-value">Production</span>
                </div>
              </div>
            </div>

            <div className="settings-actions">
              <button className="button" onClick={handleSaveSettings}>
                💾 Sauvegarder
              </button>
              <button className="button button-secondary" onClick={handleCloseSettings}>
                Annuler
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Composant pour afficher les données QBO
  const QBODataView = () => {
    if (!showQBOData) return null;
    
    if (loadingQBOData) {
      return (
        <div className="modal-overlay" onClick={handleCloseQBOData}>
          <div className="modal-content qbo-data-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>📊 Données QBO Brutes</h2>
              <button className="close-button" onClick={handleCloseQBOData}>×</button>
            </div>
            <div className="modal-body">
              <p>Chargement des données...</p>
            </div>
          </div>
        </div>
      );
    }

    if (!qboData) return null;

    const { statistics, accounts, transactions, snapshots, anomalies } = qboData;
    const { critical, warning, info } = anomalies;

    return (
      <div className="modal-overlay" onClick={handleCloseQBOData}>
        <div className="modal-content qbo-data-modal" onClick={(e) => e.stopPropagation()}>
          <div className="modal-header">
            <h2>📊 Données QBO Brutes - Analyse d'Anomalies</h2>
            <button className="close-button" onClick={handleCloseQBOData}>×</button>
          </div>
          <div className="modal-body">
            {/* Statistiques */}
            <div className="qbo-section">
              <h3>📈 Statistiques</h3>
              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-value">{statistics.total_accounts}</div>
                  <div className="stat-label">Comptes</div>
                  <div className="stat-sublabel">{statistics.active_accounts} actifs</div>
                </div>
                <div className="stat-card">
                  <div className="stat-value">{statistics.total_transactions}</div>
                  <div className="stat-label">Transactions</div>
                  <div className="stat-sublabel">{new Date(statistics.period_start).toLocaleDateString()} - {new Date(statistics.period_end).toLocaleDateString()}</div>
                </div>
                <div className="stat-card">
                  <div className="stat-value">{statistics.total_snapshots}</div>
                  <div className="stat-label">Snapshots</div>
                </div>
                <div className="stat-card">
                  <div className="stat-value">${statistics.total_amount?.toLocaleString('fr-CA', { minimumFractionDigits: 2 })}</div>
                  <div className="stat-label">Montant Total</div>
                </div>
              </div>
            </div>

            {/* Anomalies */}
            {(critical.length > 0 || warning.length > 0 || info.length > 0) && (
              <div className="qbo-section">
                <h3>⚠️ Analyse d'Anomalies</h3>
                <div className="anomalies-summary">
                  <span className={`badge critical`}>{anomalies.summary.critical_count} Critique</span>
                  <span className={`badge warning`}>{anomalies.summary.warning_count} Avertissement</span>
                  <span className={`badge info`}>{anomalies.summary.info_count} Info</span>
                </div>

                {/* Anomalies critiques */}
                {critical.length > 0 && (
                  <div className="anomalies-group critical">
                    <h4>🔴 Critiques ({critical.length})</h4>
                    {critical.map((anomaly, idx) => (
                      <div key={idx} className="anomaly-card critical">
                        <div className="anomaly-title">{anomaly.title}</div>
                        <div className="anomaly-description">{anomaly.description}</div>
                        {anomaly.details && anomaly.details.length > 0 && (
                          <details className="anomaly-details">
                            <summary>Voir détails ({anomaly.count} au total)</summary>
                            <pre>{JSON.stringify(anomaly.details, null, 2)}</pre>
                          </details>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {/* Anomalies warnings */}
                {warning.length > 0 && (
                  <div className="anomalies-group warning">
                    <h4>🟡 Avertissements ({warning.length})</h4>
                    {warning.map((anomaly, idx) => (
                      <div key={idx} className="anomaly-card warning">
                        <div className="anomaly-title">{anomaly.title}</div>
                        <div className="anomaly-description">{anomaly.description}</div>
                        {anomaly.details && anomaly.details.length > 0 && (
                          <details className="anomaly-details">
                            <summary>Voir détails ({anomaly.count} au total)</summary>
                            <pre>{JSON.stringify(anomaly.details, null, 2)}</pre>
                          </details>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {/* Anomalies info */}
                {info.length > 0 && (
                  <div className="anomalies-group info">
                    <h4>ℹ️ Informations ({info.length})</h4>
                    {info.map((anomaly, idx) => (
                      <div key={idx} className="anomaly-card info">
                        <div className="anomaly-title">{anomaly.title}</div>
                        <div className="anomaly-description">{anomaly.description}</div>
                        {anomaly.details && anomaly.details.length > 0 && (
                          <details className="anomaly-details">
                            <summary>Voir détails ({anomaly.count} au total)</summary>
                            <pre>{JSON.stringify(anomaly.details, null, 2)}</pre>
                          </details>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Comptes */}
            <div className="qbo-section">
              <h3>📋 Comptes ({accounts.length})</h3>
              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Nom</th>
                      <th>Type</th>
                      <th>Sous-type</th>
                      <th>Classification</th>
                      <th>Statut</th>
                    </tr>
                  </thead>
                  <tbody>
                    {accounts.slice(0, 20).map((acc, idx) => (
                      <tr key={idx}>
                        <td>{acc.name}</td>
                        <td>{acc.account_type || '-'}</td>
                        <td>{acc.account_subtype || '-'}</td>
                        <td>{acc.classification || '-'}</td>
                        <td>
                          <span className={`status-badge ${acc.active ? 'active' : 'inactive'}`}>
                            {acc.active ? 'Actif' : 'Inactif'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {accounts.length > 20 && <p className="table-footer">Affiche 20 sur {accounts.length} comptes</p>}
              </div>
            </div>

            {/* Transactions */}
            <div className="qbo-section">
              <h3>💰 Transactions ({transactions.length})</h3>
              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Type</th>
                      <th>Montant</th>
                      <th>Contrepartie</th>
                      <th>Mémo</th>
                    </tr>
                  </thead>
                  <tbody>
                    {transactions.slice(0, 20).map((txn, idx) => (
                      <tr key={idx}>
                        <td>{new Date(txn.txn_date).toLocaleDateString()}</td>
                        <td>{txn.txn_type || '-'}</td>
                        <td className={txn.amount >= 0 ? 'amount-positive' : 'amount-negative'}>
                          ${Math.abs(txn.amount).toLocaleString('fr-CA', { minimumFractionDigits: 2 })}
                        </td>
                        <td>{txn.counterparty || '-'}</td>
                        <td className="memo-cell">{txn.memo || '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {transactions.length > 20 && <p className="table-footer">Affiche 20 sur {transactions.length} transactions</p>}
              </div>
            </div>

            {/* Snapshots */}
            {snapshots.length > 0 && (
              <div className="qbo-section">
                <h3>📸 Snapshots ({snapshots.length})</h3>
                <div className="table-container">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Type</th>
                        <th>Période Début</th>
                        <th>Période Fin</th>
                        <th>Créé le</th>
                        <th>Données</th>
                      </tr>
                    </thead>
                    <tbody>
                      {snapshots.map((snap, idx) => (
                        <tr key={idx}>
                          <td>{snap.report_type}</td>
                          <td>{snap.period_start ? new Date(snap.period_start).toLocaleDateString() : '-'}</td>
                          <td>{snap.period_end ? new Date(snap.period_end).toLocaleDateString() : '-'}</td>
                          <td>{snap.created_at ? new Date(snap.created_at).toLocaleString() : '-'}</td>
                          <td>
                            <span className={`status-badge ${snap.has_data ? 'active' : 'inactive'}`}>
                              {snap.has_data ? 'Oui' : 'Non'}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="App">
      {showQuestionnaire && (
        <QuestionnaireHypotheses
          aiaData={aiaData}
          onAssumptionsComplete={handleAssumptionsComplete}
          onClose={() => setShowQuestionnaire(false)}
        />
      )}
      <QBODataView />
      <AIADataView />
      <ProjectionsSimulator />
      <SettingsView />
      <div className="container">
        <header>
          <h1>📊 AIA Regenord</h1>
          <p className="subtitle">Agent IA Financier - Projections Financières 3 Ans</p>
          <p className="subtitle">Groupe Regenord</p>
        </header>

        <div className="status-banner">
          <div className={`status-indicator ${healthStatus}`}>
            {healthStatus === 'checking' && '🔄 Vérification de la connexion...'}
            {healthStatus === 'healthy' && '✅ Backend connecté'}
            {healthStatus === 'error' && '❌ Backend non accessible'}
          </div>
          {apiMessage && <p className="status-message">{apiMessage}</p>}
        </div>

        <div className="dashboard">
          <div className="card">
            <h3>🔗 QuickBooks Online</h3>
            <p>Connectez votre compte QuickBooks pour extraire automatiquement vos données financières.</p>
            {qboStatus && qboStatus.connected ? (
              <span className="status active">✅ Connecté</span>
            ) : qboStatus && !qboStatus.connected ? (
              <span className="status pending">❌ Déconnecté</span>
            ) : (
              <span className="status pending">⏳ En attente</span>
            )}
            {qboStatus && qboStatus.connected ? (
              <>
                <button 
                  className="button" 
                  onClick={handleSyncQBO}
                  disabled={loading}
                  style={{ marginBottom: '10px' }}
                >
                  {loading ? '⏳ Synchronisation...' : '🔄 Synchroniser les données'}
                </button>
                <p style={{ fontSize: '0.9em', color: '#666', marginTop: '10px' }}>
                  Realm ID: {qboStatus.realm_id}
                </p>
                {qboStatus.last_sync_at && (
                  <p style={{ fontSize: '0.85em', color: '#888', marginTop: '5px' }}>
                    Dernière sync: {new Date(qboStatus.last_sync_at).toLocaleString('fr-CA')}
                  </p>
                )}
              </>
            ) : (
              <button 
                className="button" 
                onClick={handleConnectQBO}
                disabled={loading}
              >
                {loading ? 'Connexion en cours...' : 'Connecter QBO'}
              </button>
            )}
            {qboStatus && !qboStatus.connected && (
              <p style={{ fontSize: '0.9em', color: '#f44336', marginTop: '10px' }}>
                ⚠️ Token expiré - Veuillez reconnecter
              </p>
            )}
          </div>

          <div className="card">
            <h3>📈 Projections Financières</h3>
            <p>Générez des projections sur 3 ans basées sur vos données historiques et l'IA.</p>
            <span className={`status ${projectionsGenerated ? 'active' : (aiaData ? 'pending' : 'pending')}`}>
              {projectionsGenerated ? '✅ Générées' : (aiaData ? 'Prêt à générer' : 'Non générées')}
            </span>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '15px' }}>
              <button className="button" onClick={handleGenerateProjections} disabled={!aiaData}>
                🚀 Simuler Projections
              </button>
              <button className="button button-secondary" onClick={handleViewAIA}>
                📊 Voir Vue AIA
              </button>
              <button className="button button-secondary" onClick={handleViewQBO}>
                📋 Voir Vue QBO
              </button>
            </div>
          </div>

          <div className="card">
            <h3>📊 Visualisations</h3>
            <p>Consultez vos graphiques de revenus, dépenses et profits projetés.</p>
            <span className={`status ${aiaData ? 'active' : 'pending'}`}>
              {aiaData ? '✅ Disponible' : '⏳ Chargement...'}
            </span>
            <button className="button" onClick={handleViewGraphs} disabled={!aiaData}>
              📈 Voir Graphiques
            </button>
          </div>

          <div className="card">
            <h3>💾 Export Google Sheets</h3>
            <p>Exportez vos données financières au format CSV ou JSON pour Google Sheets.</p>
            <span className={`status ${aiaData ? 'active' : 'pending'}`}>
              {aiaData ? '✅ Prêt à exporter' : '❌ Données non disponibles'}
            </span>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '15px' }}>
              <button
                className="button"
                onClick={() => handleExportGoogleSheets('csv')}
                disabled={exportLoading}
              >
                {exportLoading ? '⏳ Export en cours...' : '📥 Télécharger CSV'}
              </button>
              <button
                className="button button-secondary"
                onClick={() => handleExportGoogleSheets('json')}
                disabled={exportLoading}
              >
                {exportLoading ? '⏳ Export en cours...' : '📥 Télécharger JSON'}
              </button>
              <p style={{ fontSize: '0.85em', color: '#666', marginTop: '10px', fontStyle: 'italic' }}>
                💡 Alternative: Ouvrir{' '}
                <a href={`${API_URL}/api/aia/export/google-sheets?company_id=1&months=12&format=csv`} target="_blank" rel="noopener noreferrer" style={{ color: '#667eea' }}>
                  ce lien
                </a>
                {' '}dans un nouvel onglet pour télécharger directement
              </p>
            </div>
          </div>

          <div className="card">
            <h3>⚙️ Configuration</h3>
            <p>Gérez vos paramètres, hypothèses de croissance et modèles de projection.</p>
            <button className="button" onClick={handleShowSettings}>
              ⚙️ Paramètres
            </button>
          </div>

          <div className="card">
            <h3>📝 Documentation API</h3>
            <p>Accédez à la documentation complète de l'API FastAPI.</p>
            <a href={`${API_URL}/docs`} target="_blank" rel="noopener noreferrer" className="button">
              Voir API Docs
            </a>
          </div>
        </div>

        <footer>
          <p>&copy; 2025 Groupe Regenord | AIA Regenord v1.0</p>
          <p>Propulsé par FastAPI, OpenAI GPT-4, QuickBooks Online API</p>
          <p>Backend: {API_URL}</p>
        </footer>
      </div>
    </div>
  );
}

export default App;
