/* ═══════════════════════════════════════════════════
   ClaimCheck AI — app.js
   ═══════════════════════════════════════════════════ */

const BASE_URL  = 'http://54.84.210.86:8000';
const API_URL   = BASE_URL + '/predict-claim';
const LOGIN_URL = BASE_URL + '/auth/login';

/* ══════════════════════════════════════
   TOKEN HELPERS
══════════════════════════════════════ */
function getToken()  { return localStorage.getItem('claimiq_token'); }
function setToken(t) { localStorage.setItem('claimiq_token', t); }
function clearToken(){ localStorage.removeItem('claimiq_token'); localStorage.removeItem('claimiq_user'); }
function getUser()   { return JSON.parse(localStorage.getItem('claimiq_user') || '{}'); }
function setUser(u)  { localStorage.setItem('claimiq_user', JSON.stringify(u)); }

/* ══════════════════════════════════════
   ON LOAD
══════════════════════════════════════ */
window.addEventListener('load', () => {
  if (!getToken()) showLoginModal();
  else             applyLoggedInState();
  checkAPI();
});

/* ══════════════════════════════════════
   LOGIN MODAL
══════════════════════════════════════ */
function showLoginModal(mode = 'login') {
  if (document.getElementById('login-overlay')) return;

  const isSignup = mode === 'signup';

  const overlay = document.createElement('div');
  overlay.id = 'login-overlay';
  overlay.style.cssText = `
    position:fixed;inset:0;z-index:9999;
    background:rgba(0,0,0,0.75);backdrop-filter:blur(8px);
    display:flex;align-items:center;justify-content:center;
  `;

  overlay.innerHTML = `
    <div id="login-box" style="
      background:var(--surface);border:1px solid var(--border2);
      border-radius:18px;padding:2.5rem;width:100%;max-width:420px;
      animation:fade-up 0.4s ease both;
    ">
      <div style="text-align:center;margin-bottom:2rem;">
        <div style="font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;color:var(--accent);display:flex;align-items:center;justify-content:center;gap:10px;">
          <span style="width:10px;height:10px;border-radius:50%;background:var(--accent2);display:inline-block;animation:pulse-dot 2s infinite;"></span>
          ClaimCheck AI
        </div>
        <div id="auth-title" style="font-size:0.82rem;color:var(--text3);margin-top:0.4rem;letter-spacing:1px;text-transform:uppercase;">
          ${isSignup ? 'Create Account' : ''}
        </div>
      </div>

      <div style="margin-bottom:1rem;">
        <label style="display:block;font-size:0.78rem;font-weight:500;color:var(--text2);margin-bottom:0.4rem;">Username</label>
        <input id="login-username" type="text" placeholder="username"
          style="width:100%;background:var(--bg2);border:1px solid var(--border);border-radius:8px;
                 color:var(--text);font-family:'DM Sans',sans-serif;font-size:0.88rem;
                 padding:0.65rem 0.9rem;outline:none;transition:border-color 0.2s;"
          onfocus="this.style.borderColor='var(--accent)'"
          onblur="this.style.borderColor='var(--border)'"
          onkeydown="if(event.key==='Enter')doAuth()"
        >
      </div>

      <div style="margin-bottom:1rem;">
        <label style="display:block;font-size:0.78rem;font-weight:500;color:var(--text2);margin-bottom:0.4rem;">Password</label>
        <input id="login-password" type="password" placeholder="password"
          style="width:100%;background:var(--bg2);border:1px solid var(--border);border-radius:8px;
                 color:var(--text);font-family:'DM Sans',sans-serif;font-size:0.88rem;
                 padding:0.65rem 0.9rem;outline:none;transition:border-color 0.2s;"
          onfocus="this.style.borderColor='var(--accent)'"
          onblur="this.style.borderColor='var(--border)'"
          onkeydown="if(event.key==='Enter')doAuth()"
        >
      </div>

      <div id="password-rules" style="
        display:${isSignup ? 'block' : 'none'};
        margin-top:-0.4rem;margin-bottom:1rem;
        font-size:0.75rem;color:var(--text3);line-height:1.5;
      ">
        Password must:
        <div style="margin-top:0.35rem;padding-left:0.5rem;">
          • Be at least 6 characters long<br>
          • Contain letters and numbers recommended<br>
          • Avoid common/simple passwords
        </div>
      </div>

      <div id="confirm-wrap" style="margin-bottom:1rem; display:${isSignup ? 'block' : 'none'};">
        <label style="display:block;font-size:0.78rem;font-weight:500;color:var(--text2);margin-bottom:0.4rem;">Confirm Password</label>
        <input id="login-confirm-password" type="password" placeholder="Confirm Password"
          style="width:100%;background:var(--bg2);border:1px solid var(--border);border-radius:8px;
                 color:var(--text);font-family:'DM Sans',sans-serif;font-size:0.88rem;
                 padding:0.65rem 0.9rem;outline:none;transition:border-color 0.2s;"
          onfocus="this.style.borderColor='var(--accent)'"
          onblur="this.style.borderColor='var(--border)'"
          onkeydown="if(event.key==='Enter')doAuth()"
        >
      </div>

      <div id="login-error" style="
        display:none;background:rgba(248,113,113,0.08);
        border:1px solid rgba(248,113,113,0.25);border-radius:8px;
        padding:0.6rem 0.9rem;color:var(--danger);
        font-size:0.82rem;margin-bottom:1rem;
      "></div>

      <button id="login-btn" onclick="doAuth()" style="
        width:100%;padding:0.85rem;background:var(--accent);
        color:#fff;border:none;border-radius:10px;
        font-family:'Syne',sans-serif;font-size:0.92rem;font-weight:700;
        cursor:pointer;transition:all 0.2s;letter-spacing:0.5px;
      ">${isSignup ? 'Create Account →' : 'Sign In →'}</button>

      <div style="text-align:center;margin-top:1rem;font-size:0.8rem;color:var(--text3);">
        ${isSignup
          ? `Already have an account? <a href="#" onclick="switchAuthMode('login'); return false;" style="color:var(--accent2);text-decoration:none;">Sign in</a>`
          : `Don't have an account? <a href="#" onclick="switchAuthMode('signup'); return false;" style="color:var(--accent2);text-decoration:none;">Sign up</a>`
        }
      </div>
    </div>
  `;

  document.body.appendChild(overlay);
  setTimeout(() => document.getElementById('login-username')?.focus(), 100);
}

function switchAuthMode(mode) {
  document.getElementById('login-overlay')?.remove();
  showLoginModal(mode);
}

async function doAuth() {
  const username  = document.getElementById('login-username').value.trim();
  const password  = document.getElementById('login-password').value;
  const confirmEl = document.getElementById('login-confirm-password');
  const confirmPassword = confirmEl ? confirmEl.value : '';
  const isSignup  = document.getElementById('confirm-wrap').style.display !== 'none';
  const errBox    = document.getElementById('login-error');
  const btn       = document.getElementById('login-btn');

  if (!username || !password) { showLoginError('Please enter username and password.'); return; }
  if (isSignup && !confirmPassword) { showLoginError('Please confirm your password.'); return; }
  if (isSignup && password !== confirmPassword) { showLoginError('Passwords do not match.'); return; }

  btn.textContent = isSignup ? 'Creating account…' : 'Signing in…';
  btn.disabled = true;
  errBox.style.display = 'none';

  try {
    const url  = isSignup ? (BASE_URL + '/auth/signup') : LOGIN_URL;
    const body = isSignup
      ? { username, password, confirm_password: confirmPassword }
      : { username, password };

    const resp = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(10000),
    });

    if (!resp.ok) {
      const err = await resp.json();
      if (Array.isArray(err.detail)) showLoginError(err.detail.map(e => e.msg).join(', '));
      else showLoginError(err.detail || 'Auth failed.');
      return;
    }

    const data = await resp.json();
    setToken(data.access_token);
    setUser({ name: data.name, role: data.role, username });

    document.getElementById('login-overlay')?.remove();
    applyLoggedInState();

  } catch(e) {
    showLoginError(e.name === 'TimeoutError' ? 'Server not responding.' : `Error: ${e.message}`);
  } finally {
    btn.textContent = isSignup ? 'Create Account →' : 'Sign In →';
    btn.disabled = false;
  }
}

function showLoginError(msg) {
  const e = document.getElementById('login-error');
  if (e) { e.textContent = '⚠ ' + msg; e.style.display = 'block'; }
}

function applyLoggedInState() {
  const user = getUser();
  if (!document.getElementById('nav-user-badge')) {
    const navLinks = document.querySelector('.nav-links');
    const badge = document.createElement('div');
    badge.id = 'nav-user-badge';
    badge.style.cssText = `
      display:flex;align-items:center;gap:8px;
      padding:0.35rem 0.9rem;
      background:var(--accent-glow);
      border:1px solid var(--border2);
      border-radius:20px;
      font-size:0.75rem;font-weight:500;color:var(--accent2);
    `;
    badge.innerHTML = `
      🧑‍💼 <span style="color:var(--text2);">${user.name || user.username || 'User'}</span>
      <button onclick="logout()" style="
        margin-left:8px;
        background:rgba(248,113,113,0.12);
        border:1px solid rgba(248,113,113,0.25);
        color:var(--danger);
        border-radius:8px;
        padding:0.35rem 0.7rem;
        cursor:pointer;
        font-size:0.72rem;
        font-weight:600;
        transition:all 0.2s;
      "
      onmouseover="this.style.transform='translateY(-1px)'"
      onmouseout="this.style.transform='translateY(0)'">Logout</button>
    `;
    navLinks.insertBefore(badge, navLinks.lastElementChild);
  }
}

function logout() {
  clearToken();
  document.getElementById('nav-user-badge')?.remove();
  showLoginModal();
}

/* ══════════════════════════════════════
   THEME
══════════════════════════════════════ */
function toggleTheme() {
  const h = document.documentElement;
  h.setAttribute('data-theme', h.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
}

/* ══════════════════════════════════════
   PAGE ROUTING
══════════════════════════════════════ */
function showPage(name) {
  if (!getToken()) { showLoginModal(); return; }
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById('page-' + name).classList.add('active');
  document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
  const nl = document.getElementById('nav-' + name);
  if (nl) nl.classList.add('active');
  window.scrollTo(0, 0);
  if (name === 'history') loadHistory();
}

/* ══════════════════════════════════════
   API HEALTH CHECK
══════════════════════════════════════ */
async function checkAPI() {
  try {
    const r = await fetch(BASE_URL + '/docs', { method: 'GET', signal: AbortSignal.timeout(3000) });
    if (r.ok) {
      document.getElementById('api-status-box').className = '';
      document.getElementById('api-status-text').textContent = '';
      document.getElementById('api-badge').style.color = 'var(--success)';
    } else throw new Error();
  } catch {
    document.getElementById('api-badge').innerHTML = '<div style="width:6px;height:6px;border-radius:50%;background:var(--danger);flex-shrink:0"></div> API Offline';
    document.getElementById('api-badge').style.color = 'var(--danger)';
  }
}
checkAPI();
setInterval(checkAPI, 10000);

/* ══════════════════════════════════════
   LOADING STEPS
══════════════════════════════════════ */
const STEPS = [
  'Validating claim fields',
  'Running feature pipeline',
  'Generating prediction',
  'Computing reasons',
  'Looking for policies',
  'Generating recommendations',
];

function showLoading() {
  const panel = document.getElementById('results-panel');
  panel.innerHTML = `
    <div class="loading-state result-card">
      <div class="spinner"></div>
      <div style="color:var(--text2);font-size:0.9rem;font-weight:500;">Running AI pipeline…</div>
      <div class="loading-steps">
        ${STEPS.map((s, i) => `<div class="loading-step" id="lstep-${i}"><div class="step-dot"></div>${s}</div>`).join('')}
      </div>
    </div>`;
  let i = 0;
  const iv = setInterval(() => {
    if (i > 0) document.getElementById(`lstep-${i - 1}`)?.classList.replace('active', 'done');
    if (i < STEPS.length) { document.getElementById(`lstep-${i}`)?.classList.add('active'); i++; }
    else clearInterval(iv);
  }, 400);
  return iv;
}

/* ══════════════════════════════════════
   SUBMIT CLAIM
══════════════════════════════════════ */
async function submitClaim() {
  if (!getToken()) { showLoginModal(); return; }

  const claimId       = document.getElementById('claim_id').value.trim();
  const patientId     = document.getElementById('patient_id').value.trim();
  const providerId    = document.getElementById('provider_id').value;
  const diagnosisCode = document.getElementById('diagnosis_code').value;
  const procedureCode = document.getElementById('procedure_code').value;
  const billed        = parseFloat(document.getElementById('billed_amount').value);
  const serviceDate   = document.getElementById('date_of_service').value;

  if (!claimId)                     { alert('Claim ID is missing.'); return; }
  if (!patientId)                   { alert('Patient ID is missing.'); return; }
  if (isNaN(billed) || billed <= 0) { alert('Valid Billed Amount is required.'); return; }
  if (!serviceDate)                 { alert('Date of Service is missing.'); return; }

  const payload = {
    claim_id: claimId, provider_id: providerId,
    diagnosis_code: diagnosisCode, procedure_code: procedureCode,
    billed_amount: billed, date: serviceDate,
  };

  const btn = document.getElementById('submit-btn');
  btn.disabled = true;
  document.getElementById('btn-text').textContent = 'Analysing…';
  const iv = showLoading();

  try {
    const resp = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + getToken(),
      },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(60000),
    });
    clearInterval(iv);

    if (resp.status === 401) { clearToken(); showLoginModal(); showError('Session expired. Please log in again.'); return; }
    if (resp.status === 403) { showError('Access denied. You do not have the billing analyst role.'); return; }
    if (!resp.ok) { const err = await resp.text(); showError(`API error ${resp.status}: ${err}`); return; }

    const data = await resp.json();
    showResults(data);

  } catch(e) {
    clearInterval(iv);
    showError(e.name === 'TimeoutError' ? 'Request timed out (60s).' : `Cannot connect to API: ${e.message}`);
  } finally {
    btn.disabled = false;
    document.getElementById('btn-text').textContent = '⚡ Analyse Claim';
  }
}

function showError(msg) {
  document.getElementById('results-panel').innerHTML =
    `<div class="error-card result-card">⚠ ${msg}</div>`;
}

/* ══════════════════════════════════════
   RENDER RESULTS
══════════════════════════════════════ */
function showResults(data) {
  const risk  = (data.risk_level || 'LOW').toUpperCase();
  const pred  = data.prediction || '';
  const score = parseFloat(data.risk_score || 0).toFixed(1);
  const isApproved = risk === 'LOW';
  const isDenied   = pred.toUpperCase().includes('DENIED');

  const scoreColor = score >= 70 ? 'var(--danger)' : score >= 40 ? 'var(--warn)' : 'var(--success)';
  const riskClass  = risk === 'HIGH' ? 'risk-high' : risk === 'MEDIUM' ? 'risk-medium' : 'risk-low';
  const verdictClass = isDenied ? 'denied' : 'approved';
  const verdictColor = isDenied ? 'var(--danger)' : 'var(--success)';

  const pct    = Math.min(parseFloat(score), 100) / 100;
  const circum = Math.PI * 52;
  const dash   = pct * circum;
  const gaugeStroke = score >= 70 ? '#f87171' : score >= 40 ? '#fbbf24' : '#34d399';

  let html = `
  <div class="verdict-row">
    <div class="result-card ${verdictClass}">
      <div class="rc-label">Verdict</div>
      <div class="verdict-text" style="color:${verdictColor}">${pred}</div>
      <div class="risk-badge-pill ${riskClass}">${risk}</div>
    </div>
    <div class="result-card score-card">
      <div class="rc-label" style="text-align:center">Risk Score</div>
      <div class="gauge-wrap">
        <svg width="140" height="80" viewBox="0 0 140 80">
          <path d="M 18 70 A 52 52 0 0 1 122 70" fill="none" stroke="var(--border)" stroke-width="10" stroke-linecap="round"/>
          <path d="M 18 70 A 52 52 0 0 1 122 70" fill="none" stroke="${gaugeStroke}" stroke-width="10" stroke-linecap="round"
            stroke-dasharray="${dash} ${circum}" style="transition:stroke-dasharray 1s ease"/>
        </svg>
        <div class="gauge-value" style="color:${scoreColor}">${score}<span>%</span></div>
        <div class="gauge-sublabel">Denial Risk</div>
      </div>
    </div>
  </div>`;

  if (isApproved) {
    html += `
    <div class="approved-card">
      <div class="check-anim">✓</div>
      <div class="approved-title">Claim Approved</div>
      <div class="approved-sub">Low denial risk.</div>
    </div>`;
  } else {
    const reasons = data.top_reasons || [];
    if (reasons.length) {
      html += `<div class="result-card reasons-card"><div class="rc-label">Denial Reasons</div>`;
      reasons.forEach((r, i) => {
        html += `<div class="reason-item">
          <div class="reason-num">${i + 1}</div>
          <div class="reason-text">${r.business_reason || r.feature || '—'}</div>
        </div>`;
      });
      html += `</div>`;
    }

    let ps = data.policy_summary || '';
    if (Array.isArray(ps)) ps = ps.join('\n');
    if (ps && !ps.includes('\n')) ps = ps.replace(/\s+(\d+\.)/g, '\n$1').trim();
    if (ps) {
      html += `<div class="result-card policy-card"><div class="rc-label">Policy — Rules & Regulations</div>`;
      ps.split('\n').filter(l => l.trim()).forEach(l => {
        html += `<div class="policy-line">${l.trim()}</div>`;
      });
      html += `</div>`;
    }

    const recs = data.recommendations || [];
    const next = data.next_action || '';
    if (recs.length) {
      html += `<div class="result-card"><div class="rc-label">Recommendations</div>`;
      recs.forEach(r => {
        html += `<div class="rec-item">
          <div class="rec-for">For: ${(r.reason || '').slice(0, 60)}${r.reason?.length > 60 ? '...' : ''}</div>
          <div class="rec-action">${r.action || ''}</div>
        </div>`;
      });
      html += `</div>`;
    }
    if (next) {
      html += `<div class="next-action-card result-card">
        <div class="next-action-label">⚡ Immediate Next Action</div>
        <div class="next-action-text">${next}</div>
      </div>`;
    }
  }

  document.getElementById('results-panel').innerHTML = html;
}

/* ══════════════════════════════════════
   HISTORY
══════════════════════════════════════ */
let allHistory   = [];
let activeFilter = 'all';

async function loadHistory() {
  if (!getToken()) { showLoginModal(); return; }

  document.getElementById('history-container').innerHTML = `
    <div style="text-align:center;padding:4rem 2rem;color:var(--text3);font-size:0.88rem;">
      <div class="spinner" style="margin:0 auto 1rem;"></div>
      Loading claim history from S3…
    </div>`;

  try {
    const resp = await fetch(BASE_URL + '/history', {
      headers: { 'Authorization': 'Bearer ' + getToken() },
      signal: AbortSignal.timeout(15000),
    });
    if (resp.status === 401) { clearToken(); showLoginModal(); return; }
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);

    allHistory = await resp.json();
    renderHistory();

  } catch(e) {
    document.getElementById('history-container').innerHTML =
      `<div class="error-card">⚠ Failed to load history: ${e.message}</div>`;
  }
}

function setFilter(f) {
  activeFilter = f;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('filter-' + f).classList.add('active');
  renderHistory();
}

function renderHistory() {
  let records = allHistory;

  if (activeFilter === 'denied') {
    records = records.filter(r => (r.result?.prediction || '').toUpperCase().includes('DENIED'));
  } else if (activeFilter === 'approved') {
    records = records.filter(r => (r.result?.risk_level || '').toUpperCase() === 'LOW');
  }

  document.getElementById('history-count').textContent =
    `${records.length} record${records.length !== 1 ? 's' : ''}`;

  if (!records.length) {
    document.getElementById('history-container').innerHTML = `
      <div style="text-align:center;padding:4rem 2rem;
                  background:var(--surface);border:1px dashed var(--border2);border-radius:14px;">
        <div style="font-size:2.5rem;margin-bottom:1rem;">📭</div>
        <div style="color:var(--text3);font-size:0.88rem;">No claims found for this filter.</div>
      </div>`;
    return;
  }

  let html = `
  <div style="background:var(--surface);border:1px solid var(--border);border-radius:14px;overflow:hidden;">
    <table class="history-table">
      <thead>
        <tr>
          <th>Claim ID</th><th>Date</th><th>Provider</th>
          <th>Verdict</th><th>Risk Score</th><th>Run By</th><th></th>
        </tr>
      </thead>
      <tbody>`;

  records.forEach((r, i) => {
    const result  = r.result  || {};
    const payload = r.payload || {};
    const pred    = result.prediction || '—';
    const risk    = (result.risk_level || 'LOW').toUpperCase();
    const score   = parseFloat(result.risk_score || 0).toFixed(1);
    const ts      = r.timestamp ? r.timestamp.replace('T', ' ').slice(0, 16) + ' UTC' : '—';
    const isDenied      = pred.toUpperCase().includes('DENIED');
    const verdictColor  = isDenied ? 'var(--danger)' : 'var(--success)';
    const riskClass     = risk === 'HIGH' ? 'risk-high' : risk === 'MEDIUM' ? 'risk-medium' : 'risk-low';
    const scoreColor    = score >= 70 ? 'var(--danger)' : score >= 40 ? 'var(--warn)' : 'var(--success)';

    html += `
    <tr class="history-row" onclick="toggleExpand(${i})">
      <td><span style="font-family:'Syne',sans-serif;font-weight:700;color:var(--text);">${r.claim_id || '—'}</span></td>
      <td>${ts}</td>
      <td>${payload.provider_id || '—'}</td>
      <td><span style="font-weight:600;color:${verdictColor};">${pred}</span></td>
      <td>
        <span style="font-weight:700;color:${scoreColor};">${score}%</span>
        <span class="risk-badge-pill ${riskClass}" style="margin-left:6px;font-size:0.65rem;">${risk}</span>
      </td>
      <td style="color:var(--text3);">${r.user || '—'}</td>
      <td style="text-align:right;padding-right:1.2rem;">
        <span id="chevron-${i}" style="color:var(--text3);font-size:0.8rem;transition:transform 0.2s;display:inline-block;">▶</span>
      </td>
    </tr>
    <tr class="expand-row">
      <td colspan="7">
        <div class="expand-content" id="expand-${i}">${renderExpandDetail(r)}</div>
      </td>
    </tr>`;
  });

  html += `</tbody></table></div>`;
  document.getElementById('history-container').innerHTML = html;
}

function toggleExpand(i) {
  const content = document.getElementById('expand-' + i);
  const chevron = document.getElementById('chevron-' + i);
  const isOpen  = content.classList.contains('open');

  document.querySelectorAll('.expand-content').forEach(c => c.classList.remove('open'));
  document.querySelectorAll('[id^="chevron-"]').forEach(c => { c.style.transform = 'rotate(0deg)'; });

  if (!isOpen) {
    content.classList.add('open');
    chevron.style.transform = 'rotate(90deg)';
  }
}

function renderExpandDetail(r) {
  const result  = r.result  || {};
  const payload = r.payload || {};
  const score   = parseFloat(result.risk_score || 0).toFixed(1);
  const scoreColor = score >= 70 ? 'var(--danger)' : score >= 40 ? 'var(--warn)' : 'var(--success)';

  let html = `<div class="detail-grid">
    <div class="detail-card">
      <div class="detail-label">Billed Amount</div>
      <div class="detail-value">$${(payload.billed_amount || 0).toLocaleString()}</div>
    </div>
    <div class="detail-card">
      <div class="detail-label">Diagnosis Code</div>
      <div class="detail-value">${payload.diagnosis_code || '—'}</div>
    </div>
    <div class="detail-card">
      <div class="detail-label">Procedure Code</div>
      <div class="detail-value">${payload.procedure_code || '—'}</div>
    </div>
    <div class="detail-card">
      <div class="detail-label">Risk Score</div>
      <div class="detail-value" style="color:${scoreColor}">${score}%</div>
    </div>
  </div>`;

  const reasons = result.top_reasons || [];
  if (reasons.length) {
    html += `<div style="background:var(--surface);border:1px solid var(--border);
                         border-radius:10px;padding:1rem 1.2rem;">
      <div class="detail-label" style="margin-bottom:0.6rem;">Denial Reasons</div>
      <div class="reasons-list">`;
    reasons.forEach((r2, i) => {
      html += `<div class="reason-chip">
        <span style="min-width:20px;height:20px;background:var(--accent-glow);
                     border:1px solid var(--border2);border-radius:5px;
                     display:flex;align-items:center;justify-content:center;
                     font-size:0.7rem;font-weight:700;color:var(--accent);">${i + 1}</span>
        ${r2.business_reason || r2.feature || '—'}
      </div>`;
    });
    html += `</div></div>`;
  }

  const next = result.next_action || '';
  if (next) {
    html += `<div style="margin-top:1rem;background:rgba(251,191,36,0.05);
                         border:1px solid rgba(251,191,36,0.2);border-radius:8px;
                         padding:0.9rem 1.1rem;">
      <div class="detail-label" style="color:var(--warn);margin-bottom:0.3rem;">⚡ Next Action</div>
      <div style="font-size:0.85rem;color:var(--text2);">${next}</div>
    </div>`;
  }

  return html;
}
