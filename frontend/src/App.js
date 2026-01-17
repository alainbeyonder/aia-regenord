import React, { useEffect, useState } from 'react';
import './App.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

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
  const [resultTab, setResultTab] = useState('pnl');

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
    const response = await fetch(`${API_URL}/api/aia/assumptions?company_id=${companyId}`, {
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
    const response = await fetch(`${API_URL}/api/aia/runs?company_id=${companyId}`, {
      headers: authHeaders,
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'Failed to load simulation runs');
    }
    setSimulationRuns(data);
  };

  const createAssumptionSet = async () => {
    const companyId = getCompanyId();
    if (!companyId) return;
    setLoading(true);
    showStatus('', '');
    try {
      const response = await fetch(`${API_URL}/api/aia/assumptions`, {
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
      const response = await fetch(`${API_URL}/api/aia/assumptions/${assumptionId}/validate`, {
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
      const response = await fetch(`${API_URL}/api/aia/simulate`, {
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
      const response = await fetch(`${API_URL}/api/aia/runs/${runId}`, {
        headers: authHeaders,
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Run not found');
      }
      setSelectedRun(data);
      setResultTab('pnl');
    } catch (error) {
      showStatus('error', error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (event) => {
    event.preventDefault();
    setLoading(true);
    showStatus('', '');
    try {
      const response = await fetch(`${API_URL}/api/auth/login`, {
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
      const response = await fetch(`${API_URL}/api/auth/request-access`, {
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
      const response = await fetch(`${API_URL}/api/auth/set-password`, {
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
  };

  const uploadFile = async (fileType, file) => {
    if (!file) return;
    const formData = new FormData();
    formData.append('file_type', fileType);
    formData.append('file', file);

    const response = await fetch(`${API_URL}/api/files/upload`, {
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
                    <button className="secondary" type="button" onClick={() => loadRun(run.id)} disabled={loading}>
                      View result
                    </button>
                  </div>
                ))}
              </div>
              {selectedRun && (
                <div className="result">
                  <div className="tabs result-tabs">
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
                  <pre className="result-json">
                    {JSON.stringify(
                      resultTab === 'pnl'
                        ? selectedRun.result_json?.pnl_monthly
                        : resultTab === 'balance_sheet'
                          ? selectedRun.result_json?.balance_sheet_monthly
                          : selectedRun.result_json?.cashflow_monthly,
                      null,
                      2
                    )}
                  </pre>
                  <div className="hint">
                    Reconciliation delta:{' '}
                    {selectedRun.result_json?.reconciliation?.delta ?? 'n/a'}
                  </div>
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
