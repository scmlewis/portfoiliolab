# 🚀 Web Interface & Real Data Integration

## What's New

### 1. **Web Application** 🌐
- Beautiful, responsive web interface
- Real-time backtesting results
- Interactive charts and visualizations
- Strategy comparison tools

### 2. **Yahoo Finance Integration** 📊
- Real market data (stocks, bonds, ETFs, crypto)
- Historical data from any date
- Multiple symbols support
- Daily updated data

### 3. **Real Data Module** 📈
- Python API for easy data loading
- Multiple asset type support
- Automatic date range handling
- Error handling and retry logic

---

## Quick Start

### Option 1: Web Interface (Recommended)

**Step 1: Install Dependencies**
```bash
pip install -r requirements.txt
```

**Step 2: Run the App**
```bash
# Windows with Anaconda
& "C:\Users\Lewis\anaconda3\python.exe" app.py

# Or simple (if Python in PATH)
python app.py
```

**Step 3: Open Browser**
```
http://localhost:5000
```

**Step 4: Start Backtesting!**
- Load data (sample or real)
- Select strategy
- Click "Run Backtest"
- See results with charts

### Option 2: Python API

```python
from real_data import load_real_data
from backtester_standalone import Backtester, Strategies
from src.assets import AssetType

# Load real data from Yahoo Finance
assets = load_real_data({
    'AAPL': AssetType.STOCK,
    'MSFT': AssetType.STOCK,
    'BND': AssetType.BOND
}, num_days=252)

# Run backtest
backtester = Backtester(assets)
result = backtester.run(
    Strategies.balanced_portfolio({'AAPL': 0.5, 'BND': 0.5}),
    100000
)

print(f"Return: {result.total_return*100:.2f}%")
print(f"Sharpe: {result.sharpe_ratio:.2f}")
```

---

## File Structure

```
backtester/
├── 🌐 WEB APPLICATION
│   ├── app.py                    # Flask web server
│   ├── templates/
│   │   └── index.html           # Web UI
│   └── static/
│       ├── style.css            # Styling
│       └── app.js               # Frontend logic
│
├── 📊 REAL DATA
│   ├── real_data.py             # Yahoo Finance integration
│   ├── example_real_data.py     # 5 Real data examples
│   └── WEB_INTERFACE_GUIDE.md   # Web app documentation
│
├── 🎯 CORE BACKTESTER (unchanged)
│   ├── backtester_standalone.py
│   └── src/
│       ├── assets.py
│       ├── backtester.py
│       ├── strategies.py
│       └── data_generator.py
│
└── 📚 DOCUMENTATION
    ├── START_HERE.md
    ├── GUIDE.md
    └── QUICK_REFERENCE.py
```

---

## Features

### Web Interface

#### Left Panel
- **Data Source Selection**
  - Load sample data (no internet)
  - Load real data from Yahoo Finance
  - Specify symbols and time period

- **Configuration**
  - Set initial capital
  - Select strategy
  - Configure strategy parameters

- **Actions**
  - Run single backtest
  - Quick compare (4 strategies)

#### Right Panel
- **Single Backtest Results**
  - 4 key metrics (return, drawdown, Sharpe, annual return)
  - Portfolio values
  - Equity curve chart

- **Comparison Results**
  - Side-by-side strategy table
  - Best metrics highlighted
  - Performance ranking

### Real Data Features

**Yahoo Finance Data**
- US stocks (AAPL, MSFT, GOOGL, etc.)
- ETFs (BND, VTI, VTIAX, etc.)
- Cryptocurrencies (BTC-USD, ETH-USD)
- Commodities (GLD, USO, DBC)
- Any symbol with daily OHLC data

**Data Loading**
- Automatic date range calculation
- Error handling and validation
- Progress messages
- Retry logic

---

## Real Data Examples

### Example 1: Single Stock
```python
from real_data import load_real_data
from src.assets import AssetType

assets = load_real_data({'AAPL': AssetType.STOCK})
# Loads AAPL data for last 252 days
```

### Example 2: Multiple Stocks
```python
assets = load_real_data({
    'AAPL': AssetType.STOCK,
    'MSFT': AssetType.STOCK,
    'GOOGL': AssetType.STOCK
})
```

### Example 3: Mixed Assets
```python
assets = load_real_data({
    'AAPL': AssetType.STOCK,
    'MSFT': AssetType.STOCK,
    'BND': AssetType.BOND,
    'BTC-USD': AssetType.CRYPTO
})
```

### Example 4: Custom Time Period
```python
assets = load_real_data({
    'AAPL': AssetType.STOCK
}, num_days=504)  # 2 years instead of 1
```

### Example 5: Get Default Portfolio
```python
from real_data import load_default_portfolio

assets = load_default_portfolio()
# Loads: AAPL, MSFT, GOOGL, AMZN, TSLA, BND, BTC-USD
```

---

## Web Interface Workflows

### Workflow 1: Test Strategy with Real Data

1. Open http://localhost:5000
2. Check "Use Real Data"
3. Enter: AAPL, MSFT, BND
4. Click "Load Real Data"
5. Select strategy
6. Click "Run Backtest"
7. See results and equity curve

### Workflow 2: Compare Allocation Strategies

1. Load real data (AAPL, BND)
2. Select "Balanced Portfolio"
3. Try allocation: {"AAPL": 0.8, "BND": 0.2}
4. Run backtest, note results
5. Change allocation: {"AAPL": 0.6, "BND": 0.4}
6. Run again and compare

### Workflow 3: Quick Multi-Strategy Comparison

1. Load real data
2. Click "Quick Compare (4 Strategies)"
3. View comparison table
4. See best performers by metric
5. Identify best risk-adjusted strategy

### Workflow 4: Long-term Analysis

1. Load real data with 1260 days (5 years)
2. Test momentum strategy
3. Test balanced portfolio
4. Compare performance over market cycles

---

## Installing Dependencies

### Full Installation

```bash
# Install all packages
pip install -r requirements.txt

# Or individually
pip install yfinance        # Yahoo Finance
pip install flask          # Web framework
pip install flask-cors     # CORS support
```

### Verify Installation

```bash
python -c "import yfinance; print(yfinance.__version__)"
python -c "import flask; print(flask.__version__)"
```

### Troubleshooting

**Error: "No module named yfinance"**
```bash
# Use your Python executable directly
C:\Users\Lewis\anaconda3\python.exe -m pip install yfinance
```

**Error: "SSL: CERTIFICATE_VERIFY_FAILED"**
```bash
# Update certificates (macOS only)
/Applications/Python\ 3.x/Install\ Certificates.command
```

---

## API Reference

### REST Endpoints

**Load Sample Data**
```
GET /api/sample-data
Response: {success, assets, message}
```

**Load Real Data**
```
POST /api/load-real-data
Body: {symbols: [...], num_days: 252}
Response: {success, assets, message}
```

**Run Backtest**
```
POST /api/backtest
Body: {
  use_real_data: bool,
  symbols: [...],
  strategy_id: string,
  strategy_params: {...},
  initial_capital: number,
  num_days: number
}
Response: {success, result: {...}}
```

**Compare Strategies**
```
POST /api/compare
Body: {
  use_real_data: bool,
  symbols: [...],
  strategies: [{strategy_id, name, params}, ...],
  initial_capital: number,
  num_days: number
}
Response: {success, results: [...], best_return, best_sharpe, best_dd}
```

**Get Available Strategies**
```
GET /api/strategies
Response: [{id, name, params: [{name, type, label, value}, ...]}, ...]
```

**Get Default Symbols**
```
GET /api/default-symbols
Response: {symbols: [...], descriptions: {...}}
```

---

## Real Data Sources & Symbols

### US Mega-Cap Stocks
- AAPL, MSFT, GOOGL, AMZN, TSLA

### Blue Chip Stocks
- JPM, JNJ, V, KO, PG

### Tech Stocks
- NVDA, AMD, ADBE, INTC, ORCL

### Financial
- GS, BAC, MS, BLK, AXP

### ETFs & Bonds
- BND (Total Bond)
- AGG (Aggregate Bond)
- VTI (Total Stock Market)
- VTIAX (International)

### Cryptocurrencies
- BTC-USD, ETH-USD, BNB-USD

### Commodities
- GLD (Gold), SLV (Silver), USO (Oil)
- DBC (Commodities Index)

---

## Performance & Tips

### For Best Performance
- Use 252 days of data (1 year balance)
- Limit to 5-10 symbols
- Use sample data for quick testing
- Real data slower but more accurate

### For Accurate Analysis
- Use at least 252 days (1 year)
- Include multiple market cycles
- Compare multiple strategies
- Look at Sharpe ratio for risk-adjustment

### Troubleshooting Slow Data Loading
- Fewer symbols = faster load
- Shorter time period = faster load
- Use sample data first
- Real data API can be slow sometimes

---

## Running Examples

### Example: Real Data Backtests

```bash
# Run 5 examples with real Yahoo Finance data
python example_real_data.py
```

Examples include:
1. Single stock backtest
2. Compare multiple stocks
3. Stocks & bonds allocation
4. Momentum strategy
5. Rebalancing strategy

---

## Next Steps

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Run web app**: `python app.py`
3. **Open browser**: http://localhost:5000
4. **Load real data** from Yahoo Finance
5. **Backtest strategies** with real market data
6. **Compare results** to find best allocation

---

## Support

- **Web Interface Guide**: See `WEB_INTERFACE_GUIDE.md`
- **Real Data Examples**: See `example_real_data.py`
- **Core Documentation**: See `GUIDE.md`
- **Code Examples**: See `QUICK_REFERENCE.py`

---

Happy backtesting with real data! 📈🎉
