/**
 * Investment Backtester - Frontend JavaScript
 */

// Global state
let currentResult = null;
let equityChart = null;
let comparisonChart = null;
let frontierChart = null;
let strategies = [];
let currentSymbols = [];

// DOM Elements
const configForm = document.getElementById('configForm');
const loadRealDataBtn = document.getElementById('loadRealDataBtn');
const backtestBtn = document.getElementById('backtestBtn');
const quickCompareBtn = document.getElementById('quickCompareBtn');
const strategySelect = document.getElementById('strategySelect');
const strategyParams = document.getElementById('strategyParams');
const status = document.getElementById('status');
const singleResults = document.getElementById('singleResults');
const comparisonResults = document.getElementById('comparisonResults');
const emptyState = document.getElementById('emptyState');
const optimizeBtn = document.getElementById('optimizeBtn');
const frontierBtn = document.getElementById('frontierBtn');

// Initialize
document.addEventListener('DOMContentLoaded', init);

async function init() {
    console.log('Initializing app...');
    
    // Load strategies
    await loadStrategies();
    
    // Setup event listeners
    loadRealDataBtn.addEventListener('click', loadRealDataWithDates);
    backtestBtn.addEventListener('click', runBacktest);
    quickCompareBtn.addEventListener('click', runQuickCompare);
    strategySelect.addEventListener('change', onStrategyChange);
    optimizeBtn.addEventListener('click', runOptimization);
    frontierBtn.addEventListener('click', runFrontier);
    
    // Setup dark mode
    const darkModeBtn = document.getElementById('darkModeToggle');
    if (darkModeBtn) {
        darkModeBtn.addEventListener('click', toggleDarkMode);
        initializeDarkMode();
    }
    
    // Setup date range
    setupDateRange();
    
    // Setup preset templates
    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            applyPresetTemplate(e.target.dataset.preset);
        });
    });
    
    // Setup save/load config
    document.getElementById('saveConfigBtn').addEventListener('click', saveCurrentConfig);
    document.getElementById('loadConfigBtn').addEventListener('click', loadSelectedConfig);
    document.getElementById('deleteConfigBtn').addEventListener('click', deleteSelectedConfig);
    loadSavedConfigs();
    
    // Setup tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            switchTab(e.target.dataset.tab);
        });
    });
    
    // Setup symbol autocomplete
    const symbolsInput = document.getElementById('symbols');
    if (symbolsInput) {
        symbolsInput.addEventListener('input', handleSymbolsInput);
        symbolsInput.addEventListener('blur', () => {
            setTimeout(() => {
                document.getElementById('symbolsAutocomplete').classList.add('hidden');
            }, 200);
        });
        document.addEventListener('click', (e) => {
            if (e.target.id !== 'symbols') {
                document.getElementById('symbolsAutocomplete').classList.add('hidden');
            }
        });
    }
    
    // Setup collapsible sections
    setupCollapsible();
    restoreCollapsibleState();
    
    showMessage('Ready! Load data to begin.', 'success');
}

// ============================================================================
// UI FUNCTIONS
// ============================================================================

function onStrategyChange() {
    const strategyId = strategySelect.value;
    const strategy = strategies.find(s => s.id === strategyId);
    
    if (!strategy) {
        strategyParams.innerHTML = '';
        return;
    }
    
    // Check if this is a balanced or rebalancing strategy
    const isBalnacedOrRebalance = strategyId === 'balanced' || strategyId === 'rebalance';
    
    // Build parameter inputs
    let html = '';
    for (const param of strategy.params) {
        // For allocation_json, show allocation builder instead
        if (param.name === 'allocation_json' && isBalnacedOrRebalance) {
            html += renderAllocationBuilder(param);
        } else {
            // Use first loaded symbol as default if available, otherwise use param default
            let paramValue = param.value;
            if (param.name === 'symbol' && currentSymbols.length > 0) {
                paramValue = currentSymbols[0];
            }
            
            html += `
                <label>
                    <span>${param.label}</span>
                    <input type="${param.type}" 
                           name="${param.name}" 
                           value="${paramValue}"
                           class="param-input">
                </label>
            `;
        }
    }
    
    strategyParams.innerHTML = html;
    
    // Setup allocation builder if needed
    if (isBalnacedOrRebalance) {
        setupAllocationBuilder();
    }
}

function renderAllocationBuilder(param) {
    return `
        <div class="allocation-builder">
            <label><span>Asset Allocation (%)</span></label>
            <div id="allocationSliders"></div>
            <div class="allocation-summary">
                <div class="summary-row">
                    <span>Total:</span>
                    <strong id="allocationTotal">0%</strong>
                </div>
            </div>
            <input type="hidden" name="allocation_json" id="allocationJSON" value='${param.value}'>
        </div>
    `;
}

function setupAllocationBuilder() {
    if (!currentSymbols || !Array.isArray(currentSymbols) || !currentSymbols.length) {
        document.getElementById('allocationSliders').innerHTML = 
            '<p style="color: #dc2626; font-size: 0.9em;">⚠ Load data first to create allocations</p>';
        return;
    }
    
    const slidersContainer = document.getElementById('allocationSliders');
    const numSymbols = currentSymbols.length;
    const basePercentage = Math.floor(100 / numSymbols);
    const remainder = 100 % numSymbols;
    
    let html = '';
    let sliderIndex = 0;
    
    for (const symbol of currentSymbols) {
        // Distribute remainder across first few sliders to ensure total = 100%
        const percentage = basePercentage + (sliderIndex < remainder ? 1 : 0);
        html += `
            <div class="allocation-slider-item">
                <label>${symbol}</label>
                <div class="slider-container">
                    <input type="range" 
                           name="alloc_${symbol}" 
                           class="allocation-slider" 
                           min="0" max="100" 
                           value="${percentage}"
                           data-symbol="${symbol}">
                    <span class="allocation-value">${percentage}%</span>
                </div>
            </div>
        `;
        sliderIndex++;
    }
    
    slidersContainer.innerHTML = html;
    
    // Setup event listeners for sliders
    document.querySelectorAll('.allocation-slider').forEach(slider => {
        slider.addEventListener('input', updateAllocationDisplay);
    });
    
    updateAllocationDisplay();
}

function updateAllocationDisplay() {
    const sliders = document.querySelectorAll('.allocation-slider');
    let total = 0;
    let allocation = {};
    
    sliders.forEach(slider => {
        const value = parseInt(slider.value);
        const symbol = slider.dataset.symbol;
        allocation[symbol] = value / 100;
        total += value;
        
        // Update display
        slider.parentElement.querySelector('.allocation-value').textContent = value + '%';
    });
    
    // Update total
    const totalEl = document.getElementById('allocationTotal');
    if (totalEl) {
        totalEl.textContent = total + '%';
        totalEl.style.color = total === 100 ? '#16a34a' : '#dc2626';
    }
    
    // Update hidden JSON field
    const jsonField = document.getElementById('allocationJSON');
    if (jsonField) {
        jsonField.value = JSON.stringify(allocation);
    }
}

function showMessage(message, type = 'info') {
    status.textContent = message;
    status.className = `status ${type}`;
    status.classList.remove('hidden');
    
    if (type !== 'loading') {
        setTimeout(() => status.classList.add('hidden'), 5000);
    }
}

function showLoading(message = 'Loading...') {
    showMessage(message, 'loading');
}

function hideResults() {
    singleResults.classList.add('hidden');
    comparisonResults.classList.add('hidden');
    emptyState.classList.remove('hidden');
}

// ============================================================================
// API CALLS
// ============================================================================

async function loadStrategies() {
    try {
        const response = await fetch('/api/strategies');
        const data = await response.json();
        strategies = data;
        
        // Populate strategy select
        strategySelect.innerHTML = '<option value="">Choose a strategy...</option>';
        for (const strategy of strategies) {
            strategySelect.innerHTML += `
                <option value="${strategy.id}">${strategy.name}</option>
            `;
        }
    } catch (error) {
        showMessage('Error loading strategies: ' + error, 'error');
    }
}

async function loadRealData() {
    try {
        const symbolsText = document.getElementById('symbols').value;
        const symbols = symbolsText.split(',').map(s => s.trim()).filter(s => s);
        
        // Get numDays - try from element first, fallback to calculated from dates
        let numDays = 252; // default
        const numDaysEl = document.getElementById('numDays');
        if (numDaysEl && numDaysEl.value) {
            numDays = parseInt(numDaysEl.value);
        } else {
            // Calculate from date range if available
            const startDateEl = document.getElementById('startDate');
            const endDateEl = document.getElementById('endDate');
            if (startDateEl && endDateEl && startDateEl.value && endDateEl.value) {
                const start = new Date(startDateEl.value);
                const end = new Date(endDateEl.value);
                const daysInMs = end - start;
                numDays = Math.max(10, Math.ceil(daysInMs / (1000 * 60 * 60 * 24)));
            }
        }
        
        if (!symbols.length) {
            showMessage('Please enter at least one symbol', 'error');
            return;
        }
        
        // Validate symbols first
        showLoading(`Validating symbols...`);
        const isValid = await validateSymbols(symbols);
        
        if (!isValid) {
            showMessage('Some symbols could not be validated. Check the messages above.', 'warning');
            // Continue anyway if at least some symbols are valid
        }
        
        showLoading(`Fetching data for ${symbols.length} symbols...`);
        
        const response = await fetch('/api/load-real-data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbols, num_days: numDays })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentSymbols = data.assets;  // Store loaded symbols
            showMessage('✓ ' + data.message, 'success');
        } else {
            showMessage('Error: ' + data.error, 'error');
        }
    } catch (error) {
        showMessage('Error loading real data: ' + error, 'error');
    }
}

async function runBacktest() {
    try {
        const strategyId = strategySelect.value;
        
        if (!strategyId) {
            showMessage('Please select a strategy', 'error');
            return;
        }
        
        // Collect parameters
        const paramInputs = document.querySelectorAll('.param-input');
        const params = {};
        for (const input of paramInputs) {
            params[input.name] = input.value;
        }
        
        // Also collect hidden allocation JSON field if present
        const allocationJSON = document.getElementById('allocationJSON');
        if (allocationJSON) {
            params['allocation_json'] = allocationJSON.value;
        }
        
        // Always use real data from Yahoo Finance
        const symbols = document.getElementById('symbols').value.split(',').map(s => s.trim()).filter(s => s);
        const initialCapital = parseFloat(document.getElementById('initialCapital').value);
        
        // Calculate numDays - try from element first, fallback to calculated from dates
        let numDays = 252; // default
        const numDaysEl = document.getElementById('numDays');
        if (numDaysEl && numDaysEl.value) {
            numDays = parseInt(numDaysEl.value);
        } else {
            // Calculate from date range if available
            const startDateEl = document.getElementById('startDate');
            const endDateEl = document.getElementById('endDate');
            if (startDateEl && endDateEl && startDateEl.value && endDateEl.value) {
                const start = new Date(startDateEl.value);
                const end = new Date(endDateEl.value);
                const daysInMs = end - start;
                numDays = Math.max(10, Math.ceil(daysInMs / (1000 * 60 * 60 * 24)));
            }
        }
        
        showLoading('Running backtest...');
        
        const response = await fetch('/api/backtest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                use_real_data: true,
                symbols,
                strategy_id: strategyId,
                strategy_params: params,
                initial_capital: initialCapital,
                num_days: numDays
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentResult = data.result;
            displaySingleResult(currentResult);
            showMessage('✓ Backtest completed', 'success');
        } else {
            showMessage('Error: ' + data.error, 'error');
        }
    } catch (error) {
        showMessage('Error: ' + error, 'error');
    }
}

async function runQuickCompare() {
    try {
        // Always use real data from Yahoo Finance
        const symbols = document.getElementById('symbols').value.split(',').map(s => s.trim()).filter(s => s);
        const initialCapital = parseFloat(document.getElementById('initialCapital').value);
        
        if (symbols.length === 0) {
            showMessage('Please load some symbols first', 'warning');
            return;
        }
        
        // Calculate numDays - try from element first, fallback to calculated from dates
        let numDays = 252; // default
        const numDaysEl = document.getElementById('numDays');
        if (numDaysEl && numDaysEl.value) {
            numDays = parseInt(numDaysEl.value);
        } else {
            // Calculate from date range if available
            const startDateEl = document.getElementById('startDate');
            const endDateEl = document.getElementById('endDate');
            if (startDateEl && endDateEl && startDateEl.value && endDateEl.value) {
                const start = new Date(startDateEl.value);
                const end = new Date(endDateEl.value);
                const daysInMs = end - start;
                numDays = Math.max(10, Math.ceil(daysInMs / (1000 * 60 * 60 * 24)));
            }
        }
        
        // Build equal-weight allocation for loaded symbols
        const equalWeight = (1 / symbols.length).toFixed(2);
        const allocationObj = {};
        symbols.forEach(s => {
            allocationObj[s] = parseFloat(equalWeight);
        });
        const allocationJson = JSON.stringify(allocationObj);
        
        // Define 4 default strategies using the user's loaded symbols
        const defaultStrategies = [
            {
                strategy_id: 'buy_hold_single',
                name: `Buy & Hold (${symbols[0]})`,
                params: { symbol: symbols[0] }
            },
            {
                strategy_id: 'balanced',
                name: `Balanced (${symbols.slice(0, 2).join('/')}`,
                params: { allocation_json: allocationJson }
            },
            {
                strategy_id: 'momentum',
                name: 'Momentum Strategy',
                params: { short_window: '20', long_window: '50' }
            },
            {
                strategy_id: 'rebalance',
                name: `Quarterly Rebalancing (${symbols.slice(0, 2).join('/')})`,
                params: { 
                    allocation_json: allocationJson,
                    frequency: '63'
                }
            }
        ];
        
        showLoading('Comparing 4 strategies...');
        
        const response = await fetch('/api/compare', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                use_real_data: true,
                symbols,
                strategies: defaultStrategies,
                initial_capital: initialCapital,
                num_days: numDays
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayComparison(data);
            showMessage('✓ Comparison completed', 'success');
        } else {
            showMessage('Error: ' + data.error, 'error');
        }
    } catch (error) {
        showMessage('Error: ' + error, 'error');
    }
}

// ============================================================================
// DISPLAY FUNCTIONS
// ============================================================================

function displaySingleResult(result) {
    hideResults();
    
    // Clear any previous error messages
    status.classList.add('hidden');
    status.textContent = '';
    
    // Update metrics
    document.getElementById('strategyName').textContent = result.strategy_name;
    document.getElementById('totalReturn').textContent = result.total_return + '%';
    document.getElementById('annualReturn').textContent = result.annual_return + '%';
    document.getElementById('maxDD').textContent = result.max_drawdown + '%';
    document.getElementById('sharpeRatio').textContent = result.sharpe_ratio.toFixed(2);
    
    document.getElementById('initialVal').textContent = '$' + formatNumber(result.initial_capital);
    document.getElementById('finalVal').textContent = '$' + formatNumber(result.final_value);
    document.getElementById('period').textContent = result.start_date + ' to ' + result.end_date;
    
    // Draw chart
    drawEquityChart(result.snapshots);
    
    singleResults.classList.remove('hidden');
}

function displayComparison(data) {
    hideResults();
    
    console.log('Comparison data received:', data);
    console.log('Results:', data.results);
    
    if (data.results && data.results.length > 0) {
        console.log('First result:', data.results[0]);
        console.log('First result snapshots:', data.results[0].snapshots);
    }
    
    // Draw comparison chart
    drawComparisonChart(data.results);
    
    // Update best metrics
    document.getElementById('bestReturn').textContent = data.best_return;
    document.getElementById('bestSharpe').textContent = data.best_sharpe;
    document.getElementById('bestDD').textContent = data.best_dd;
    
    // Populate table
    const tbody = document.getElementById('comparisonBody');
    tbody.innerHTML = '';
    
    for (const result of data.results) {
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${result.name}</td>
            <td>$${formatNumber(result.initial)}</td>
            <td>$${formatNumber(result.final)}</td>
            <td>${result.return}%</td>
            <td>${result.annual}%</td>
            <td>${result.max_dd}%</td>
            <td>${result.sharpe.toFixed(2)}</td>
        `;
    }
    
    comparisonResults.classList.remove('hidden');
}

function drawEquityChart(snapshots) {
    const ctx = document.getElementById('equityChart').getContext('2d');
    
    // Validate snapshots data exists
    if (!snapshots || !Array.isArray(snapshots) || snapshots.length === 0) {
        document.getElementById('equityChart').innerHTML = '<p style="color: #dc2626;">No equity data available</p>';
        return;
    }
    
    const dates = snapshots.map(s => s.date);
    const values = snapshots.map(s => s.value);
    
    // Destroy existing chart
    if (equityChart) {
        equityChart.destroy();
    }
    
    equityChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Portfolio Value',
                data: values,
                borderColor: '#2563eb',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                borderWidth: 2,
                tension: 0.1,
                fill: true,
                pointRadius: 0,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    ticks: {
                        callback: function(value) {
                            return '$' + formatNumber(value);
                        }
                    }
                },
                x: {
                    display: true,
                    ticks: {
                        callback: function(index) {
                            const dateStr = dates[index];
                            if (dateStr) {
                                const date = new Date(dateStr);
                                return date.toLocaleDateString('en-US', {month: 'short', year: '2-digit'});
                            }
                            return '';
                        },
                        maxRotation: 45,
                        minRotation: 0,
                        maxTicksLimit: 12
                    }
                }
            }
        }
    });
}

function drawComparisonChart(results) {
    const canvasEl = document.getElementById('comparisonChart');
    if (!canvasEl) {
        console.error('comparisonChart canvas not found');
        return;
    }
    
    const ctx = canvasEl.getContext('2d');
    
    // Destroy existing chart
    if (comparisonChart) {
        comparisonChart.destroy();
    }
    
    // Validate results
    if (!results || results.length === 0) {
        console.warn('No results provided to drawComparisonChart');
        return;
    }
    
    // Validate first result has snapshots
    if (!results[0] || !results[0].snapshots || !Array.isArray(results[0].snapshots) || results[0].snapshots.length === 0) {
        console.warn('First result has no valid snapshots');
        canvasEl.parentElement.innerHTML = '<p style="color: #dc2626; text-align: center; padding: 20px;">No comparison data available</p>';
        return;
    }
    
    const dates = results[0].snapshots.map(s => s.date);
    
    // Color palette for multiple lines
    const colors = [
        { border: '#2563eb', bg: 'rgba(37, 99, 235, 0.1)' },      // Blue
        { border: '#dc2626', bg: 'rgba(220, 38, 38, 0.1)' },      // Red
        { border: '#16a34a', bg: 'rgba(22, 163, 74, 0.1)' },      // Green
        { border: '#ea580c', bg: 'rgba(234, 88, 12, 0.1)' },      // Orange
        { border: '#7c3aed', bg: 'rgba(124, 58, 237, 0.1)' },     // Purple
        { border: '#0891b2', bg: 'rgba(8, 145, 178, 0.1)' },      // Cyan
    ];
    
    // Create datasets for each strategy
    const datasets = results.map((result, index) => {
        const color = colors[index % colors.length];
        // Validate each result has snapshots
        if (!result || !result.snapshots || !Array.isArray(result.snapshots)) {
            console.warn(`Skipping result ${index}: invalid snapshots`);
            return null; // Skip invalid results
        }
        return {
            label: result.name,
            data: result.snapshots.map(s => s.value),
            borderColor: color.border,
            backgroundColor: color.bg,
            borderWidth: 2.5,
            tension: 0.2,
            fill: false,
            pointRadius: 0,
            pointHoverRadius: 6,
            spanGaps: true
        };
    }).filter(d => d !== null); // Remove null entries
    
    if (datasets.length === 0) {
        console.warn('No valid datasets after filtering');
        return;
    }
    
    console.log(`Drawing comparison chart with ${datasets.length} datasets`);
    
    comparisonChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': $' + formatNumber(context.parsed.y);
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) {
                            return '$' + formatNumber(value);
                        }
                    }
                },
                x: {
                    display: true,
                    ticks: {
                        callback: function(index) {
                            const date = new Date(dates[index]);
                            return date.toLocaleDateString('en-US', {month: 'short', year: '2-digit'});
                        },
                        maxRotation: 45,
                        minRotation: 0,
                        maxTicksLimit: 12
                    }
                }
            }
        }
    });
}

// ============================================================================
// PORTFOLIO OPTIMIZATION FUNCTIONS
// ============================================================================

function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.add('hidden');
        tab.classList.remove('active');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    const selectedTab = document.getElementById(`${tabName}-tab`);
    if (selectedTab) {
        selectedTab.classList.remove('hidden');
        selectedTab.classList.add('active');
    }
    
    // Activate button
    const button = document.querySelector(`[data-tab="${tabName}"]`);
    if (button) {
        button.classList.add('active');
    }
}

async function runOptimization() {
    if (currentSymbols.length < 2) {
        showMessage('Load data with at least 2 symbols to optimize', 'error');
        return;
    }
    
    const optimizationType = document.querySelector('input[name="optimizationType"]:checked').value;
    
    showMessage(`Optimizing for ${optimizationType === 'sharpe' ? 'Maximum Sharpe Ratio' : 'Minimum Variance'}...`, 'loading');
    switchTab('optimization');
    
    try {
        const response = await fetch('/api/optimize-portfolio', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                symbols: currentSymbols,
                type: optimizationType
            })
        });
        
        const data = await response.json();
        
        if (!data.success) {
            showMessage('Optimization failed: ' + data.error, 'error');
            return;
        }
        
        displayOptimization(data);
        showMessage(data.message, 'success');
        
    } catch (error) {
        showMessage('Error: ' + error.message, 'error');
    }
}

async function runFrontier() {
    if (currentSymbols.length < 2) {
        showMessage('Load data with at least 2 symbols', 'error');
        return;
    }
    
    showMessage('Calculating efficient frontier...', 'loading');
    switchTab('optimization');
    
    try {
        const response = await fetch('/api/efficient-frontier', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                symbols: currentSymbols,
                num_points: 50
            })
        });
        
        const data = await response.json();
        
        if (!data.success) {
            showMessage('Error: ' + data.error, 'error');
            return;
        }
        
        displayFrontier(data);
        showMessage(data.message, 'success');
        
    } catch (error) {
        showMessage('Error: ' + error.message, 'error');
    }
}

function displayOptimization(data) {
    // Hide frontier, show optimization
    document.getElementById('frontierResults').classList.add('hidden');
    document.getElementById('emptyStateOpt').classList.add('hidden');
    document.getElementById('optimizationResults').classList.remove('hidden');
    
    // Update metrics
    document.getElementById('optExpectedReturn').textContent = 
        (data.expected_return * 100).toFixed(2) + '%';
    document.getElementById('optVolatility').textContent = 
        (data.volatility * 100).toFixed(2) + '%';
    document.getElementById('optSharpeRatio').textContent = 
        data.sharpe_ratio.toFixed(2);
    
    // Display weights
    const weightsHtml = Object.entries(data.weights)
        .sort((a, b) => b[1] - a[1])
        .map(([symbol, weight]) => `
            <div class="weight-row">
                <div class="weight-symbol">${symbol}</div>
                <div class="weight-bar-container">
                    <div class="weight-bar">
                        <div class="weight-fill" style="width: ${weight * 100}%"></div>
                    </div>
                    <div style="font-size: 0.85em; color: #666;">${(weight * 100).toFixed(1)}%</div>
                </div>
                <div class="weight-value">${(weight * 100).toFixed(1)}%</div>
            </div>
        `).join('');
    document.getElementById('weightsTable').innerHTML = weightsHtml || '<p>No weights</p>';
    
    // Display asset statistics
    const statsHtml = Object.entries(data.asset_stats)
        .map(([symbol, stats]) => `
            <div class="stat-row">
                <div class="stat-label">${symbol}</div>
                <div class="stat-value">
                    <div class="stat-item">
                        <div class="stat-item-label">Annual Return</div>
                        <div class="stat-item-value">${(stats.return * 100).toFixed(2)}%</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-item-label">Volatility</div>
                        <div class="stat-item-value">${(stats.volatility * 100).toFixed(2)}%</div>
                    </div>
                </div>
            </div>
        `).join('');
    document.getElementById('assetStatsTable').innerHTML = statsHtml;
    
    // Display correlation matrix
    if (data.correlation && typeof data.correlation === 'object' && Object.keys(data.correlation).length > 0) {
        const symbols = Object.keys(data.correlation);
        const corrTable = `
            <table class="corr-table">
                <thead>
                    <tr>
                        <th></th>
                        ${symbols.map(s => `<th>${s}</th>`).join('')}
                    </tr>
                </thead>
                <tbody>
                    ${symbols.map(s1 => `
                        <tr>
                            <th>${s1}</th>
                            ${symbols.map(s2 => {
                                const corr = data.correlation[s1][s2];
                                let className = 'corr-neutral';
                                if (corr > 0.5) className = 'corr-positive';
                                else if (corr < -0.5) className = 'corr-negative';
                                return `<td class="corr-cell ${className}">${corr.toFixed(2)}</td>`;
                            }).join('')}
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        document.getElementById('correlationTable').innerHTML = corrTable;
    } else {
        document.getElementById('correlationTable').innerHTML = '<p style="color: #cbd5e1;">No correlation data available</p>';
    }
}

function displayFrontier(data) {
    // Hide optimization, show frontier
    document.getElementById('optimizationResults').classList.add('hidden');
    document.getElementById('emptyStateOpt').classList.add('hidden');
    document.getElementById('frontierResults').classList.remove('hidden');
    
    // Update metrics
    document.getElementById('frontierMaxSharpe').textContent = 
        data.max_sharpe.sharpe_ratio.toFixed(2);
    document.getElementById('frontierMinVar').textContent = 
        (data.min_variance.volatility * 100).toFixed(2) + '%';
    document.getElementById('frontierPoints').textContent = 
        data.frontier.length;
    
    // Draw frontier chart
    drawFrontierChart(data);
}

function drawFrontierChart(data) {
    const ctx = document.getElementById('frontierChart').getContext('2d');
    
    // Validate frontier data exists
    if (!data.frontier || !Array.isArray(data.frontier) || data.frontier.length === 0) {
        document.getElementById('frontierChart').innerHTML = '<p style="color: #dc2626;">No frontier data available</p>';
        return;
    }
    
    // Extract frontier data
    const frontierPoints = data.frontier.map(p => ({
        x: p.volatility * 100,
        y: p.return * 100
    }));
    
    // Get special points with defensive checks
    const maxSharpe = data.max_sharpe ? {
        x: (data.max_sharpe.volatility || 0) * 100,
        y: (data.max_sharpe.expected_return || 0) * 100,
        label: 'Max Sharpe'
    } : { x: 0, y: 0, label: 'Max Sharpe' };
    
    const minVar = data.min_variance ? {
        x: (data.min_variance.volatility || 0) * 100,
        y: (data.min_variance.expected_return || 0) * 100,
        label: 'Min Variance'
    } : { x: 0, y: 0, label: 'Min Variance' };
    
    if (frontierChart) {
        frontierChart.destroy();
    }
    
    frontierChart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [
                {
                    label: 'Efficient Frontier',
                    data: frontierPoints,
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    showLine: true,
                    borderWidth: 2,
                    fill: false,
                    tension: 0.1,
                    pointRadius: 3,
                    pointHoverRadius: 6
                },
                {
                    label: 'Max Sharpe Ratio',
                    data: [maxSharpe],
                    backgroundColor: '#16a34a',
                    pointRadius: 8,
                    pointHoverRadius: 10,
                    showLine: false
                },
                {
                    label: 'Min Variance',
                    data: [minVar],
                    backgroundColor: '#ea580c',
                    pointRadius: 8,
                    pointHoverRadius: 10,
                    showLine: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: (context) => {
                            const x = context.parsed.x.toFixed(2);
                            const y = context.parsed.y.toFixed(2);
                            return `Return: ${y}%, Risk: ${x}%`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'linear',
                    title: {
                        display: true,
                        text: 'Volatility (%)'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Expected Return (%)'
                    }
                }
            }
        }
    });
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function formatNumber(num) {
    return Math.round(num).toLocaleString();
}

// ============================================================================
// AUTOCOMPLETE & VALIDATION FUNCTIONS
// ============================================================================

async function handleSymbolsInput(e) {
    const input = e.target;
    const value = input.value.trim();
    
    // Get the last symbol being typed
    const lastComma = value.lastIndexOf(',');
    let query = lastComma === -1 ? value : value.substring(lastComma + 1);
    query = query.trim().toUpperCase();
    
    const autocompleteList = document.getElementById('symbolsAutocomplete');
    
    if (query.length < 1) {
        autocompleteList.classList.add('hidden');
        return;
    }
    
    try {
        const response = await fetch(`/api/symbols-autocomplete?q=${query}`);
        const data = await response.json();
        
        autocompleteList.innerHTML = '';
        
        if (data.suggestions && data.suggestions.length > 0) {
            data.suggestions.forEach(symbol => {
                const li = document.createElement('li');
                li.className = 'autocomplete-item';
                li.innerHTML = `<strong>${symbol}</strong>`;
                li.addEventListener('click', () => selectSymbol(symbol, input));
                autocompleteList.appendChild(li);
            });
            autocompleteList.classList.remove('hidden');
        } else {
            autocompleteList.classList.add('hidden');
        }
    } catch (error) {
        console.error('Autocomplete error:', error);
        autocompleteList.classList.add('hidden');
    }
}

function selectSymbol(symbol, inputElement) {
    const currentValue = inputElement.value.trim();
    const lastComma = currentValue.lastIndexOf(',');
    
    let newValue;
    if (lastComma === -1) {
        newValue = symbol;
    } else {
        const beforeComma = currentValue.substring(0, lastComma + 1);
        newValue = beforeComma + ' ' + symbol;
    }
    
    inputElement.value = newValue + ', ';
    inputElement.focus();
    
    document.getElementById('symbolsAutocomplete').classList.add('hidden');
    
    // Clear validation message
    const validationDiv = document.getElementById('symbolsValidation');
    validationDiv.classList.add('hidden');
}

async function validateSymbols(symbols) {
    if (!symbols || symbols.length === 0) {
        return;
    }
    
    try {
        const response = await fetch('/api/validate-symbols', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbols: symbols })
        });
        
        const data = await response.json();
        const validationDiv = document.getElementById('symbolsValidation');
        
        if (data.valid) {
            validationDiv.className = 'symbols-validation success';
            validationDiv.innerHTML = `✓ All symbols validated (${data.loaded_symbols.length}/${symbols.length})`;
            validationDiv.classList.remove('hidden');
            return true;
        } else {
            let message = data.error || 'Validation failed';
            if (data.missing_symbols && data.missing_symbols.length > 0) {
                if (data.loaded_symbols.length > 0) {
                    validationDiv.className = 'symbols-validation warning';
                    message = `⚠ ${data.loaded_symbols.length} valid (missing: ${data.missing_symbols.join(', ')})`;
                } else {
                    validationDiv.className = 'symbols-validation error';
                }
            } else {
                validationDiv.className = 'symbols-validation error';
            }
            validationDiv.innerHTML = message;
            validationDiv.classList.remove('hidden');
            return data.loaded_symbols && data.loaded_symbols.length > 0;
        }
    } catch (error) {
        console.error('Validation error:', error);
        const validationDiv = document.getElementById('symbolsValidation');
        validationDiv.className = 'symbols-validation error';
        validationDiv.innerHTML = '✗ Validation error: ' + error.message;
        validationDiv.classList.remove('hidden');
        return false;
    }
}

// ============================================================================
// DARK MODE
// ============================================================================

function toggleDarkMode() {
    const html = document.documentElement;
    html.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', html.classList.contains('dark-mode'));
}

function initializeDarkMode() {
    const isDarkMode = localStorage.getItem('darkMode') === 'true';
    if (isDarkMode) {
        document.documentElement.classList.add('dark-mode');
    }
}

// ============================================================================
// DATE RANGE
// ============================================================================

function setupDateRange() {
    const today = new Date();
    const oneYearAgo = new Date(today.getFullYear() - 1, today.getMonth(), today.getDate());
    
    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');
    
    if (startDateInput && endDateInput) {
        startDateInput.valueAsDate = oneYearAgo;
        endDateInput.valueAsDate = today;
    }
}

async function loadRealDataWithDates() {
    // Just call loadRealData - it now handles both date ranges and numDays
    await loadRealData();
}

// ============================================================================
// PRESET TEMPLATES
// ============================================================================

const PRESET_TEMPLATES = {
    conservative: {
        name: 'Conservative (60/40)',
        symbols: ['VTI', 'AGG'],  // US Total Market, US Aggregate Bonds
        allocation: { 'VTI': 0.6, 'AGG': 0.4 }
    },
    balanced: {
        name: 'Balanced (50/50)',
        symbols: ['VTI', 'VXUS'],  // US & International stocks
        allocation: { 'VTI': 0.5, 'VXUS': 0.5 }
    },
    aggressive: {
        name: 'Aggressive (80/20)',
        symbols: ['QQQ', 'VTI'],  // Tech & Total US Market
        allocation: { 'QQQ': 0.8, 'VTI': 0.2 }
    },
    growth: {
        name: 'Growth (100% Stocks)',
        symbols: ['VTI', 'VXUS'],
        allocation: { 'VTI': 0.6, 'VXUS': 0.4 }
    }
};

function applyPresetTemplate(preset) {
    const template = PRESET_TEMPLATES[preset];
    if (!template) return;
    
    // Get current symbols instead of replacing them
    const currentSymbolsText = document.getElementById('symbols').value.trim();
    const currentSymbolsList = currentSymbolsText.split(',').map(s => s.trim()).filter(s => s);
    
    if (currentSymbolsList.length === 0) {
        // Only set symbols if user hasn't loaded any yet
        document.getElementById('symbols').value = template.symbols.join(', ');
        currentSymbols = template.symbols;
    }
    // Otherwise keep the user's current symbols
    
    // Select balanced strategy
    document.getElementById('strategySelect').value = 'balanced';
    
    // Trigger strategy change to show allocation builder
    const event = new Event('change', { bubbles: true });
    document.getElementById('strategySelect').dispatchEvent(event);
    
    // After a brief delay, update allocation sliders with preset weights
    // But only for symbols that actually exist in current selection
    setTimeout(() => {
        updatePresetsAllocation(template.allocation);
    }, 100);
    
    showMessage(`✓ Applied ${template.name} preset (keeping your symbols)`, 'success');
}

function updatePresetsAllocation(allocation) {
    for (const [symbol, percent] of Object.entries(allocation)) {
        const slider = document.getElementById(`slider-${symbol}`);
        if (slider) {
            slider.value = percent * 100;
            slider.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }
}

// ============================================================================
// SAVE / LOAD CONFIGURATION
// ============================================================================

function saveCurrentConfig() {
    const configName = document.getElementById('configName').value.trim();
    if (!configName) {
        showMessage('Please enter a configuration name', 'warning');
        return;
    }
    
    const config = {
        name: configName,
        symbols: document.getElementById('symbols').value,
        startDate: document.getElementById('startDate').value,
        endDate: document.getElementById('endDate').value,
        initialCapital: document.getElementById('initialCapital').value,
        strategy: document.getElementById('strategySelect').value,
        timestamp: new Date().toISOString()
    };
    
    // Get allocation if it exists
    const allocationJSON = document.getElementById('allocationJSON');
    if (allocationJSON) {
        config.allocation = allocationJSON.value;
    }
    
    // Get other strategy params
    const paramInputs = document.querySelectorAll('.param-input');
    config.params = {};
    paramInputs.forEach(input => {
        config.params[input.name] = input.value;
    });
    
    // Save to localStorage
    let savedConfigs = JSON.parse(localStorage.getItem('backtesterConfigs') || '{}');
    savedConfigs[configName] = config;
    localStorage.setItem('backtesterConfigs', JSON.stringify(savedConfigs));
    
    document.getElementById('configName').value = '';
    loadSavedConfigs();
    showMessage(`✓ Configuration "${configName}" saved`, 'success');
}

function loadSavedConfigs() {
    const savedConfigs = JSON.parse(localStorage.getItem('backtesterConfigs') || '{}');
    const select = document.getElementById('savedConfigs');
    
    select.innerHTML = '<option value="">-- No saved configs --</option>';
    
    Object.keys(savedConfigs).forEach(name => {
        const option = document.createElement('option');
        option.value = name;
        option.textContent = name;
        select.appendChild(option);
    });
}

function loadSelectedConfig() {
    const configName = document.getElementById('savedConfigs').value;
    if (!configName) {
        showMessage('Please select a configuration', 'warning');
        return;
    }
    
    const savedConfigs = JSON.parse(localStorage.getItem('backtesterConfigs') || '{}');
    const config = savedConfigs[configName];
    
    if (!config) {
        showMessage('Configuration not found', 'error');
        return;
    }
    
    // Load values
    document.getElementById('symbols').value = config.symbols;
    document.getElementById('startDate').value = config.startDate || '';
    document.getElementById('endDate').value = config.endDate || '';
    document.getElementById('initialCapital').value = config.initialCapital;
    document.getElementById('strategySelect').value = config.strategy;
    
    // Trigger strategy change
    const event = new Event('change', { bubbles: true });
    document.getElementById('strategySelect').dispatchEvent(event);
    
    // Load params
    setTimeout(() => {
        if (config.allocation) {
            const allocationJSON = document.getElementById('allocationJSON');
            if (allocationJSON) {
                allocationJSON.value = config.allocation;
                updateAllocationDisplay();
            }
        }
        
        if (config.params) {
            Object.entries(config.params).forEach(([name, value]) => {
                const input = document.querySelector(`[name="${name}"]`);
                if (input) input.value = value;
            });
        }
    }, 100);
    
    showMessage(`✓ Loaded configuration: ${configName}`, 'success');
}

function deleteSelectedConfig() {
    const configName = document.getElementById('savedConfigs').value;
    if (!configName) {
        showMessage('Please select a configuration to delete', 'warning');
        return;
    }
    
    if (!confirm(`Delete configuration "${configName}"?`)) return;
    
    const savedConfigs = JSON.parse(localStorage.getItem('backtesterConfigs') || '{}');
    delete savedConfigs[configName];
    localStorage.setItem('backtesterConfigs', JSON.stringify(savedConfigs));
    
    loadSavedConfigs();
    showMessage(`✓ Configuration deleted`, 'success');
}
