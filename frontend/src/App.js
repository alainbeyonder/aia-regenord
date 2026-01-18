import React, { useEffect, useState } from 'react';
import './App.css';

const API_BASE = (import.meta?.env?.VITE_API_BASE) || 'http://127.0.0.1:8000';

const initialLogin = { email: '', password: '' };
const initialRequest = { company_name: '', requester_name: '', email: '', phone: '', message: '' };
const defaultAssumptionPayload = {
  company_id: 1,
  scenario_default: 'realistic',
  horizon: { months_1: 12, years_2_3: 2 },
  revenue: {
    monthly_growth_rate: 0.05,
    events: [{ month: 4, name: 'New license', monthly_amount: 8000, probability: 0.8 }],
  },
  costs: {
    fixed_costs_annual_inflation: 0.03,
    events: [{ month: 6, name: 'New hire', monthly_amount: 6500 }],
    optimization: [{ category_key: 'expense_admin', reduction_percent: 0.1, start_month: 7 }],
  },
  debt: {
    mode: 'interest_only_then_resume',
    interest_only_months: 6,
    resume_mode: 'normal',
    equity_backstop: { enabled: true, max_amount: 65000, trigger_min_cash: 20000 },
  },
  rsde: {
    enabled: true,
    eligible_salary_share: 0.8,
    credit_estimated_amount: 75000,
    prudence_factor: 0.75,
    refund_delay_months: 9,
  },
  ias38: {
    enabled: true,
    capitalization_salary_share: 0.8,
    apply_to_overheads: true,
    overhead_share: 0.8,
    amortization: { enabled: false, start_month: 0, useful_life_years: 5 },
  },
};

function App() {
  const [activeTab, setActiveTab] = useState('signin');
  const [loginForm, setLoginForm] = useState(initialLogin);
  const [requestForm, setRequestForm] = useState(initialRequest);
  const [newPassword, setNewPassword] = useState('');
  const [status, setStatus] = useState({ type: '', message: '' });
  const [loading, setLoading] = useState(false);
  const [auth, setAuth] = useState({ token: null, user: null, mustChangePassword: false });
  const [uploadState, setUploadState] = useState({ pl: null, bs: null, loans: null });
  const [assumptionSets, setAssumptionSets] = useState([]);
  const [simulationRuns, setSimulationRuns] = useState([]);
  const [selectedRun, setSelectedRun] = useState(null);
  const [resultTab, setResultTab] = useState('summary');
  const [showMonthly, setShowMonthly] = useState(false);
  const [uploads, setUploads] = useState([]);
  const [pdfAnalysis, setPdfAnalysis] = useState(null);
  const [pdfTab, setPdfTab] = useState('client');

  useEffect(() => {
    const stored = localStorage.getItem('aia_auth');
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        if (parsed?.token) {
          setAuth(parsed);
        }
      } catch (error) {
        localStorage.removeItem('aia_auth');
      }
    }
  }, []);

  useEffect(() => {
    if (!auth.token || auth.mustChangePassword) return;
    fetchAssumptions();
    fetchRuns();
    fetchUploads();
  }, [auth.token, auth.mustChangePassword]);

  const persistAuth = (nextAuth) => {
    setAuth(nextAuth);
    localStorage.setItem('aia_auth', JSON.stringify(nextAuth));
  };

  const showStatus = (type, message) => setStatus({ type, message });

  const authHeaders = auth.token
    ? { Authorization: `Bearer ${auth.token}` }
    : {};

  const getCompanyId = () => auth.user?.company_id;

  const fetchAssumptions = async () => {
    const companyId = getCompanyId();
    if (!companyId) return;
    const response = await fetch(`${API_BASE}/api/aia/assumptions?company_id=${companyId}`, {
      headers: authHeaders,
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'Failed to load assumption sets');
    }
    setAssumptionSets(data);
  };

  const fetchRuns = async () => {
    const companyId = getCompanyId();
    if (!companyId) return;
    const response = await fetch(`${API_BASE}/api/aia/runs?company_id=${companyId}`, {
      headers: authHeaders,
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'Failed to load simulation runs');
    }
    setSimulationRuns(data);
  };

  const fetchUploads = async () => {
    const response = await fetch(`${API_BASE}/api/files/list`, {
      headers: authHeaders,
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'Failed to load uploads');
    }
    setUploads(data.uploads || []);
  };

  const createAssumptionSet = async () => {
    const companyId = getCompanyId();
    if (!companyId) return;
    setLoading(true);
    showStatus('', '');
    try {
      const response = await fetch(`${API_BASE}/api/aia/assumptions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeaders },
        body: JSON.stringify({
          company_id: companyId,
          name: `V1 Baseline ${new Date().toLocaleDateString()}`,
          scenario_key: 'realistic',
          payload_json: { ...defaultAssumptionPayload, company_id: companyId },
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to create assumption set');
      }
      await fetchAssumptions();
      showStatus('success', 'Assumption set created.');
    } catch (error) {
      showStatus('error', error.message);
    } finally {
      setLoading(false);
    }
  };

  const validateAssumptionSet = async (assumptionId) => {
    setLoading(true);
    showStatus('', '');
    try {
      const response = await fetch(`${API_BASE}/api/aia/assumptions/${assumptionId}/validate`, {
        method: 'POST',
        headers: authHeaders,
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Validation failed');
      }
      await fetchAssumptions();
      showStatus('success', 'Assumption set validated.');
    } catch (error) {
      showStatus('error', error.message);
    } finally {
      setLoading(false);
    }
  };

  const runSimulation = async (assumptionId) => {
    const companyId = getCompanyId();
    if (!companyId) return;
    setLoading(true);
    showStatus('', '');
    try {
      const response = await fetch(`${API_BASE}/api/aia/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeaders },
        body: JSON.stringify({
          company_id: companyId,
          assumption_set_id: assumptionId,
          period_start: new Date().toISOString().slice(0, 10),
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Simulation failed');
      }
      await fetchRuns();
      showStatus('success', `Simulation queued. Run ${data.run_id}.`);
    } catch (error) {
      showStatus('error', error.message);
    } finally {
      setLoading(false);
    }
  };

  const loadRun = async (runId) => {
    setLoading(true);
    showStatus('', '');
    try {
      const response = await fetch(`${API_BASE}/api/aia/runs/${runId}`, {
        headers: authHeaders,
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Run not found');
      }
      setSelectedRun(data);
      setResultTab('summary');
      setShowMonthly(false);
    } catch (error) {
      showStatus('error', error.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadRunPdf = async (runId) => {
    const companyId = getCompanyId();
    if (!companyId) return;
    setLoading(true);
    showStatus('', '');
    try {
      const response = await fetch(`${API_BASE}/api/aia/runs/${runId}/export.pdf`, {
        headers: authHeaders,
      });
      if (!response.ok) {
        throw new Error('PDF export failed');
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `AIA_Report_company${companyId}_run${runId}.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      showStatus('error', error.message);
    } finally {
      setLoading(false);
    }
  };

  const getYear1Total = (series = []) => series.reduce((sum, value) => sum + value, 0);

  const getYearTotals = (resultJson, key) => {
    if (!resultJson) return { year1: null, year2: null, year3: null };
    const year1 = getYear1Total(resultJson[key] || []);
    const year2 = resultJson[`${key.replace('_monthly', '')}_year2`]?.total ?? null;
    const year3 = resultJson[`${key.replace('_monthly', '')}_year3`]?.total ?? null;
    return { year1, year2, year3 };
  };

  const getMinimumCashMonth = (series = []) => {
    if (!series.length) return null;
    let minValue = series[0];
    let minIndex = 0;
    series.forEach((value, index) => {
      if (value < minValue) {
        minValue = value;
        minIndex = index;
      }
    });
    return { month: minIndex + 1, value: minValue };
  };

  const getClosingCashClass = (value) => {
    if (value == null) return '';
    if (value < 0) return 'cash-negative';
    if (value < 20000) return 'cash-warning';
    return 'cash-positive';
  };

  const handleLogin = async (event) => {
    event.preventDefault();
    setLoading(true);
    showStatus('', '');
    try {
      const response = await fetch(`${API_BASE}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(loginForm),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Login failed');
      }
      persistAuth({ token: data.access_token, user: data.user, mustChangePassword: data.must_change_password });
      showStatus('success', 'Signed in successfully.');
    } catch (error) {
      showStatus('error', error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRequestAccess = async (event) => {
    event.preventDefault();
    setLoading(true);
    showStatus('', '');
    try {
      const response = await fetch(`${API_BASE}/api/auth/request-access`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestForm),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Request failed');
      }
      showStatus('success', `Request submitted. Reference: ${data.request_id}.`);
      setRequestForm(initialRequest);
    } catch (error) {
      showStatus('error', error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSetPassword = async (event) => {
    event.preventDefault();
    setLoading(true);
    showStatus('', '');
    try {
      const response = await fetch(`${API_BASE}/api/auth/set-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${auth.token}`,
        },
        body: JSON.stringify({ new_password: newPassword }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Password update failed');
      }
      persistAuth({ ...auth, mustChangePassword: false });
      setNewPassword('');
      showStatus('success', 'Password updated.');
    } catch (error) {
      showStatus('error', error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('aia_auth');
    setAuth({ token: null, user: null, mustChangePassword: false });
    setLoginForm(initialLogin);
    showStatus('', '');
    setAssumptionSets([]);
    setSimulationRuns([]);
    setSelectedRun(null);
    setUploads([]);
    setPdfAnalysis(null);
  };

  const uploadFile = async (fileType, file) => {
    if (!file) return;
    const formData = new FormData();
    formData.append('file_type', fileType);
    formData.append('file', file);

    const response = await fetch(`${API_BASE}/api/files/upload`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${auth.token}`,
      },
      body: formData,
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'Upload failed');
    }
    return data;
  };

  const handleUpload = async () => {
    setLoading(true);
    showStatus('', '');
    try {
      await uploadFile('pl_pdf', uploadState.pl);
      await uploadFile('bs_pdf', uploadState.bs);
      if (uploadState.loans) {
        await uploadFile('loans_pdf', uploadState.loans);
      }
      showStatus('success', 'Files uploaded (metadata only).');
      setUploadState({ pl: null, bs: null, loans: null });
      await fetchUploads();
    } catch (error) {
      showStatus('error', error.message);
    } finally {
      setLoading(false);
    }
  };

  const getLatestUploadId = (type) => {
    const filtered = uploads.filter((item) => item.file_type === type);
    if (!filtered.length) return null;
    return filtered[0].id;
  };

  const analyzePdfs = async () => {
    const companyId = getCompanyId();
    if (!companyId) return;
    const plUploadId = getLatestUploadId('pl_pdf');
    const bsUploadId = getLatestUploadId('bs_pdf');
    const loansUploadId = getLatestUploadId('loans_pdf');
    if (!plUploadId || !bsUploadId) {
      showStatus('error', 'Upload both P&L and Balance Sheet first.');
      return;
    }
    setLoading(true);
    showStatus('', '');
    try {
      const response = await fetch(`${API_BASE}/api/aia/pdf/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeaders },
        body: JSON.stringify({
          company_id: companyId,
          pl_upload_id: plUploadId,
          bs_upload_id: bsUploadId,
          loans_upload_id: loansUploadId,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'PDF analysis failed');
      }
      setPdfAnalysis(data);
      setPdfTab('client');
      showStatus('success', 'PDF analysis completed.');
    } catch (error) {
      showStatus('error', error.message);
    } finally {
      setLoading(false);
    }
  };

  const loadLatestPdfAnalysis = async () => {
    const companyId = getCompanyId();
    if (!companyId) return;
    setLoading(true);
    showStatus('', '');
    try {
      const response = await fetch(`${API_BASE}/api/aia/pdf/analysis/latest?company_id=${companyId}`, {
        headers: authHeaders,
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'No analysis found');
      }
      setPdfAnalysis(data);
      setPdfTab('client');
      showStatus('success', 'Latest PDF analysis loaded.');
    } catch (error) {
      showStatus('error', error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="hero">
        <p className="eyebrow">AIA Intelligent</p>
        <h1>Understand Your Business. Not Just Your Accounting.</h1>
        <p className="subhead">
          AIA Intelligent transforms your financial data into clear, strategic insight.
        </p>
      </header>

      {status.message && (
        <div className={`status ${status.type}`}>{status.message}</div>
      )}

      {!auth.token ? (
        <section className="auth-card">
          <div className="tabs">
            <button
              className={activeTab === 'signin' ? 'tab active' : 'tab'}
              onClick={() => setActiveTab('signin')}
            >
              Sign in
            </button>
            <button
              className={activeTab === 'request' ? 'tab active' : 'tab'}
              onClick={() => setActiveTab('request')}
            >
              Request access
            </button>
          </div>

          {activeTab === 'signin' ? (
            <form className="form" onSubmit={handleLogin}>
              <label>
                Email
                <input
                  type="email"
                  value={loginForm.email}
                  onChange={(e) => setLoginForm({ ...loginForm, email: e.target.value })}
                  required
                />
              </label>
              <label>
                Password
                <input
                  type="password"
                  value={loginForm.password}
                  onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                  required
                />
              </label>
              <div className="form-row">
                <button className="primary" type="submit" disabled={loading}>
                  {loading ? 'Signing in...' : 'Sign in'}
                </button>
                <button
                  className="link"
                  type="button"
                  onClick={() => showStatus('info', 'Contact support@regenord.com')}
                  disabled={loading}
                >
                  Forgot password
                </button>
              </div>
            </form>
          ) : (
            <form className="form" onSubmit={handleRequestAccess}>
              <label>
                Company name
                <input
                  type="text"
                  value={requestForm.company_name}
                  onChange={(e) => setRequestForm({ ...requestForm, company_name: e.target.value })}
                  required
                />
              </label>
              <label>
                Full name
                <input
                  type="text"
                  value={requestForm.requester_name}
                  onChange={(e) => setRequestForm({ ...requestForm, requester_name: e.target.value })}
                  required
                />
              </label>
              <label>
                Email
                <input
                  type="email"
                  value={requestForm.email}
                  onChange={(e) => setRequestForm({ ...requestForm, email: e.target.value })}
                  required
                />
              </label>
              <label>
                Phone (optional)
                <input
                  type="text"
                  value={requestForm.phone}
                  onChange={(e) => setRequestForm({ ...requestForm, phone: e.target.value })}
                />
              </label>
              <label>
                Message (optional)
                <textarea
                  value={requestForm.message}
                  onChange={(e) => setRequestForm({ ...requestForm, message: e.target.value })}
                />
              </label>
              <button className="primary" type="submit" disabled={loading}>
                {loading ? 'Submitting...' : 'Request access'}
              </button>
            </form>
          )}

          <p className="note">PDF mode is available after sign-in to protect confidentiality.</p>
        </section>
      ) : auth.mustChangePassword ? (
        <section className="dashboard">
          <div className="dashboard-header">
            <div>
              <h2>Set new password</h2>
              <p>Temporary password detected. Please set a new one.</p>
            </div>
            <button className="secondary" onClick={handleLogout}>Log out</button>
          </div>
          <div className="card">
            <form className="form" onSubmit={handleSetPassword}>
              <label>
                New password
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                />
              </label>
              <button className="primary" type="submit" disabled={loading}>
                {loading ? 'Updating...' : 'Update password'}
              </button>
            </form>
          </div>
        </section>
      ) : (
        <section className="dashboard">
          <div className="dashboard-header">
            <div>
              <h2>Dashboard</h2>
              <p>Welcome {auth.user?.name || auth.user?.email}</p>
            </div>
            <button className="secondary" onClick={handleLogout}>Log out</button>
          </div>

          <div className="cards">
            <div className="card">
              <h3>Upload Financial PDFs</h3>
              <p>Upload your Profit & Loss and Balance Sheet PDFs.</p>
              <label className="file">
                Profit & Loss (PDF)
                <input type="file" accept="application/pdf" onChange={(e) => setUploadState({ ...uploadState, pl: e.target.files[0] })} />
              </label>
              <label className="file">
                Balance Sheet (PDF)
                <input type="file" accept="application/pdf" onChange={(e) => setUploadState({ ...uploadState, bs: e.target.files[0] })} />
              </label>
              <label className="file">
                Loan list (optional)
                <input type="file" accept="application/pdf" onChange={(e) => setUploadState({ ...uploadState, loans: e.target.files[0] })} />
              </label>
              <button className="primary" type="button" onClick={handleUpload} disabled={loading}>
                {loading ? 'Uploading...' : 'Upload'}
              </button>
              <div className="panel-actions">
                <button
                  className="secondary"
                  type="button"
                  onClick={analyzePdfs}
                  disabled={loading || !getLatestUploadId('pl_pdf') || !getLatestUploadId('bs_pdf')}
                >
                  Analyze PDFs
                </button>
                <button className="link" type="button" onClick={loadLatestPdfAnalysis} disabled={loading}>
                  Load latest analysis
                </button>
              </div>
              {pdfAnalysis && (
                <div className="result">
                  <div className="tabs result-tabs">
                    <button
                      className={pdfTab === 'client' ? 'tab active' : 'tab'}
                      type="button"
                      onClick={() => setPdfTab('client')}
                    >
                      Client View
                    </button>
                    <button
                      className={pdfTab === 'aia' ? 'tab active' : 'tab'}
                      type="button"
                      onClick={() => setPdfTab('aia')}
                    >
                      AIA View
                    </button>
                    <button
                      className={pdfTab === 'reconciliation' ? 'tab active' : 'tab'}
                      type="button"
                      onClick={() => setPdfTab('reconciliation')}
                    >
                      Reconciliation
                    </button>
                  </div>
                  {pdfTab === 'client' && (
                    <div className="table-block">
                      <h4>P&L rows</h4>
                      <table className="data-table">
                        <thead>
                          <tr>
                            <th>Label</th>
                            <th>Amount</th>
                          </tr>
                        </thead>
                        <tbody>
                          {(pdfAnalysis.client_view?.pnl?.rows || []).map((row, index) => (
                            <tr key={`pnl-${index}`}>
                              <td>{row.label}</td>
                              <td>{row.amount ?? 'n/a'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                      <h4>Balance Sheet rows</h4>
                      <table className="data-table">
                        <thead>
                          <tr>
                            <th>Label</th>
                            <th>Amount</th>
                          </tr>
                        </thead>
                        <tbody>
                          {(pdfAnalysis.client_view?.bs?.rows || []).map((row, index) => (
                            <tr key={`bs-${index}`}>
                              <td>{row.label}</td>
                              <td>{row.amount ?? 'n/a'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                  {pdfTab === 'aia' && (
                    <div className="table-block">
                      <h4>P&L categories</h4>
                      <table className="data-table">
                        <thead>
                          <tr>
                            <th>Category</th>
                            <th>Total</th>
                          </tr>
                        </thead>
                        <tbody>
                          {Object.entries(pdfAnalysis.aia_view?.pnl?.totals_by_category || {}).map(([key, value]) => (
                            <tr key={`pnl-cat-${key}`}>
                              <td>{key}</td>
                              <td>{value}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                      <h4>Balance Sheet categories</h4>
                      <table className="data-table">
                        <thead>
                          <tr>
                            <th>Category</th>
                            <th>Total</th>
                          </tr>
                        </thead>
                        <tbody>
                          {Object.entries(pdfAnalysis.aia_view?.bs?.totals_by_category || {}).map(([key, value]) => (
                            <tr key={`bs-cat-${key}`}>
                              <td>{key}</td>
                              <td>{value}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                  {pdfTab === 'reconciliation' && (
                    <div className="table-block">
                      <table className="data-table">
                        <thead>
                          <tr>
                            <th>Metric</th>
                            <th>P&L</th>
                            <th>Balance Sheet</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr>
                            <td>Client total</td>
                            <td>{pdfAnalysis.reconciliation?.pnl_delta?.client_total ?? 'n/a'}</td>
                            <td>{pdfAnalysis.reconciliation?.bs_delta?.client_total ?? 'n/a'}</td>
                          </tr>
                          <tr>
                            <td>AIA total</td>
                            <td>{pdfAnalysis.reconciliation?.pnl_delta?.aia_total ?? 'n/a'}</td>
                            <td>{pdfAnalysis.reconciliation?.bs_delta?.aia_total ?? 'n/a'}</td>
                          </tr>
                          <tr>
                            <td>Delta</td>
                            <td>{pdfAnalysis.reconciliation?.pnl_delta?.delta ?? 'n/a'}</td>
                            <td>{pdfAnalysis.reconciliation?.bs_delta?.delta ?? 'n/a'}</td>
                          </tr>
                        </tbody>
                      </table>
                      <div className="hint">
                        Warnings: {(pdfAnalysis.warnings || []).join(' • ') || 'none'}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            <div className="card">
              <h3>Assumption Sets</h3>
              <p>Create and validate assumption sets used for simulations.</p>
              <button className="primary" type="button" onClick={createAssumptionSet} disabled={loading}>
                Create new set
              </button>
              <div className="panel-list">
                {assumptionSets.length === 0 && <span className="hint">No assumption sets yet.</span>}
                {assumptionSets.map((item) => (
                  <div key={item.id} className="panel-row">
                    <div>
                      <strong>{item.name}</strong>
                      <div className="hint">#{item.id} · {item.scenario_key}</div>
                    </div>
                    <div className="panel-actions">
                      <span className={`tag ${item.status}`}>{item.status}</span>
                      {item.status !== 'validated' && (
                        <button className="secondary" type="button" onClick={() => validateAssumptionSet(item.id)} disabled={loading}>
                          Validate
                        </button>
                      )}
                      {item.status === 'validated' && (
                        <button className="primary" type="button" onClick={() => runSimulation(item.id)} disabled={loading}>
                          Simulate
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="card">
              <h3>Simulation Runs</h3>
              <p>Run and inspect simulation outputs.</p>
              <div className="panel-list">
                {simulationRuns.length === 0 && <span className="hint">No runs yet.</span>}
                {simulationRuns.map((run) => (
                  <div key={run.id} className="panel-row">
                    <div>
                      <strong>Run #{run.id}</strong>
                      <div className="hint">{run.period_start} → {run.period_end}</div>
                    </div>
                    <div className="panel-actions">
                      <button className="secondary" type="button" onClick={() => loadRun(run.id)} disabled={loading}>
                        View result
                      </button>
                      <button className="primary" type="button" onClick={() => downloadRunPdf(run.id)} disabled={loading}>
                        Download PDF
                      </button>
                    </div>
                  </div>
                ))}
              </div>
              {selectedRun && (
                <div className="result">
                  <div className="tabs result-tabs">
                    <button
                      className={resultTab === 'summary' ? 'tab active' : 'tab'}
                      type="button"
                      onClick={() => setResultTab('summary')}
                    >
                      Summary
                    </button>
                    <button
                      className={resultTab === 'pnl' ? 'tab active' : 'tab'}
                      type="button"
                      onClick={() => setResultTab('pnl')}
                    >
                      P&L
                    </button>
                    <button
                      className={resultTab === 'balance_sheet' ? 'tab active' : 'tab'}
                      type="button"
                      onClick={() => setResultTab('balance_sheet')}
                    >
                      Balance sheet
                    </button>
                    <button
                      className={resultTab === 'cashflow' ? 'tab active' : 'tab'}
                      type="button"
                      onClick={() => setResultTab('cashflow')}
                    >
                      Cashflow
                    </button>
                  </div>
                  {resultTab === 'summary' && (
                    <div className="summary-grid">
                      <div className="summary-card">
                        <span className="hint">Total revenue (Year 1)</span>
                        <strong>{getYearTotals(selectedRun.result_json, 'pnl_monthly').year1?.toFixed(2) ?? 'n/a'}</strong>
                      </div>
                      <div className="summary-card">
                        <span className="hint">EBITDA / Net result</span>
                        <strong>{selectedRun.result_json?.pnl_year1?.ebitda ?? selectedRun.result_json?.pnl_year2?.total ?? 'n/a'}</strong>
                      </div>
                      <div className="summary-card">
                        <span className="hint">Ending cash (Year 1)</span>
                        <strong>{(selectedRun.result_json?.cashflow_monthly || []).slice(-1)[0]?.toFixed(2) ?? 'n/a'}</strong>
                      </div>
                      <div className="summary-card">
                        <span className="hint">Minimum cash month</span>
                        <strong>
                          {(() => {
                            const minCash = getMinimumCashMonth(selectedRun.result_json?.cashflow_monthly || []);
                            return minCash ? `M${minCash.month} (${minCash.value.toFixed(2)})` : 'n/a';
                          })()}
                        </strong>
                      </div>
                      <div className="summary-card">
                        <span className="hint">Net debt end period</span>
                        <strong>{selectedRun.result_json?.balance_sheet_year3?.net_debt ?? 'n/a'}</strong>
                      </div>
                      <div className="summary-card">
                        <span className="hint">Reconciliation delta</span>
                        <strong>{selectedRun.result_json?.reconciliation?.delta ?? 'n/a'}</strong>
                      </div>
                    </div>
                  )}
                  {resultTab === 'pnl' && (
                    <div className="table-block">
                      <div className="table-header">
                        <h4>P&L summary</h4>
                        <label className="toggle">
                          <input
                            type="checkbox"
                            checked={showMonthly}
                            onChange={() => setShowMonthly(!showMonthly)}
                          />
                          Show monthly breakdown
                        </label>
                      </div>
                      <table className="data-table">
                        <thead>
                          <tr>
                            <th>Line item</th>
                            <th>Year 1 total</th>
                            <th>Year 2</th>
                            <th>Year 3</th>
                          </tr>
                        </thead>
                        <tbody>
                          {['Revenue', 'Operating Costs', 'EBITDA', 'Depreciation', 'Interest', 'Net Income'].map((label) => (
                            <tr key={label}>
                              <td>{label}</td>
                              <td>{getYearTotals(selectedRun.result_json, 'pnl_monthly').year1?.toFixed(2) ?? 'n/a'}</td>
                              <td>{getYearTotals(selectedRun.result_json, 'pnl_monthly').year2 ?? 'n/a'}</td>
                              <td>{getYearTotals(selectedRun.result_json, 'pnl_monthly').year3 ?? 'n/a'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                      {showMonthly && (
                        <pre className="result-json">
                          {JSON.stringify(selectedRun.result_json?.pnl_monthly || [], null, 2)}
                        </pre>
                      )}
                    </div>
                  )}
                  {resultTab === 'cashflow' && (
                    <div className="table-block">
                      <table className="data-table">
                        <thead>
                          <tr>
                            <th>Line item</th>
                            <th>Year 1 total</th>
                            <th>Year 2</th>
                            <th>Year 3</th>
                          </tr>
                        </thead>
                        <tbody>
                          {['Opening Cash', 'Operating Cash', 'Debt Service', 'RS&DE', 'Closing Cash'].map((label, index) => {
                            const totals = getYearTotals(selectedRun.result_json, 'cashflow_monthly');
                            const closingCash = (selectedRun.result_json?.cashflow_monthly || []).slice(-1)[0];
                            return (
                              <tr key={label}>
                                <td>{label}</td>
                                <td className={index === 4 ? getClosingCashClass(closingCash) : ''}>
                                  {(index === 4 ? closingCash : totals.year1)?.toFixed?.(2) ?? 'n/a'}
                                </td>
                                <td>{totals.year2 ?? 'n/a'}</td>
                                <td>{totals.year3 ?? 'n/a'}</td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  )}
                  {resultTab === 'balance_sheet' && (
                    <div className="table-block">
                      <table className="data-table">
                        <thead>
                          <tr>
                            <th>Line item</th>
                            <th>Year 1 total</th>
                            <th>Year 2</th>
                            <th>Year 3</th>
                          </tr>
                        </thead>
                        <tbody>
                          {['Assets', 'Liabilities', 'Equity', 'Intangible Assets'].map((label) => {
                            const totals = getYearTotals(selectedRun.result_json, 'balance_sheet_monthly');
                            return (
                              <tr key={label}>
                                <td>{label}</td>
                                <td>{totals.year1?.toFixed(2) ?? 'n/a'}</td>
                                <td>{totals.year2 ?? 'n/a'}</td>
                                <td>{totals.year3 ?? 'n/a'}</td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </section>
      )}

      <footer className="footer">
        <a href="/privacy" rel="noreferrer">Privacy Policy</a>
        <a href="/terms" rel="noreferrer">Terms of Service</a>
        <a href="mailto:support@regenord.com">Support</a>
        <span>© Regenord GROUP – AIA Intelligent</span>
      </footer>
    </div>
  );
}

export default App;
