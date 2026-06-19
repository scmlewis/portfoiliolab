/**
 * PortfolioLab - Frontend JavaScript
 */

let currentResult = null;
let equityChart = null;
let comparisonChart = null;
let frontierChart = null;
let strategies = [];
let currentSymbols = [];
let activeAbortControllers = [];
let dataLoaded = false;

// DOM
const backtestBtn = document.getElementById('backtestBtn');
const quickCompareBtn = document.getElementById('quickCompareBtn');
const strategySelect = document.getElementById('strategySelect');
const strategyParams = document.getElementById('strategyParams');
const statusEl = document.getElementById('status');
const singleResults = document.getElementById('singleResults');
const comparisonResults = document.getElementById('comparisonResults');
const emptyState = document.getElementById('emptyState');
const optimizeBtn = document.getElementById('optimizeBtn');
const frontierBtn = document.getElementById('frontierBtn');

document.addEventListener('DOMContentLoaded', init);

async function init() {
    await loadStrategies();
    setupEventListeners();
    setupDateRange();
    setupPresets();
    setupAdvancedToggle();
    setupTabs();
    setupSymbolInput();
    setupHelp();
    restoreDarkMode();
    restoreResults();
    autoLoadData();
}

// ============================================================================
// EVENT LISTENERS
// ============================================================================

function setupEventListeners() {
    backtestBtn.addEventListener('click', runBacktest);
    quickCompareBtn.addEventListener('click', runQuickCompare);
    strategySelect.addEventListener('change', onStrategyChange);
    optimizeBtn.addEventListener('click', runOptimization);
    frontierBtn.addEventListener('click', runFrontier);

    document.getElementById('darkModeToggle').addEventListener('click', toggleDarkMode);

    document.getElementById('saveConfigBtn').addEventListener('click', saveConfig);
    document.getElementById('loadConfigBtn').addEventListener('click', loadConfig);
    document.getElementById('deleteConfigBtn').addEventListener('click', deleteConfig);
    loadSavedConfigs();
}

// ============================================================================
// UTILITIES
// ============================================================================

function debounce(fn, ms) {
    let t;
    return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
}

function abortPrevious() {
    activeAbortControllers.forEach(c => c.abort());
    activeAbortControllers = [];
}

function fetchAbort(url, opts = {}) {
    const c = new AbortController();
    activeAbortControllers.push(c);
    return fetch(url, { ...opts, signal: c.signal });
}

function fmt(n) { return Math.round(n).toLocaleString(); }

// ============================================================================
// AUTO-LOAD DATA
// ============================================================================

function autoLoadData() {
    setDataStatus('loading', 'Loading data...');
    loadRealData();

    const debounced = debounce(() => { dataLoaded = false; setDataStatus('loading', 'Loading data...'); loadRealData(); }, 800);
    document.getElementById('startDate').addEventListener('change', debounced);
    document.getElementById('endDate').addEventListener('change', debounced);
}

function setDataStatus(state, msg) {
    const el = document.getElementById('dataStatus');
    const txt = document.getElementById('dataStatusText');
    const icon = el.querySelector('.data-status__icon');
    el.className = 'data-status data-status--' + state;
    txt.textContent = msg;
    if (icon) icon.textContent = state === 'loaded' ? 'check_circle' : state === 'error' ? 'error' : 'cloud_queue';
}

async function loadRealData() {
    try {
        const { symbols, numDays } = getParams();
        if (!symbols.length) { setDataStatus('error', 'Enter at least one symbol'); return; }

        const res = await fetchAbort('/api/load-real-data', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbols, num_days: numDays })
        });
        const d = await res.json();

        if (d.success) {
            currentSymbols = d.assets;
            dataLoaded = true;
            let msg = 'Loaded ' + d.assets.length + ' asset' + (d.assets.length !== 1 ? 's' : '');
            if (d.missing_symbols?.length) msg += ' (' + d.missing_symbols.join(', ') + ' not found)';
            setDataStatus('loaded', msg);
        } else {
            setDataStatus('error', d.error || 'Failed to load');
        }
    } catch (e) {
        if (e.name !== 'AbortError') setDataStatus('error', e.message);
    }
}

// ============================================================================
// HELP TAB
// ============================================================================

function setupHelp() {
    document.getElementById('helpBtn').addEventListener('click', () => switchTab('help'));
}

// ============================================================================
// ADVANCED TOGGLE
// ============================================================================

function setupAdvancedToggle() {
    const section = document.getElementById('advancedSection');
    const toggle = document.getElementById('advancedToggle');
    const body = document.getElementById('advancedBody');

    toggle.addEventListener('click', () => {
        const collapsed = section.classList.contains('section--collapsed');
        if (collapsed) {
            section.classList.remove('section--collapsed');
            section.classList.add('section--expanded');
            body.classList.remove('hidden');
        } else {
            section.classList.add('section--collapsed');
            section.classList.remove('section--expanded');
            body.classList.add('hidden');
        }
    });
}

// ============================================================================
// TABS
// ============================================================================

function setupTabs() {
    document.querySelectorAll('.tab').forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });
}

function switchTab(name) {
    document.querySelectorAll('.tab-panel').forEach(p => { p.classList.add('hidden'); p.classList.remove('active'); });
    document.querySelectorAll('.tab').forEach(b => b.classList.remove('active'));
    const panel = document.getElementById(name + '-tab');
    if (panel) { panel.classList.remove('hidden'); panel.classList.add('active'); }
    const btn = document.querySelector('[data-tab="' + name + '"]');
    if (btn) btn.classList.add('active');
}

// ============================================================================
// STRATEGY
// ============================================================================

function onStrategyChange() {
    const id = strategySelect.value;
    const s = strategies.find(x => x.id === id);
    if (!s) { strategyParams.innerHTML = ''; return; }

    const isAlloc = id === 'balanced' || id === 'rebalance';
    let html = '';
    for (const p of s.params) {
        if (p.name === 'allocation_json' && isAlloc) {
            html += renderAllocationBuilder(p);
        } else {
            let v = p.value;
            if (p.name === 'symbol') {
                if (selectedSymbols.length) v = selectedSymbols[0].symbol;
                else if (currentSymbols.length) v = currentSymbols[0];
            }
            html += '<div class="field-group"><label class="field-label" for="param-' + p.name + '">' + p.label + '</label>' +
                    '<input type="' + p.type + '" name="' + p.name + '" value="' + v + '" class="text-input param-input" id="param-' + p.name + '"></div>';
        }
    }
    strategyParams.innerHTML = html;
    if (isAlloc) setupAllocation(selectedSymbols.length ? selectedSymbols : currentSymbols);
}

function renderAllocationBuilder(p) {
    return '<div class="alloc-builder">' +
        '<label class="field-label">Asset Allocation (%)</label>' +
        '<div id="allocSliders"></div>' +
        '<div class="alloc-summary"><span>Total:</span> <strong id="allocTotal">0%</strong></div>' +
        '<input type="hidden" name="allocation_json" id="allocJSON" value=\'' + p.value + '\'>';
}

function setupAllocation(symbolsOverride) {
    const raw = symbolsOverride || currentSymbols;
    if (!raw?.length) {
        const el = document.getElementById('allocSliders');
        if (el) el.innerHTML = '<p style="color:var(--error);font-size:0.8125rem">Load data first</p>';
        return;
    }
    const syms = raw.map(s => typeof s === 'string' ? s : s.symbol);
    const n = syms.length;
    const base = Math.floor(100 / n), rem = 100 % n;
    let html = '';
    syms.forEach((ticker, i) => {
        const pct = base + (i < rem ? 1 : 0);
        html += '<div class="alloc-row"><span class="alloc-sym">' + ticker + '</span>' +
                '<input type="range" class="alloc-slider" min="0" max="100" value="' + pct + '" data-symbol="' + ticker + '">' +
                '<span class="alloc-val">' + pct + '%</span></div>';
    });
    document.getElementById('allocSliders').innerHTML = html;
    document.querySelectorAll('.alloc-slider').forEach(sl => sl.addEventListener('input', updateAlloc));
    updateAlloc();
}

function updateAlloc() {
    let total = 0, obj = {};
    document.querySelectorAll('.alloc-slider').forEach(sl => {
        const v = parseInt(sl.value), s = sl.dataset.symbol;
        obj[s] = v / 100; total += v;
        sl.closest('.alloc-row').querySelector('.alloc-val').textContent = v + '%';
    });
    const t = document.getElementById('allocTotal');
    if (t) { t.textContent = total + '%'; t.className = total === 100 ? 'valid' : 'invalid'; }
    const j = document.getElementById('allocJSON');
    if (j) j.value = JSON.stringify(obj);
}

// ============================================================================
// API CALLS
// ============================================================================

async function loadStrategies() {
    try {
        const r = await fetch('/api/strategies');
        strategies = await r.json();
        strategySelect.innerHTML = '<option value="">Choose a strategy...</option>';
        strategies.forEach(s => { strategySelect.innerHTML += '<option value="' + s.id + '">' + s.name + '</option>'; });
    } catch (e) { showMsg('Error loading strategies: ' + e, 'error'); }
}

function getParams() {
    const symbols = getSelectedSymbols();
    let numDays = 252;
    const s = document.getElementById('startDate'), e = document.getElementById('endDate');
    if (s?.value && e?.value) numDays = Math.max(10, Math.ceil((new Date(e.value) - new Date(s.value)) / 864e5));
    const cap = parseFloat(document.getElementById('initialCapital').value) || 100000;
    return { symbols, numDays, initialCapital: cap };
}

function showMsg(msg, type) {
    statusEl.textContent = msg;
    statusEl.className = 'status status--' + type;
    statusEl.classList.remove('hidden');
    if (type !== 'loading') setTimeout(() => statusEl.classList.add('hidden'), 5000);
}

function hideResults() {
    singleResults.classList.add('hidden');
    comparisonResults.classList.add('hidden');
    emptyState.classList.remove('hidden');
}

async function runBacktest() {
    try {
        abortPrevious();
        if (!strategySelect.value) { showMsg('Please select a strategy', 'error'); return; }
        if (!dataLoaded) { showMsg('Please wait for data to load', 'error'); return; }

        const params = {};
        document.querySelectorAll('.param-input').forEach(i => { params[i.name] = i.value; });
        const aj = document.getElementById('allocJSON');
        if (aj) params.allocation_json = aj.value;

        const { symbols, numDays, initialCapital } = getParams();
        showMsg('Running backtest...', 'loading');
        setBtnLoading(backtestBtn, true);

        const r = await fetchAbort('/api/backtest', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ use_real_data: true, symbols, strategy_id: strategySelect.value, strategy_params: params, initial_capital: initialCapital, num_days: numDays })
        });
        const d = await r.json();
        if (d.success) { currentResult = d.result; displaySingle(d.result); saveResults(); showMsg('Backtest completed', 'success'); }
        else showMsg('Error: ' + d.error, 'error');
    } catch (e) { if (e.name !== 'AbortError') showMsg('Error: ' + e.message, 'error'); }
    finally { setBtnLoading(backtestBtn, false); }
}

async function runQuickCompare() {
    try {
        abortPrevious();
        const { symbols, numDays, initialCapital } = getParams();
        if (!symbols.length) { showMsg('Load symbols first', 'warning'); return; }
        if (!dataLoaded) { showMsg('Wait for data to load', 'error'); return; }

        const ew = (1 / symbols.length).toFixed(2);
        const ao = {}; symbols.forEach(s => { ao[s] = parseFloat(ew); });
        const aj = JSON.stringify(ao);

        const strats = [
            { strategy_id: 'buy_hold_single', name: 'Buy & Hold (' + symbols[0] + ')', params: { symbol: symbols[0] } },
            { strategy_id: 'balanced', name: 'Balanced (' + symbols.slice(0, 2).join('/') + ')', params: { allocation_json: aj } },
            { strategy_id: 'momentum', name: 'Momentum', params: { short_window: '20', long_window: '50' } },
            { strategy_id: 'rebalance', name: 'Rebalancing (' + symbols.slice(0, 2).join('/') + ')', params: { allocation_json: aj, frequency: '63' } }
        ];

        showMsg('Comparing 4 strategies...', 'loading');
        setBtnLoading(quickCompareBtn, true);

        const r = await fetchAbort('/api/compare', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ use_real_data: true, symbols, strategies: strats, initial_capital: initialCapital, num_days: numDays })
        });
        const d = await r.json();
        if (d.success) { displayComparison(d); saveResults(); showMsg('Comparison completed', 'success'); }
        else showMsg('Error: ' + d.error, 'error');
    } catch (e) { if (e.name !== 'AbortError') showMsg('Error: ' + e.message, 'error'); }
    finally { setBtnLoading(quickCompareBtn, false); }
}

function setBtnLoading(btn, on) {
    btn.classList.toggle('btn--loading', on);
    btn.disabled = on;
}

// ============================================================================
// DISPLAY
// ============================================================================

function displaySingle(r) {
    hideResults();
    statusEl.classList.add('hidden');
    document.getElementById('strategyName').textContent = r.strategy_name;

    const tre = document.getElementById('totalReturn');
    tre.textContent = r.total_return + '%';
    tre.className = 'metric-card__value' + (r.total_return < 0 ? ' negative' : '');

    document.getElementById('annualReturn').textContent = r.annual_return + '%';
    document.getElementById('maxDD').textContent = r.max_drawdown + '%';
    document.getElementById('sharpeRatio').textContent = r.sharpe_ratio.toFixed(2);
    document.getElementById('initialVal').textContent = '$' + fmt(r.initial_capital);
    document.getElementById('finalVal').textContent = '$' + fmt(r.final_value);
    document.getElementById('period').textContent = r.start_date + ' to ' + r.end_date;

    drawEquity(r.snapshots);
    singleResults.classList.remove('hidden');
}

function displayComparison(d) {
    hideResults();
    drawComparison(d.results);
    document.getElementById('bestReturn').textContent = d.best_return;
    document.getElementById('bestSharpe').textContent = d.best_sharpe;
    document.getElementById('bestDD').textContent = d.best_dd;

    const tb = document.getElementById('comparisonBody');
    tb.innerHTML = '';
    d.results.forEach(r => {
        const row = tb.insertRow();
        row.innerHTML = '<td>' + r.name + '</td><td>$' + fmt(r.initial) + '</td><td>$' + fmt(r.final) + '</td>' +
            '<td class="' + (r.return >= 0 ? 'positive' : 'negative') + '">' + r.return + '%</td>' +
            '<td>' + r.annual + '%</td><td>' + r.max_dd + '%</td><td>' + r.sharpe.toFixed(2) + '</td>';
    });
    comparisonResults.classList.remove('hidden');
}

// ============================================================================
// CHARTS
// ============================================================================

function chartColors() {
    const dark = document.documentElement.classList.contains('dark');
    return {
        grid: dark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)',
        text: dark ? '#94a3b8' : '#64748b',
        primary: dark ? '#d0bcff' : '#6750a4',
        primaryA: dark ? 'rgba(208,188,255,0.08)' : 'rgba(103,80,164,0.08)',
        tooltip: dark ? '#1e1e2e' : '#ffffff',
        tooltipText: dark ? '#e0e0e0' : '#1c1b1f',
        tooltipBorder: dark ? '#444' : '#e0e0e0'
    };
}

function drawEquity(snapshots) {
    if (!snapshots?.length) return;
    const ctx = document.getElementById('equityChart').getContext('2d');
    if (equityChart) equityChart.destroy();
    const c = chartColors();
    const dates = snapshots.map(s => s.date), vals = snapshots.map(s => s.value);

    equityChart = new Chart(ctx, {
        type: 'line',
        data: { labels: dates, datasets: [{ data: vals, borderColor: c.primary, backgroundColor: c.primaryA, borderWidth: 2, tension: 0.3, fill: true, pointRadius: 0, pointHoverRadius: 5 }] },
        options: chartOpts(c, dates, v => '$' + fmt(v))
    });
}

function drawComparison(results) {
    const el = document.getElementById('comparisonChart');
    if (!el) return;
    const ctx = el.getContext('2d');
    if (comparisonChart) comparisonChart.destroy();
    if (!results?.length || !results[0]?.snapshots?.length) return;

    const c = chartColors();
    const dates = results[0].snapshots.map(s => s.date);
    const palette = c.primary === '#d0bcff'
        ? ['#d0bcff', '#f2b8b5', '#9dd676', '#efb8c8']
        : ['#6750a4', '#b3261e', '#386a20', '#984061'];

    const ds = results.filter(r => r?.snapshots?.length).map((r, i) => ({
        label: r.name, data: r.snapshots.map(s => s.value),
        borderColor: palette[i % palette.length], borderWidth: 2, tension: 0.3,
        fill: false, pointRadius: 0, pointHoverRadius: 5, spanGaps: true
    }));

    comparisonChart = new Chart(ctx, {
        type: 'line', data: { labels: dates, datasets: ds },
        options: { ...chartOpts(c, dates, v => '$' + fmt(v)), interaction: { mode: 'index', intersect: false },
            plugins: { legend: { display: true, position: 'top', labels: { usePointStyle: true, pointStyle: 'circle', padding: 12, color: c.text, font: { size: 11 } } },
                tooltip: { backgroundColor: c.tooltip, titleColor: c.tooltipText, bodyColor: c.tooltipText, borderColor: c.tooltipBorder, borderWidth: 1, cornerRadius: 8, padding: 10,
                    callbacks: { label: ctx => ctx.dataset.label + ': $' + fmt(ctx.parsed.y) } } } }
    });
}

function drawFrontier(data) {
    if (!data.frontier?.length) return;
    const ctx = document.getElementById('frontierChart').getContext('2d');
    if (frontierChart) frontierChart.destroy();
    const c = chartColors();
    const fp = data.frontier.map(p => ({ x: p.volatility * 100, y: p.return * 100 }));
    const ms = data.max_sharpe ? { x: (data.max_sharpe.volatility || 0) * 100, y: (data.max_sharpe.expected_return || 0) * 100 } : { x: 0, y: 0 };
    const mv = data.min_variance ? { x: (data.min_variance.volatility || 0) * 100, y: (data.min_variance.expected_return || 0) * 100 } : { x: 0, y: 0 };
    const green = c.primary === '#d0bcff' ? '#9dd676' : '#386a20';
    const red = c.primary === '#d0bcff' ? '#f2b8b5' : '#b3261e';

    frontierChart = new Chart(ctx, {
        type: 'scatter',
        data: { datasets: [
            { label: 'Efficient Frontier', data: fp, borderColor: c.primary, backgroundColor: c.primaryA, showLine: true, borderWidth: 2, fill: false, tension: 0.1, pointRadius: 2, pointHoverRadius: 5 },
            { label: 'Max Sharpe', data: [ms], backgroundColor: green, pointRadius: 8, pointHoverRadius: 10, pointStyle: 'star' },
            { label: 'Min Variance', data: [mv], backgroundColor: red, pointRadius: 8, pointHoverRadius: 10, pointStyle: 'triangle' }
        ] },
        options: {
            responsive: true, maintainAspectRatio: false, animation: { duration: 500 },
            plugins: { legend: { display: true, position: 'top', labels: { color: c.text, font: { size: 11 } } },
                tooltip: { backgroundColor: c.tooltip, titleColor: c.tooltipText, bodyColor: c.tooltipText, borderColor: c.tooltipBorder, borderWidth: 1, cornerRadius: 8,
                    callbacks: { label: ctx => 'Return: ' + ctx.parsed.y.toFixed(2) + '%, Risk: ' + ctx.parsed.x.toFixed(2) + '%' } } },
            scales: {
                x: { type: 'linear', title: { display: true, text: 'Volatility (%)', color: c.text }, grid: { color: c.grid }, ticks: { color: c.text } },
                y: { title: { display: true, text: 'Expected Return (%)', color: c.text }, grid: { color: c.grid }, ticks: { color: c.text } }
            }
        }
    });
}

function chartOpts(c, dates, fmtFn) {
    return {
        responsive: true, maintainAspectRatio: false, animation: { duration: 500 },
        plugins: { legend: { display: false },
            tooltip: { backgroundColor: c.tooltip, titleColor: c.tooltipText, bodyColor: c.tooltipText, borderColor: c.tooltipBorder, borderWidth: 1, cornerRadius: 8, padding: 10, displayColors: false,
                callbacks: { label: ctx => fmtFn(ctx.parsed.y) } } },
        scales: {
            y: { grid: { color: c.grid }, ticks: { color: c.text, callback: fmtFn } },
            x: { grid: { display: false }, ticks: { color: c.text, maxTicksLimit: 10, callback: i => { const d = dates[i]; return d ? new Date(d).toLocaleDateString('en-US', { month: 'short', year: '2-digit' }) : ''; } } }
        }
    };
}

// ============================================================================
// OPTIMIZATION
// ============================================================================

async function runOptimization() {
    if (currentSymbols.length < 2) { showMsg('Need at least 2 symbols', 'error'); return; }
    abortPrevious();
    const type = document.querySelector('input[name="optimizationType"]:checked').value;
    showMsg('Optimizing...', 'loading');
    switchTab('optimization');
    setBtnLoading(optimizeBtn, true);

    try {
        const r = await fetchAbort('/api/optimize-portfolio', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ symbols: currentSymbols, type }) });
        const d = await r.json();
        if (!d.success) { showMsg('Failed: ' + d.error, 'error'); return; }
        displayOpt(d);
        showMsg(d.message, 'success');
    } catch (e) { if (e.name !== 'AbortError') showMsg(e.message, 'error'); }
    finally { setBtnLoading(optimizeBtn, false); }
}

async function runFrontier() {
    if (currentSymbols.length < 2) { showMsg('Need at least 2 symbols', 'error'); return; }
    abortPrevious();
    showMsg('Calculating frontier...', 'loading');
    switchTab('optimization');
    setBtnLoading(frontierBtn, true);

    try {
        const r = await fetchAbort('/api/efficient-frontier', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ symbols: currentSymbols, num_points: 50 }) });
        const d = await r.json();
        if (!d.success) { showMsg('Error: ' + d.error, 'error'); return; }
        document.getElementById('optimizationResults').classList.add('hidden');
        document.getElementById('emptyStateOpt').classList.add('hidden');
        document.getElementById('frontierResults').classList.remove('hidden');
        document.getElementById('frontierMaxSharpe').textContent = d.max_sharpe.sharpe_ratio.toFixed(2);
        document.getElementById('frontierMinVar').textContent = (d.min_variance.volatility * 100).toFixed(2) + '%';
        document.getElementById('frontierPoints').textContent = d.frontier.length;
        drawFrontier(d);
        showMsg(d.message, 'success');
    } catch (e) { if (e.name !== 'AbortError') showMsg(e.message, 'error'); }
    finally { setBtnLoading(frontierBtn, false); }
}

function displayOpt(d) {
    document.getElementById('frontierResults').classList.add('hidden');
    document.getElementById('emptyStateOpt').classList.add('hidden');
    document.getElementById('optimizationResults').classList.remove('hidden');
    document.getElementById('optExpectedReturn').textContent = (d.expected_return * 100).toFixed(2) + '%';
    document.getElementById('optVolatility').textContent = (d.volatility * 100).toFixed(2) + '%';
    document.getElementById('optSharpeRatio').textContent = d.sharpe_ratio.toFixed(2);

    document.getElementById('weightsTable').innerHTML = Object.entries(d.weights).sort((a, b) => b[1] - a[1]).map(([s, w]) =>
        '<div class="weight-row"><span class="weight-symbol">' + s + '</span><div class="weight-bar-wrap"><div class="weight-bar"><div class="weight-fill" style="width:' + (w * 100) + '%"></div></div></div><span class="weight-val">' + (w * 100).toFixed(1) + '%</span></div>'
    ).join('');

    document.getElementById('assetStatsTable').innerHTML = Object.entries(d.asset_stats).map(([s, st]) =>
        '<div class="stat-row"><span class="stat-label">' + s + '</span><div class="stat-items"><div class="stat-item"><small>Return</small><strong>' + (st.return * 100).toFixed(2) + '%</strong></div><div class="stat-item"><small>Volatility</small><strong>' + (st.volatility * 100).toFixed(2) + '%</strong></div></div></div>'
    ).join('');

    if (d.correlation) {
        const syms = Object.keys(d.correlation);
        document.getElementById('correlationTable').innerHTML = '<table class="corr-table"><thead><tr><th></th>' + syms.map(s => '<th>' + s + '</th>').join('') + '</tr></thead><tbody>' +
            syms.map(s1 => '<tr><th>' + s1 + '</th>' + syms.map(s2 => { const v = d.correlation[s1][s2]; const cls = v > 0.5 ? 'corr-positive' : v < -0.5 ? 'corr-negative' : ''; return '<td class="' + cls + '">' + v.toFixed(2) + '</td>'; }).join('') + '</tr>').join('') +
            '</tbody></table>';
    }
}

// ============================================================================
// SYMBOL INPUT (Chip/Tag)
// ============================================================================

let selectedSymbols = [];
let popularSymbolsData = [];
let activeACIndex = -1;

const SYMBOL_CHIPS_EL = document.getElementById('symbolChips');
const SYMBOL_TEXT_EL = document.getElementById('symbolText');
const SYMBOLS_HIDDEN_EL = document.getElementById('symbols');
const AUTOCOMPLETE_EL = document.getElementById('symbolsAutocomplete');
const POPULAR_LIST_EL = document.getElementById('popularList');
const SYMBOL_INPUT_EL = document.getElementById('symbolInput');

function setupSymbolInput() {
    renderInitialChips();
    loadPopularSymbols();

    SYMBOL_TEXT_EL.addEventListener('input', onSymbolInput);
    SYMBOL_TEXT_EL.addEventListener('keydown', onSymbolKeydown);
    SYMBOL_TEXT_EL.addEventListener('focus', onSymbolInput);
    SYMBOL_TEXT_EL.addEventListener('blur', () => setTimeout(hideAutocomplete, 150));
    SYMBOL_INPUT_EL.addEventListener('click', () => SYMBOL_TEXT_EL.focus());

    if (SYMBOLS_HIDDEN_EL.value.trim()) {
        const initial = SYMBOLS_HIDDEN_EL.value.split(',').map(s => s.trim()).filter(Boolean);
        setSymbols(initial, false);
    }
}

function renderInitialChips() {
    SYMBOL_CHIPS_EL.innerHTML = '';
    selectedSymbols.forEach(s => renderChip(s));
    syncHiddenInput();
}

function renderChip(sym) {
    const chip = document.createElement('span');
    chip.className = 'symbol-chip';
    chip.dataset.symbol = sym.symbol;
    chip.innerHTML = '<span class="symbol-chip__ticker">' + sym.symbol + '</span>' +
        (sym.name ? '<span class="symbol-chip__name">' + sym.name + '</span>' : '') +
        '<button type="button" class="symbol-chip__remove" aria-label="Remove ' + sym.symbol + '">' +
        '<span class="material-symbols-rounded">close</span></button>';
    chip.querySelector('.symbol-chip__remove').addEventListener('click', (e) => {
        e.stopPropagation();
        removeSymbol(sym.symbol);
    });
    SYMBOL_CHIPS_EL.appendChild(chip);
}

function addSymbol(ticker, name) {
    ticker = ticker.toUpperCase().trim();
    if (!ticker || selectedSymbols.some(s => s.symbol === ticker)) return false;
    const sym = { symbol: ticker, name: name || '' };
    selectedSymbols.push(sym);
    renderChip(sym);
    syncHiddenInput();
    updatePopularVisibility();
    triggerDataReload();
    return true;
}

function removeSymbol(ticker) {
    selectedSymbols = selectedSymbols.filter(s => s.symbol !== ticker);
    const chip = SYMBOL_CHIPS_EL.querySelector('[data-symbol="' + ticker + '"]');
    if (chip) chip.remove();
    syncHiddenInput();
    updatePopularVisibility();
    triggerDataReload();
}

function setSymbols(tickers, reload) {
    selectedSymbols = [];
    SYMBOL_CHIPS_EL.innerHTML = '';
    tickers.forEach(t => {
        const ticker = t.toUpperCase().trim();
        if (ticker) {
            selectedSymbols.push({ symbol: ticker, name: '' });
            renderChip({ symbol: ticker, name: '' });
        }
    });
    syncHiddenInput();
    updatePopularVisibility();
    if (reload !== false) triggerDataReload();
}

function syncHiddenInput() {
    SYMBOLS_HIDDEN_EL.value = selectedSymbols.map(s => s.symbol).join(', ');
}

function getSelectedSymbols() {
    return selectedSymbols.map(s => s.symbol);
}

function hideAutocomplete() {
    AUTOCOMPLETE_EL.classList.add('hidden');
    AUTOCOMPLETE_EL.innerHTML = '';
    activeACIndex = -1;
}

async function fetchAutocomplete(q) {
    if (!q || q.length < 1) { hideAutocomplete(); return; }
    try {
        const r = await fetchAbort('/api/symbols-autocomplete?q=' + encodeURIComponent(q));
        const d = await r.json();
        activeACIndex = -1;

        if (!d.results?.length) { hideAutocomplete(); return; }

        let html = '';
        let lastCat = '';
        d.results.forEach(item => {
            if (item.category !== lastCat) {
                lastCat = item.category;
                html += '<li class="autocomplete__category">' + item.category + '</li>';
            }
            const alreadyAdded = selectedSymbols.some(s => s.symbol === item.symbol);
            html += '<li class="autocomplete__item' + (alreadyAdded ? ' autocomplete__item--added' : '') + '" data-symbol="' + item.symbol + '" data-name="' + item.name.replace(/"/g, '&quot;') + '">' +
                '<span class="autocomplete__symbol">' + item.symbol + '</span>' +
                '<span class="autocomplete__name">' + item.name + '</span>' +
                (alreadyAdded ? '<span class="autocomplete__added">Added</span>' : '') +
                '</li>';
        });

        AUTOCOMPLETE_EL.innerHTML = html;
        AUTOCOMPLETE_EL.classList.remove('hidden');

        AUTOCOMPLETE_EL.querySelectorAll('.autocomplete__item:not(.autocomplete__item--added)').forEach(item => {
            item.addEventListener('mousedown', (e) => {
                e.preventDefault();
                addSymbol(item.dataset.symbol, item.dataset.name);
                SYMBOL_TEXT_EL.value = '';
                hideAutocomplete();
                SYMBOL_TEXT_EL.focus();
            });
        });
    } catch (e) {
        if (e.name !== 'AbortError') hideAutocomplete();
    }
}

const debouncedAC = debounce(fetchAutocomplete, 250);

function onSymbolInput() {
    const q = SYMBOL_TEXT_EL.value.trim();
    if (q.length < 1) { hideAutocomplete(); return; }
    debouncedAC(q);
}

function onSymbolKeydown(e) {
    const items = AUTOCOMPLETE_EL.querySelectorAll('.autocomplete__item');

    if (e.key === 'ArrowDown') {
        e.preventDefault();
        activeACIndex = Math.min(activeACIndex + 1, items.length - 1);
        updateACHighlight(items);
    } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        activeACIndex = Math.max(activeACIndex - 1, -1);
        updateACHighlight(items);
    } else if (e.key === 'Enter') {
        e.preventDefault();
        if (activeACIndex >= 0 && items[activeACIndex]) {
            const sym = items[activeACIndex].dataset.symbol;
            const name = items[activeACIndex].dataset.name;
            addSymbol(sym, name);
            SYMBOL_TEXT_EL.value = '';
            hideAutocomplete();
        } else if (SYMBOL_TEXT_EL.value.trim()) {
            addSymbol(SYMBOL_TEXT_EL.value.trim());
            SYMBOL_TEXT_EL.value = '';
            hideAutocomplete();
        }
    } else if (e.key === 'Escape') {
        hideAutocomplete();
    } else if (e.key === 'Backspace' && !SYMBOL_TEXT_EL.value && selectedSymbols.length) {
        removeSymbol(selectedSymbols[selectedSymbols.length - 1].symbol);
    }
}

function updateACHighlight(items) {
    items.forEach((item, i) => {
        item.classList.toggle('autocomplete__item--active', i === activeACIndex);
    });
    if (activeACIndex >= 0 && items[activeACIndex]) {
        items[activeACIndex].scrollIntoView({ block: 'nearest' });
    }
}

// === Popular Symbols ===

async function loadPopularSymbols() {
    try {
        const r = await fetch('/api/popular-symbols');
        const d = await r.json();
        popularSymbolsData = d.symbols || [];
        renderPopularSymbols();
    } catch (e) {}
}

function renderPopularSymbols() {
    POPULAR_LIST_EL.innerHTML = '';
    popularSymbolsData.forEach(sym => {
        if (selectedSymbols.some(s => s.symbol === sym.symbol)) return;
        const chip = document.createElement('button');
        chip.type = 'button';
        chip.className = 'popular-chip';
        chip.dataset.symbol = sym.symbol;
        chip.textContent = sym.symbol;
        chip.title = sym.name;
        chip.addEventListener('click', () => {
            addSymbol(sym.symbol, sym.name);
            SYMBOL_TEXT_EL.focus();
        });
        POPULAR_LIST_EL.appendChild(chip);
    });
}

function updatePopularVisibility() {
    const container = document.getElementById('popularSymbols');
    if (!container) return;
    renderPopularSymbols();
    container.style.display = POPULAR_LIST_EL.children.length ? '' : 'none';
}

function triggerDataReload() {
    refreshStrategyParams();
    dataLoaded = false;
    setDataStatus('loading', 'Loading data...');
    debouncedDataReload();
}

const debouncedDataReload = debounce(() => loadRealData(), 600);

function refreshStrategyParams() {
    const id = strategySelect.value;
    if (!id) return;
    const s = strategies.find(x => x.id === id);
    if (!s) return;

    const isAlloc = id === 'balanced' || id === 'rebalance';
    if (isAlloc) {
        const allocEl = document.getElementById('allocSliders');
        if (allocEl) setupAllocation(selectedSymbols);
    }

    const symbolInput = document.getElementById('param-symbol');
    if (symbolInput && selectedSymbols.length) {
        symbolInput.value = selectedSymbols[0].symbol;
    }
}

// ============================================================================
// DARK MODE
// ============================================================================

function toggleDarkMode() {
    const dark = document.documentElement.classList.toggle('dark');
    localStorage.setItem('darkMode', dark);
    updateDarkIcon(dark);
    if (equityChart) drawEquity(currentResult?.snapshots || []);
    if (comparisonChart) {
        const ld = comparisonChart.data;
        if (ld) drawComparison(ld.datasets.map(ds => ({ name: ds.label, snapshots: ld.labels.map((date, i) => ({ date, value: ds.data[i] })) })));
    }
    if (frontierChart) {
        const ld = frontierChart.data;
        if (ld) {
            const fp = ld.datasets.find(d => d.label === 'Efficient Frontier');
            if (fp) drawFrontier({ frontier: fp.data.map(p => ({ volatility: p.x / 100, return: p.y / 100 })), max_sharpe: null, min_variance: null });
        }
    }
}

function restoreDarkMode() {
    const dark = localStorage.getItem('darkMode') === 'true';
    document.documentElement.classList.toggle('dark', dark);
    updateDarkIcon(dark);
}

function updateDarkIcon(dark) {
    document.getElementById('darkModeToggle').innerHTML = dark
        ? '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>'
        : '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>';
}

// ============================================================================
// DATE RANGE
// ============================================================================

function setupDateRange() {
    const now = new Date(), ago = new Date(now.getFullYear() - 1, now.getMonth(), now.getDate());
    document.getElementById('startDate').valueAsDate = ago;
    document.getElementById('endDate').valueAsDate = now;
}

// ============================================================================
// PRESETS
// ============================================================================

const PRESETS = {
    conservative: { name: 'Conservative (60/40)', symbols: ['VTI', 'AGG'], alloc: { VTI: 0.6, AGG: 0.4 } },
    balanced: { name: 'Balanced (50/50)', symbols: ['VTI', 'VXUS'], alloc: { VTI: 0.5, VXUS: 0.5 } },
    aggressive: { name: 'Aggressive (80/20)', symbols: ['QQQ', 'VTI'], alloc: { QQQ: 0.8, VTI: 0.2 } },
    growth: { name: 'Growth (100% Stocks)', symbols: ['VTI', 'VXUS'], alloc: { VTI: 0.6, VXUS: 0.4 } }
};

function setupPresets() {
    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const t = PRESETS[btn.dataset.preset];
            if (!t) return;
            setSymbols(t.symbols, true);
            strategySelect.value = 'balanced';
            strategySelect.dispatchEvent(new Event('change'));
            setTimeout(() => {
                Object.entries(t.alloc).forEach(([s, p]) => {
                    const sl = document.querySelector('[data-symbol="' + s + '"]');
                    if (sl) { sl.value = p * 100; sl.dispatchEvent(new Event('input')); }
                });
            }, 100);
            showMsg('Applied ' + t.name + ' preset', 'success');
        });
    });
}

// ============================================================================
// CONFIG SAVE/LOAD
// ============================================================================

function saveConfig() {
    const name = document.getElementById('configName').value.trim();
    if (!name) { showMsg('Enter a config name', 'warning'); return; }
    const cfg = {
        name, symbols: document.getElementById('symbols').value,
        startDate: document.getElementById('startDate').value, endDate: document.getElementById('endDate').value,
        initialCapital: document.getElementById('initialCapital').value, strategy: strategySelect.value,
        timestamp: new Date().toISOString()
    };
    const aj = document.getElementById('allocJSON');
    if (aj) cfg.allocation = aj.value;
    const params = {};
    document.querySelectorAll('.param-input').forEach(i => { params[i.name] = i.value; });
    cfg.params = params;
    const saved = JSON.parse(localStorage.getItem('backtesterConfigs') || '{}');
    saved[name] = cfg;
    localStorage.setItem('backtesterConfigs', JSON.stringify(saved));
    document.getElementById('configName').value = '';
    loadSavedConfigs();
    showMsg('Saved "' + name + '"', 'success');
}

function loadSavedConfigs() {
    const saved = JSON.parse(localStorage.getItem('backtesterConfigs') || '{}');
    const sel = document.getElementById('savedConfigs');
    sel.innerHTML = '<option value="">-- No saved configs --</option>';
    Object.keys(saved).forEach(n => { const o = document.createElement('option'); o.value = n; o.textContent = n; sel.appendChild(o); });
}

function loadConfig() {
    const name = document.getElementById('savedConfigs').value;
    if (!name) { showMsg('Select a config', 'warning'); return; }
    const cfg = JSON.parse(localStorage.getItem('backtesterConfigs') || '{}')[name];
    if (!cfg) { showMsg('Not found', 'error'); return; }
    const syms = cfg.symbols.split(',').map(s => s.trim()).filter(Boolean);
    setSymbols(syms, false);
    document.getElementById('startDate').value = cfg.startDate || '';
    document.getElementById('endDate').value = cfg.endDate || '';
    document.getElementById('initialCapital').value = cfg.initialCapital;
    strategySelect.value = cfg.strategy;
    strategySelect.dispatchEvent(new Event('change'));
    setTimeout(() => {
        if (cfg.allocation) { const aj = document.getElementById('allocJSON'); if (aj) { aj.value = cfg.allocation; updateAlloc(); } }
        if (cfg.params) Object.entries(cfg.params).forEach(([n, v]) => { const i = document.querySelector('[name="' + n + '"]'); if (i) i.value = v; });
    }, 100);
    showMsg('Loaded "' + name + '"', 'success');
}

function deleteConfig() {
    const name = document.getElementById('savedConfigs').value;
    if (!name) { showMsg('Select a config to delete', 'warning'); return; }
    if (!confirm('Delete "' + name + '"?')) return;
    const saved = JSON.parse(localStorage.getItem('backtesterConfigs') || '{}');
    delete saved[name];
    localStorage.setItem('backtesterConfigs', JSON.stringify(saved));
    loadSavedConfigs();
    showMsg('Deleted', 'success');
}

// ============================================================================
// RESULT PERSISTENCE
// ============================================================================

function saveResults() { try { if (currentResult) localStorage.setItem('lastBacktestResult', JSON.stringify(currentResult)); } catch (e) {} }
function restoreResults() {
    try {
        const s = localStorage.getItem('lastBacktestResult');
        if (s) { const r = JSON.parse(s); if (r?.snapshots) { currentResult = r; displaySingle(r); } }
    } catch (e) {}
}
