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
let currentAllocations = {};
let savedStrategyParams = {};
let fabIntersectionObserver = null;

function initScrollReveal() {
  const reveals = document.querySelectorAll('.reveal');
  if (!reveals.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed');
        observer.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  });

  reveals.forEach(el => observer.observe(el));
}

// DOM
const backtestBtn = document.getElementById('backtestBtn');
const strategySelect = document.getElementById('strategySelect');
const strategyParams = document.getElementById('strategyParams');
const statusEl = document.getElementById('status');
const singleResults = document.getElementById('singleResults');
const comparisonResults = document.getElementById('comparisonResults');
const emptyState = document.getElementById('emptyState');
const optimizeBtn = document.getElementById('optimizeBtn');
const frontierBtn = document.getElementById('frontierBtn');

document.addEventListener('DOMContentLoaded', init);
document.addEventListener('DOMContentLoaded', initScrollReveal);
window.addEventListener('beforeunload', cleanupMobileFab);

async function init() {
    await loadStrategies();
    setupEventListeners();
    setupDateRange();
    setupPresets();
    setupAdvancedToggle();
    setupTabs();
    setupSymbolInput();
    setupHelp();
    setupTooltips();
    setupStrategyPicker();
    setupOnboarding();
    setupMobileFab();
    restoreResults();
    const fromURL = loadFromURL();
    autoLoadData();
}

// ============================================================================
// EVENT LISTENERS
// ============================================================================

function setupEventListeners() {
    backtestBtn.addEventListener('click', runBacktest);
    document.getElementById('compareSelectedBtn').addEventListener('click', runCompareSelected);
    strategySelect.addEventListener('change', onStrategyChange);
    optimizeBtn.addEventListener('click', runOptimization);
    frontierBtn.addEventListener('click', runFrontier);

    document.getElementById('monteCarloBtn').addEventListener('click', runMonteCarlo);
    document.getElementById('saveConfigBtn').addEventListener('click', saveConfig);
    document.getElementById('loadConfigBtn').addEventListener('click', loadConfig);
    document.getElementById('deleteConfigBtn').addEventListener('click', deleteConfig);
    loadSavedConfigs();

    document.getElementById('exportCsvBtn').addEventListener('click', exportCSV);
    document.getElementById('exportTradesBtn').addEventListener('click', exportTrades);
    document.getElementById('exportPdfBtn').addEventListener('click', exportPDF);
    document.getElementById('benchmarkToggle').addEventListener('change', toggleBenchmark);

    document.addEventListener('keydown', handleKeyboard);
}

// ============================================================================
// KEYBOARD SHORTCUTS
// ============================================================================

function handleKeyboard(e) {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') return;

    const ctrl = e.ctrlKey || e.metaKey;

    if (e.key === 'Escape') {
        const modal = document.getElementById('helpModal');
        if (modal && !modal.classList.contains('hidden')) { modal.classList.add('hidden'); return; }
        const onb = document.getElementById('onboardingOverlay');
        if (onb && !onb.classList.contains('hidden')) { onboardingClose(); return; }
        hideTooltip();
        return;
    }

    if (ctrl && e.key === 'Enter') { e.preventDefault(); runBacktest(); return; }
    if (ctrl && e.key === 'd') { e.preventDefault(); toggleDarkMode(); return; }
    if (ctrl && e.key === 's') { e.preventDefault(); saveConfig(); return; }
    if (!ctrl && e.key === '?') {
        const modal = document.getElementById('helpModal');
        if (modal) modal.classList.toggle('hidden');
        return;
    }
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
// HELP MODAL
// ============================================================================

function setupHelp() {
    const modal = document.getElementById('helpModal');
    const closeBtn = document.getElementById('helpCloseBtn');

    function openHelp() { modal.classList.remove('hidden'); }

    document.querySelectorAll('[data-section="help"]').forEach(el => {
        el.addEventListener('click', (e) => { e.preventDefault(); openHelp(); });
    });

    closeBtn.addEventListener('click', () => modal.classList.add('hidden'));
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.classList.add('hidden');
    });
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
            modal.classList.add('hidden');
        }
    });
}

// ============================================================================
// TOOLTIPS
// ============================================================================

const TOOLTIP_DEFS = {
    totalReturn: { title: 'Total Return', desc: 'The overall percentage gain or loss from your initial investment over the entire period.' },
    annualReturn: { title: 'Annual Return', desc: 'The average yearly return, adjusted for compounding. Useful for comparing investments of different lengths.' },
    maxDrawdown: { title: 'Max Drawdown', desc: 'The largest peak-to-trust decline during the period. Lower is better — it shows the worst-case loss you would have experienced.' },
    sharpeRatio: { title: 'Sharpe Ratio', desc: 'Risk-adjusted return. Higher is better — it means you earned more return per unit of risk taken. Above 1 is good, above 2 is excellent.' },
    expectedReturn: { title: 'Expected Return', desc: 'The estimated annual return based on historical averages and the optimal allocation found by the optimizer.' },
    volatility: { title: 'Volatility', desc: 'How much the portfolio value fluctuates. Higher volatility means bigger swings — both up and down.' }
};

let activeTooltip = null;

function setupTooltips() {
    // Use pointer: coarse to detect touch-primary devices (excludes hybrid touchscreen laptops with mouse)
    // Note: 'ontouchstart' in window || navigator.maxTouchPoints > 0 would match hybrid devices
    // (Surface Pro, MacBook Touch Bar), disabling hover tooltips even when using a mouse.
    const isTouch = window.matchMedia('(pointer: coarse)').matches;

    if (isTouch) {
        // Tap-to-toggle on touch devices
        document.addEventListener('click', (e) => {
            const trigger = e.target.closest('.tooltip-trigger');
            if (trigger) {
                e.preventDefault();
                e.stopPropagation();
                const key = trigger.dataset.tooltip;
                const def = TOOLTIP_DEFS[key];
                if (!def) return;
                if (activeTooltip && activeTooltip.parentElement === trigger) {
                    hideTooltip();
                } else {
                    showTooltip(trigger, def);
                }
                return;
            }
            // Tap outside dismisses
            if (activeTooltip && !e.target.closest('.tooltip')) {
                hideTooltip();
            }
        });
    } else {
        // Hover on desktop
        document.addEventListener('mouseover', (e) => {
            const trigger = e.target.closest('.tooltip-trigger');
            if (!trigger) return;
            const key = trigger.dataset.tooltip;
            const def = TOOLTIP_DEFS[key];
            if (!def) return;
            showTooltip(trigger, def);
        });
        document.addEventListener('mouseout', (e) => {
            const trigger = e.target.closest('.tooltip-trigger');
            if (!trigger) return;
            hideTooltip();
        });
    }
}

// ============================================================================
// ONBOARDING
// ============================================================================

const ONBOARDING_STEPS = [
    { title: 'Welcome to PortfolioLab', desc: 'This tool lets you backtest investment strategies using real Yahoo Finance data. Let\'s walk through the key areas.' },
    { title: '1. Load Assets', desc: 'Enter a ticker symbol (e.g. AAPL, MSFT, SPY) and click Load Data. You can add up to 5 assets to compare.' },
    { title: '2. Configure Strategy', desc: 'Choose a strategy from the dropdown and adjust parameters. Adjust allocation weights in the pie chart or by number.' },
    { title: '3. Run & Compare', desc: 'Click Run Backtest to see results. Use Compare Strategies in the Advanced section to test multiple strategies side-by-side.' }
];
let onboardingIdx = 0;

function setupOnboarding() {
    const overlay = document.getElementById('onboardingOverlay');
    if (!overlay) return;
    if (localStorage.getItem('portfoliolab_onboarded') === '1') return;
    const nextBtn = document.getElementById('onboardingNext');
    const skipBtn = document.getElementById('onboardingSkip');
    nextBtn.addEventListener('click', onboardingNext);
    skipBtn.addEventListener('click', onboardingClose);
    showOnboardingStep();
    overlay.classList.remove('hidden');
}

function showOnboardingStep() {
    const s = ONBOARDING_STEPS[onboardingIdx];
    document.getElementById('onboardingStep').textContent = 'Step ' + (onboardingIdx + 1) + ' of ' + ONBOARDING_STEPS.length;
    document.getElementById('onboardingTitle').textContent = s.title;
    document.getElementById('onboardingDesc').textContent = s.desc;
    document.getElementById('onboardingNext').textContent = onboardingIdx === ONBOARDING_STEPS.length - 1 ? 'Get Started' : 'Next';
    const dots = document.getElementById('onboardingDots');
    dots.innerHTML = ONBOARDING_STEPS.map((_, i) =>
        '<div class="onboarding__dot' + (i === onboardingIdx ? ' active' : '') + '"></div>'
    ).join('');
}

function onboardingNext() {
    if (onboardingIdx < ONBOARDING_STEPS.length - 1) {
        onboardingIdx++;
        showOnboardingStep();
    } else {
        onboardingClose();
    }
}

function onboardingClose() {
    document.getElementById('onboardingOverlay').classList.add('hidden');
    localStorage.setItem('portfoliolab_onboarded', '1');
}

// ============================================================================
// MOBILE FAB
// ============================================================================

function setupMobileFab() {
    const fab = document.getElementById('mobileFab');
    if (!fab) return;

    fab.addEventListener('click', () => runBacktest());

    // Show/hide based on scroll position
    fabIntersectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                fab.classList.add('hidden');
                fab.classList.remove('fab--visible');
            } else {
                fab.classList.remove('hidden');
                fab.classList.add('fab--visible');
            }
        });
    }, { threshold: 0 });

    // Observe the desktop backtest button
    const backtestBtn = document.getElementById('backtestBtn');
    if (backtestBtn) fabIntersectionObserver.observe(backtestBtn);
}

function cleanupMobileFab() {
    if (fabIntersectionObserver) {
        fabIntersectionObserver.disconnect();
        fabIntersectionObserver = null;
    }
}

function showTooltip(trigger, def) {
    hideTooltip();
    const tip = document.createElement('div');
    tip.className = 'tooltip';
    tip.innerHTML = '<div class="tooltip__title">' + def.title + '</div><div class="tooltip__desc">' + def.desc + '</div>';
    trigger.appendChild(tip);
    activeTooltip = tip;
}

function hideTooltip() {
    if (activeTooltip) { activeTooltip.remove(); activeTooltip = null; }
}

// ============================================================================
// MONTE CARLO SIMULATION
// ============================================================================

function runMonteCarlo() {
    try {
        abortPrevious();
        const { symbols, numDays, initialCapital } = getParams();
        if (!symbols.length) { showMsg('Load symbols first', 'warning'); return; }
        if (!dataLoaded) { showMsg('Wait for data to load', 'error'); return; }

        const sims = parseInt(document.querySelector('input[name="mcSims"]:checked').value);
        showMsg('Running ' + sims.toLocaleString() + ' simulations...', 'loading');
        setBtnLoading(document.getElementById('monteCarloBtn'), true);

        fetchAbort('/api/monte-carlo', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbols, num_simulations: sims, num_days: numDays, initial_value: initialCapital, weights: currentAllocations })
        }).then(r => r.json()).then(d => {
            if (d.success) { displayMonteCarlo(d); showMsg('Simulation completed', 'success'); }
            else showMsg('Error: ' + d.error, 'error');
        }).catch(e => { if (e.name !== 'AbortError') showMsg('Error: ' + e.message, 'error'); })
          .finally(() => setBtnLoading(document.getElementById('monteCarloBtn'), false));
    } catch (e) { if (e.name !== 'AbortError') showMsg('Error: ' + e.message, 'error'); }
}

function displayMonteCarlo(d) {
    const el = document.getElementById('monteCarloResults');
    if (!el) return;

    const stats = d.statistics;
    const fmt = v => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(v);
    const pct = v => (v * 100).toFixed(1) + '%';

    let html = '<div class="results__header"><h2 class="results__title"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="3"/><circle cx="8" cy="8" r="1" fill="currentColor"/><circle cx="16" cy="8" r="1" fill="currentColor"/><circle cx="12" cy="12" r="1" fill="currentColor"/><circle cx="8" cy="16" r="1" fill="currentColor"/><circle cx="16" cy="16" r="1" fill="currentColor"/></svg> Monte Carlo Simulation</h2></div>';
    html += '<div class="metric-row">';
    html += '<div class="metric-card metric-card--compact"><div class="metric-card__title">Median Final Value</div><div class="metric-card__value">' + fmt(stats.median) + '</div></div>';
    html += '<div class="metric-card metric-card--compact"><div class="metric-card__title">Mean Final Value</div><div class="metric-card__value">' + fmt(stats.mean) + '</div></div>';
    html += '<div class="metric-card metric-card--compact"><div class="metric-card__title">5th Percentile</div><div class="metric-card__value">' + fmt(stats.percentiles['5th']) + '</div></div>';
    html += '<div class="metric-card metric-card--compact"><div class="metric-card__title">95th Percentile</div><div class="metric-card__value">' + fmt(stats.percentiles['95th']) + '</div></div>';
    html += '<div class="metric-card metric-card--compact"><div class="metric-card__title">Probability of Loss</div><div class="metric-card__value">' + pct(stats.probability_of_loss) + '</div></div>';
    html += '</div>';
    html += '<div class="chart-container"><canvas id="mcChart"></canvas></div>';
    el.innerHTML = html;
    el.classList.remove('hidden');

    // Draw fan chart from percentile data
    const days = d.simulations[0].values;
    const xLabels = days.map((_, i) => i);
    const median = days.map((_, i) => d.simulations.reduce((sum, s) => sum + s.values[i], 0) / d.simulations.length);
    const p5 = days.map((_, i) => {
        const vals = d.simulations.map(s => s.values[i]).sort((a, b) => a - b);
        return vals[Math.floor(vals.length * 0.05)];
    });
    const p95 = days.map((_, i) => {
        const vals = d.simulations.map(s => s.values[i]).sort((a, b) => a - b);
        return vals[Math.floor(vals.length * 0.95)];
    });

    new Chart(document.getElementById('mcChart'), {
        type: 'line',
        data: {
            labels: xLabels,
            datasets: [
                { label: '95th Percentile', data: p95, borderColor: 'rgba(76,175,80,0.4)', backgroundColor: 'rgba(76,175,80,0.08)', fill: '+1', pointRadius: 0 },
                { label: 'Median', data: median, borderColor: '#4caf50', borderWidth: 2, pointRadius: 0 },
                { label: '5th Percentile', data: p5, borderColor: 'rgba(244,67,54,0.4)', backgroundColor: 'rgba(244,67,54,0.08)', fill: '-1', pointRadius: 0 }
            ]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { position: 'top', labels: { usePointStyle: true, padding: 16 } } },
            scales: {
                x: { display: false },
                y: { ticks: { callback: v => '$' + (v / 1000).toFixed(0) + 'k' } }
            }
        }
    });
}

function setBtnLoading(btn, on) {
    btn.classList.toggle('btn--loading', on);
    btn.disabled = on;
}

const MAX_COMPARE = 6;
let selectedStrategies = new Set();

function setupStrategyPicker() {
    const picker = document.getElementById('strategyPicker');
    if (!picker || !strategies.length) return;
    let html = '<p class="strategy-picker__max">Select up to ' + MAX_COMPARE + ' strategies</p>';
    strategies.forEach(s => {
        html += '<label class="strategy-picker__item">' +
            '<input type="checkbox" value="' + s.id + '" data-name="' + s.name + '">' +
            '<span class="strategy-picker__name">' + s.name + '</span></label>';
    });
    picker.innerHTML = html;
    picker.querySelectorAll('input[type="checkbox"]').forEach(cb => {
        cb.addEventListener('change', onStrategyPickerChange);
    });
}

function onStrategyPickerChange() {
    const picker = document.getElementById('strategyPicker');
    const cbs = picker.querySelectorAll('input[type="checkbox"]');
    const btn = document.getElementById('compareSelectedBtn');
    selectedStrategies.clear();
    cbs.forEach(cb => {
        if (cb.checked) selectedStrategies.add(cb.value);
    });
    btn.textContent = 'Compare Selected (' + selectedStrategies.size + ')';
    btn.disabled = selectedStrategies.size < 2;
}

function runCompareSelected() {
    if (selectedStrategies.size < 2) return;
    try {
        abortPrevious();
        const { symbols, numDays, initialCapital } = getParams();
        if (!symbols.length) { showMsg('Load symbols first', 'warning'); return; }
        if (!dataLoaded) { showMsg('Wait for data to load', 'error'); return; }

        const { symbols: syms } = getParams();
        const ew = (1 / syms.length).toFixed(2);
        const ao = {}; syms.forEach(s => { ao[s] = parseFloat(ew); });
        const aj = JSON.stringify(ao);

        const strats = [];
        selectedStrategies.forEach(id => {
            const s = strategies.find(x => x.id === id);
            if (!s) return;
            const params = {};
            s.params.forEach(p => {
                if (p.name === 'allocation_json') params.allocation_json = aj;
                else if (p.name === 'symbol') params.symbol = syms[0] || '';
                else params[p.name] = p.value;
            });
            strats.push({ strategy_id: id, name: s.name, params });
        });

        showMsg('Comparing ' + strats.length + ' strategies...', 'loading');
        setBtnLoading(document.getElementById('compareSelectedBtn'), true);

        fetchAbort('/api/compare', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ use_real_data: true, symbols, strategies: strats, initial_capital: initialCapital, num_days: numDays })
        }).then(r => r.json()).then(d => {
            if (d.success) { displayComparison(d); saveResults(); showMsg('Comparison completed', 'success'); }
            else showMsg('Error: ' + d.error, 'error');
        }).catch(e => { if (e.name !== 'AbortError') showMsg('Error: ' + e.message, 'error'); })
          .finally(() => setBtnLoading(document.getElementById('compareSelectedBtn'), false));
    } catch (e) { if (e.name !== 'AbortError') showMsg('Error: ' + e.message, 'error'); }
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
            let v = savedStrategyParams[p.name] || p.value;
            if (p.name === 'symbol') {
                if (selectedSymbols.length) v = selectedSymbols[0].symbol;
                else if (currentSymbols.length) v = currentSymbols[0];
            }
            html += '<div class="field-group"><label class="field-label" for="param-' + p.name + '">' + p.label + '</label>' +
                    '<input type="' + p.type + '" name="' + p.name + '" value="' + v + '" class="text-input param-input" id="param-' + p.name + '"></div>';
        }
    }
    strategyParams.innerHTML = html;
    document.querySelectorAll('.param-input').forEach(input => {
        input.addEventListener('change', () => {
            savedStrategyParams[input.name] = input.value;
        });
    });
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
    const existingAlloc = { ...currentAllocations };
    const existingTotal = Object.values(existingAlloc).reduce((sum, v) => sum + v, 0);
    const hasExisting = Object.keys(existingAlloc).length > 0 && Math.abs(existingTotal - 100) < 1;
    let html = '';
    syms.forEach((ticker) => {
        let pct;
        if (hasExisting && existingAlloc[ticker] !== undefined) {
            pct = Math.round(existingAlloc[ticker] * 100);
        } else if (hasExisting) {
            pct = 0;
        } else {
            pct = Math.floor(100 / n);
        }
        html += '<div class="alloc-row"><span class="alloc-sym">' + ticker + '</span>' +
                '<input type="range" class="alloc-slider" min="0" max="100" value="' + pct + '" data-symbol="' + ticker + '">' +
                '<span class="alloc-val">' + pct + '%</span></div>';
    });
    document.getElementById('allocSliders').innerHTML = html;
    document.querySelectorAll('.alloc-slider').forEach(sl => sl.addEventListener('input', updateAlloc));
    if (!hasExisting) {
        const base = Math.floor(100 / n), rem = 100 % n;
        syms.forEach((ticker, i) => {
            currentAllocations[ticker] = (base + (i < rem ? 1 : 0)) / 100;
        });
    }
    updateAlloc();
}

function updateAlloc() {
    let total = 0, obj = {};
    document.querySelectorAll('.alloc-slider').forEach(sl => {
        const v = parseInt(sl.value), s = sl.dataset.symbol;
        obj[s] = v / 100; total += v;
        sl.closest('.alloc-row').querySelector('.alloc-val').textContent = v + '%';
    });
    currentAllocations = obj;
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
        buildCustomSelect('strategyCustomSelect', 'strategySelectTrigger', 'strategySelectDropdown', strategySelect);
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
        if (backtestBtn) setBtnLoading(backtestBtn, true);

        const r = await fetchAbort('/api/backtest', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ use_real_data: true, symbols, strategy_id: strategySelect.value, strategy_params: params, initial_capital: initialCapital, num_days: numDays })
        });
        const d = await r.json();
        if (d.success) { currentResult = d.result; displaySingle(d.result); saveResults(); showMsg('Backtest completed', 'success'); }
        else showMsg('Error: ' + d.error, 'error');
    } catch (e) { if (e.name !== 'AbortError') showMsg('Error: ' + e.message, 'error'); }
    finally { if (backtestBtn) setBtnLoading(backtestBtn, false); }
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

    const exportTradesBtn = document.getElementById('exportTradesBtn');
    if (r.trades?.length) {
        exportTradesBtn.classList.remove('hidden');
        displayTradeLog(r.trades);
    } else {
        exportTradesBtn.classList.add('hidden');
        document.getElementById('tradeLogSection').classList.add('hidden');
    }

    singleResults.classList.remove('hidden');
    syncToURL();
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
// EXPORT
// ============================================================================

function exportCSV() {
    if (!currentResult) return;
    const r = currentResult;
    const lines = [];
    lines.push('Portfolio Backtest Results');
    lines.push('Strategy,' + csvEscape(r.strategy_name));
    lines.push('Start Date,' + r.start_date);
    lines.push('End Date,' + r.end_date);
    lines.push('Initial Capital,' + r.initial_capital);
    lines.push('Final Value,' + r.final_value);
    lines.push('Total Return %,' + r.total_return);
    lines.push('Annual Return %,' + r.annual_return);
    lines.push('Max Drawdown %,' + r.max_drawdown);
    lines.push('Sharpe Ratio,' + r.sharpe_ratio);
    lines.push('');
    lines.push('Date,Value,Return %');
    r.snapshots.forEach(s => {
        lines.push(s.date + ',' + s.value + ',' + s.returns);
    });
    downloadCSV(lines.join('\n'), 'backtest-' + r.strategy_name.replace(/[^a-z0-9]/gi, '_') + '.csv');
}

function exportTrades() {
    if (!currentResult?.trades?.length) return;
    const r = currentResult;
    const lines = ['Date,Action,Symbol,Quantity,Price,Value'];
    r.trades.forEach(t => {
        lines.push(t.date + ',' + t.action + ',' + t.symbol + ',' + t.quantity + ',' + t.price + ',' + t.value);
    });
    downloadCSV(lines.join('\n'), 'trades-' + r.strategy_name.replace(/[^a-z0-9]/gi, '_') + '.csv');
}

function displayTradeLog(trades) {
    const section = document.getElementById('tradeLogSection');
    const tbody = document.getElementById('tradeLogBody');
    const count = document.getElementById('tradeCount');
    if (!trades?.length) {
        section.classList.add('hidden');
        return;
    }
    tbody.innerHTML = '';
    trades.forEach(t => {
        const row = tbody.insertRow();
        const actionClass = t.action === 'BUY' ? 'trade-buy' : 'trade-sell';
        row.innerHTML = '<td>' + t.date + '</td><td class="' + actionClass + '">' + t.action + '</td><td>' + t.symbol + '</td><td>' + fmt(t.quantity) + '</td><td>$' + fmt(t.price) + '</td><td>$' + fmt(t.value) + '</td>';
    });
    count.textContent = trades.length + ' trade' + (trades.length !== 1 ? 's' : '');
    section.classList.remove('hidden');
}

function csvEscape(val) {
    const s = String(val);
    if (s.includes(',') || s.includes('"') || s.includes('\n')) {
        return '"' + s.replace(/"/g, '""') + '"';
    }
    return s;
}

function downloadCSV(content, filename) {
    const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

// ============================================================================
// PDF EXPORT
// ============================================================================

function exportPDF() {
    const resultsEl = document.getElementById('singleResults');
    if (!resultsEl || resultsEl.classList.contains('hidden')) { showMsg('Run a backtest first', 'warning'); return; }

    showMsg('Generating PDF...', 'loading');
    setBtnLoading(document.getElementById('exportPdfBtn'), true);

    html2canvas(resultsEl, { scale: 2, useCORS: true, backgroundColor: '#ffffff' }).then(canvas => {
        const { jsPDF } = window.jspdf;
        const pdf = new jsPDF('p', 'mm', 'a4');
        const pageW = pdf.internal.pageSize.getWidth();
        const margin = 15;
        const contentW = pageW - margin * 2;
        const imgH = (canvas.height * contentW) / canvas.width;

        const imgData = canvas.toDataURL('image/png');
        pdf.addImage(imgData, 'PNG', margin, margin, contentW, imgH);
        pdf.save('portfoliolab-backtest.pdf');
        showMsg('PDF exported', 'success');
    }).catch(e => showMsg('PDF error: ' + e.message, 'error'))
      .finally(() => setBtnLoading(document.getElementById('exportPdfBtn'), false));
}

// ============================================================================
// BENCHMARK
// ============================================================================

function toggleBenchmark() {
    if (!currentResult?.snapshots?.length) return;
    drawEquity(currentResult.snapshots);
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
    const showBenchmark = document.getElementById('benchmarkToggle').checked;
    const datasets = [{
        label: 'Portfolio', data: vals, borderColor: c.primary, backgroundColor: c.primaryA,
        borderWidth: 2, tension: 0.3, fill: true, pointRadius: 0, pointHoverRadius: 5
    }];

    if (showBenchmark && currentResult?.benchmark?.snapshots?.length) {
        const benchDates = currentResult.benchmark.snapshots.map(s => s.date);
        const benchVals = currentResult.benchmark.snapshots.map(s => s.value);
        const benchData = dates.map(d => {
            const idx = benchDates.indexOf(d);
            return idx >= 0 ? benchVals[idx] : null;
        });
        const benchColor = c.primary === '#d0bcff' ? '#f2b8b5' : '#b3261e';
        datasets.push({
            label: 'S&P 500', data: benchData, borderColor: benchColor, borderWidth: 2,
            borderDash: [6, 3], tension: 0.3, fill: false, pointRadius: 0, pointHoverRadius: 4
        });
    }

    equityChart = new Chart(ctx, {
        type: 'line',
        data: { labels: dates, datasets: datasets },
        options: { ...chartOpts(c, dates, v => '$' + fmt(v)), plugins: { ...chartOpts(c, dates, v => '$' + fmt(v)).plugins, legend: { display: showBenchmark && currentResult?.benchmark, position: 'top', labels: { usePointStyle: true, pointStyle: 'line', padding: 12, color: c.text, font: { size: 11 } } } } }
    });

    const benchRow = document.getElementById('benchmarkRow');
    const benchStats = document.getElementById('benchmarkStats');
    if (currentResult?.benchmark) {
        benchRow.style.display = '';
        benchStats.textContent = 'SPY Return: ' + currentResult.benchmark.total_return + '%';
    } else {
        benchRow.style.display = 'none';
    }
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
        '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>';
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
    delete currentAllocations[ticker];
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
        savedStrategyParams['symbol'] = selectedSymbols[0].symbol;
    }
}

// ============================================================================
// URL STATE SYNC
// ============================================================================

function syncToURL() {
    const { symbols } = getParams();
    const strategy = strategySelect.value;
    if (!symbols.length || !strategy) return;

    const params = new URLSearchParams();
    params.set('symbols', symbols.join(','));
    params.set('strategy', strategy);

    // Add strategy-specific params
    const stratParams = {};
    const rows = strategyParams.querySelectorAll('.param-row');
    rows.forEach(row => {
        const input = row.querySelector('input, select');
        if (input && input.name) stratParams[input.name] = input.value;
    });
    if (Object.keys(stratParams).length) params.set('params', JSON.stringify(stratParams));

    const url = window.location.pathname + '?' + params.toString();
    window.history.replaceState({}, '', url);
}

function loadFromURL() {
    const params = new URLSearchParams(window.location.search);
    if (!params.has('symbols')) return false;

    const symbols = params.get('symbols').split(',').filter(s => s.trim());
    if (symbols.length) {
        const input = document.getElementById('symbolInput');
        symbols.forEach(s => addSymbol(s.trim()));
    }

    if (params.has('strategy')) {
        strategySelect.value = params.get('strategy');
        strategySelect.dispatchEvent(new Event('change'));
    }

    if (params.has('params')) {
        try {
            const stratParams = JSON.parse(params.get('params'));
            Object.entries(stratParams).forEach(([name, value]) => {
                const input = strategyParams.querySelector('[name="' + name + '"]');
                if (input) input.value = value;
            });
        } catch (e) {}
    }

    return true;
}

// ============================================================================
// DARK MODE
// ============================================================================

function toggleDarkMode() {
    const html = document.documentElement;
    const dark = html.classList.toggle('dark');
    localStorage.setItem('portfoliolab_theme', dark ? 'dark' : 'light');
    const toggle = document.getElementById('darkModeToggle');
    if (toggle) {
        const sun = toggle.querySelector('.icon-sun');
        const moon = toggle.querySelector('.icon-moon');
        if (sun) sun.style.display = dark ? 'none' : 'block';
        if (moon) moon.style.display = dark ? 'block' : 'none';
    }
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

// Dark mode toggle
function initDarkMode() {
  const toggle = document.getElementById('darkModeToggle');
  const toggleMobile = document.getElementById('darkModeToggleMobile');
  const html = document.documentElement;
  const iconSun = toggle?.querySelector('.icon-sun');
  const iconMoon = toggle?.querySelector('.icon-moon');

  // Check for saved preference or system preference
  const savedTheme = localStorage.getItem('portfoliolab_theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

  if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
    html.classList.add('dark');
    updateIcons(true);
  }

  function toggleDark() {
    html.classList.toggle('dark');
    const isDark = html.classList.contains('dark');
    localStorage.setItem('portfoliolab_theme', isDark ? 'dark' : 'light');
    updateIcons(isDark);
  }

  function updateIcons(isDark) {
    if (iconSun) iconSun.style.display = isDark ? 'none' : 'block';
    if (iconMoon) iconMoon.style.display = isDark ? 'block' : 'none';
  }

  toggle?.addEventListener('click', toggleDark);
  toggleMobile?.addEventListener('click', toggleDark);
}

document.addEventListener('DOMContentLoaded', initDarkMode);

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
            currentAllocations = {};
            savedStrategyParams = {};
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
        timestamp: new Date().toISOString(),
        allocations: { ...currentAllocations },
        strategyParams: { ...savedStrategyParams }
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
    buildCustomSelect('configCustomSelect', 'configSelectTrigger', 'configSelectDropdown', sel);
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
    if (cfg.allocations) currentAllocations = { ...cfg.allocations };
    if (cfg.strategyParams) savedStrategyParams = { ...cfg.strategyParams };
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

// Mobile nav toggle
const navHamburger = document.getElementById('navHamburger');
const navOverlay = document.getElementById('navOverlay');

if (navHamburger && navOverlay) {
  navHamburger.addEventListener('click', () => {
    navHamburger.classList.toggle('active');
    navOverlay.classList.toggle('hidden');
    document.body.style.overflow = navOverlay.classList.contains('hidden') ? '' : 'hidden';
  });

  navOverlay.querySelectorAll('.nav-overlay__link').forEach(link => {
    link.addEventListener('click', () => {
      navHamburger.classList.remove('active');
      navOverlay.classList.add('hidden');
      document.body.style.overflow = '';
    });
  });
}



// Magnetic button hover effects
function initMagneticButtons() {
  const buttons = document.querySelectorAll('.btn--primary, .btn--lg');

  buttons.forEach(btn => {
    btn.addEventListener('mouseenter', (e) => {
      const rect = btn.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;

      btn.style.transform = `translate(${x * 0.15}px, ${y * 0.15}px)`;
    });

    btn.addEventListener('mousemove', (e) => {
      const rect = btn.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;

      btn.style.transform = `translate(${x * 0.15}px, ${y * 0.15}px)`;
    });

    btn.addEventListener('mouseleave', () => {
      btn.style.transform = 'translate(0, 0)';
    });
  });
}

// Initialize magnetic buttons
document.addEventListener('DOMContentLoaded', initMagneticButtons);

// ============================================================================
// CUSTOM SELECT
// ============================================================================

function buildCustomSelect(containerId, triggerId, dropdownId, nativeSelect) {
    const container = document.getElementById(containerId);
    const trigger = document.getElementById(triggerId);
    const dropdown = document.getElementById(dropdownId);
    if (!container || !trigger || !dropdown || !nativeSelect) return;

    dropdown.innerHTML = '';
    const options = nativeSelect.querySelectorAll('option');

    options.forEach(opt => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'custom-select__option';
        btn.textContent = opt.textContent;
        btn.dataset.value = opt.value;

        if (opt.value === nativeSelect.value) {
            btn.classList.add('custom-select__option--selected');
            trigger.textContent = opt.textContent;
            if (!opt.value) trigger.classList.add('custom-select__trigger--placeholder');
        }

        if (!opt.value) btn.classList.add('custom-select__option--placeholder');

        btn.addEventListener('click', () => {
            nativeSelect.value = opt.value;
            trigger.textContent = opt.textContent;
            trigger.classList.toggle('custom-select__trigger--placeholder', !opt.value);
            dropdown.querySelectorAll('.custom-select__option').forEach(o => o.classList.remove('custom-select__option--selected'));
            btn.classList.add('custom-select__option--selected');
            container.classList.remove('custom-select--open');
            nativeSelect.dispatchEvent(new Event('change'));
        });

        dropdown.appendChild(btn);
    });

    trigger.addEventListener('click', (e) => {
        e.stopPropagation();
        document.querySelectorAll('.custom-select--open').forEach(el => {
            if (el !== container) el.classList.remove('custom-select--open');
        });
        container.classList.toggle('custom-select--open');
    });
}

document.addEventListener('click', () => {
    document.querySelectorAll('.custom-select--open').forEach(el => el.classList.remove('custom-select--open'));
});
