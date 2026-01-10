# Web Interface Guide

## Features

The web application provides:

✅ **Interactive Dashboard** - Beautiful UI for backtesting
✅ **Real Data Integration** - Yahoo Finance data feeds
✅ **Strategy Comparison** - Compare multiple strategies side-by-side
✅ **Performance Charts** - Visualize equity curves
✅ **Custom Parameters** - Configure strategies with custom parameters

---

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `yfinance` - Yahoo Finance data
- `flask` - Web framework
- `flask-cors` - Cross-origin requests
- Optional: pandas, numpy, matplotlib

### 2. Verify Installation

```bash
pip list | findstr yfinance flask
```

Should show:
```
flask                     2.3.0
flask-cors               4.0.0
yfinance                 0.2.18
```

---

## Running the App

### Quick Start

```bash
# Use Anaconda Python
& "C:\Users\Lewis\anaconda3\python.exe" app.py

# Or if Python is in PATH
python app.py
```

### Output

```
================================================================================
INVESTMENT BACKTESTER WEB APPLICATION
================================================================================

Starting Flask server on http://localhost:5000

Features:
  ✓ Web interface for backtesting
  ✓ Real data from Yahoo Finance
  ✓ Multiple strategy comparison
  ✓ Custom parameters

Tip: Use Ctrl+C to stop the server
================================================================================
```

### Access the App

Open your browser to:
```
http://localhost:5000
```

---

## Using the Interface

### 1. Load Data

**Option A: Sample Data (No Internet Required)**
- Click "Load Sample Data"
- Uses simulated data for TECH, DIVIDEND, BOND, CRYPTO, COMMODITY

**Option B: Real Data (Yahoo Finance)**
- Check "Use Real Data"
- Enter symbols (comma-separated): AAPL, MSFT, GOOGL, BND
- Enter historical days: 252 (default = 1 year)
- Click "Load Real Data"

### 2. Configure Backtest

**Initial Capital**
- Set starting amount (default: $100,000)

**Select Strategy**
- Buy & Hold (Single Asset)
- Balanced Portfolio
- Momentum Strategy
- Rebalancing Strategy

**Strategy Parameters**
- Parameters appear based on selected strategy
- Examples:
  - Buy & Hold: Symbol (e.g., AAPL)
  - Balanced: JSON allocation {"AAPL": 0.5, "BND": 0.5}
  - Momentum: Short window (20), Long window (50)
  - Rebalancing: Allocation + frequency (days)

### 3. Run Backtest

Click **"Run Backtest"** to execute.

Results show:
- **Total Return** - Overall profit percentage
- **Annual Return** - Annualized return rate
- **Max Drawdown** - Largest decline
- **Sharpe Ratio** - Risk-adjusted return
- **Equity Curve** - Portfolio value over time

### 4. Compare Strategies

Click **"Quick Compare (4 Strategies)"** to compare:
- Buy & Hold
- Balanced Portfolio
- Momentum Strategy
- Quarterly Rebalancing

Results table shows all metrics for each strategy.

---

## Real Data Sources

### Yahoo Finance Symbols

**US Stocks**
```
AAPL      - Apple Inc.
MSFT      - Microsoft Corporation
GOOGL     - Alphabet (Google)
AMZN      - Amazon.com
TSLA      - Tesla Inc.
META      - Meta Platforms
NVDA      - NVIDIA
JPM       - JPMorgan Chase
JNJ       - Johnson & Johnson
```

**ETFs (Bonds, etc.)**
```
BND       - Total Bond Market ETF
AGG       - Aggregate Bond ETF
VTIAX     - International ETF
VTI       - Total Stock Market ETF
```

**Cryptocurrencies**
```
BTC-USD   - Bitcoin
ETH-USD   - Ethereum
```

**Commodities & Others**
```
GLD       - Gold ETF
USO       - Oil ETF
DBC       - Commodities ETF
```

---

## Example Workflows

### Example 1: Test Buy & Hold vs Active Trading

1. **Load Sample Data** (or Real Data with AAPL)
2. **Run Backtest** with "Buy & Hold" strategy → note the return
3. **Run Backtest** with "Momentum" strategy → compare
4. Compare Sharpe ratios to see risk-adjusted performance

### Example 2: Find Optimal Allocation

1. **Load Real Data**: AAPL, MSFT, BND (stocks and bonds)
2. **Try these allocations**:
   - 80/20: {"AAPL": 0.4, "MSFT": 0.4, "BND": 0.2}
   - 60/40: {"AAPL": 0.3, "MSFT": 0.3, "BND": 0.4}
   - 40/60: {"AAPL": 0.2, "MSFT": 0.2, "BND": 0.6}
3. Compare max drawdowns to find best risk/reward

### Example 3: Test Different Time Periods

1. **Load Real Data** with different "Historical Days":
   - 252 days (1 year)
   - 504 days (2 years)
   - 1260 days (5 years)
2. See how strategies perform over longer periods
3. Compare stability and consistency

### Example 4: Momentum Strategy Testing

1. **Load Real Data**: AAPL, MSFT, GOOGL
2. **Select Momentum Strategy**
3. **Test different MA windows**:
   - Short: 20, Long: 50
   - Short: 10, Long: 30
   - Short: 30, Long: 100
4. Find which parameters work best

---

## API Endpoints

If you want to integrate with other tools:

### Load Data
```
GET /api/sample-data
POST /api/load-real-data
  - body: {symbols: [...], num_days: 252}
```

### Run Backtest
```
POST /api/backtest
  - body: {
      use_real_data: bool,
      symbols: [...],
      strategy_id: string,
      strategy_params: {...},
      initial_capital: number,
      num_days: number
    }
```

### Compare Strategies
```
POST /api/compare
  - body: {
      use_real_data: bool,
      symbols: [...],
      strategies: [...],
      initial_capital: number,
      num_days: number
    }
```

### Get Options
```
GET /api/strategies
GET /api/asset-types
GET /api/default-symbols
```

---

## Troubleshooting

### "Failed to load real data"

**Causes:**
- Symbol doesn't exist on Yahoo Finance
- No internet connection
- Service temporarily unavailable

**Solutions:**
1. Verify symbol exists (check Yahoo Finance website)
2. Check internet connection
3. Wait a few minutes and try again
4. Use different symbols

### "Insufficient cash" error

**Cause:** Strategy allocations sum to more than 100%

**Solution:** Ensure allocation JSON percentages sum to 1.0 or less:
```json
{"AAPL": 0.5, "BND": 0.5}  // ✓ Correct (sums to 1.0)
{"AAPL": 0.6, "BND": 0.5}  // ✗ Wrong (sums to 1.1)
```

### Port 5000 already in use

**Solution:** Flask will use another port automatically, or:
```bash
# Kill the process using port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Slow data loading

**Cause:** Yahoo Finance API responses can be slow

**Solutions:**
- Use fewer symbols
- Use fewer days of history
- Retry after a moment
- Use sample data instead

---

## Performance Tips

### For Fast Backtests
- Use sample data (no internet required)
- Use fewer historical days (e.g., 100 instead of 1000)
- Use fewer assets (e.g., 3 instead of 10)

### For Accurate Analysis
- Use at least 252 days (1 year)
- Use multiple years for more robust results
- Include both bull and bear market periods

### For Better Charts
- 252 days = Good balance of data and clarity
- 504 days = 2 years, good trend analysis
- 1260+ days = Long-term patterns

---

## Advanced Usage

### Custom Strategies (Python)

Edit `app.py` to add new strategies:

```python
@app.route('/api/custom-backtest', methods=['POST'])
def api_custom_backtest():
    # Your custom logic here
    pass
```

### Real Data Integration

Use the `real_data.py` module directly:

```python
from real_data import load_real_data
from src.assets import AssetType

# Load multiple assets
assets = load_real_data({
    'AAPL': AssetType.STOCK,
    'MSFT': AssetType.STOCK,
    'BND': AssetType.BOND
}, num_days=252)
```

---

## Next Steps

1. **Run the app**: `python app.py`
2. **Try sample data**: Click "Load Sample Data"
3. **Run a backtest**: Select strategy and click "Run Backtest"
4. **Compare strategies**: Click "Quick Compare"
5. **Use real data**: Load Yahoo Finance data
6. **Experiment**: Try different symbols and parameters

---

Enjoy using the web interface! 🚀📈
