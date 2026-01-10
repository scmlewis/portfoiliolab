# Portfolio Backtester

A Flask-based web application for backtesting investment portfolios with real market data, multiple strategies, and interactive visualizations.

🌐 **Live Demo**: [https://portfoiliolab.onrender.com](https://portfoiliolab.onrender.com)

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Flask app
python app.py
```

Visit `http://localhost:5000` to use the web interface.

### Production Deployment

Deployed on [Render](https://render.com) with automatic deployments from GitHub.

## Features

- 📊 **Real Market Data**: Fetch live stock prices from Yahoo Finance
- 🎯 **Multiple Strategies**: Buy & Hold, Balanced Portfolio, Momentum, Rebalancing
- 📈 **Interactive Charts**: Visualize equity curves with Chart.js
- 📱 **Mobile Responsive**: Clean, modern UI that works on all devices
- ⚡ **Quick Compare**: Side-by-side strategy comparison
- 🔧 **Custom Allocations**: Build your own portfolio with slider controls
- 📉 **Performance Metrics**: Returns, Max Drawdown, Sharpe Ratio, and more

## Project Structure

```
portfoiliolab/
├── app.py                     # Flask application and API endpoints
├── requirements.txt           # Python dependencies
├── Procfile                   # Render deployment configuration
├── runtime.txt                # Python version specification
├── README.md                  # This file
│
├── src/                       # Core backtesting engine
│   ├── __init__.py
│   ├── assets.py             # Asset class definitions
│   ├── backtester.py         # Backtesting engine
│   ├── data_generator.py     # Market data fetching (Yahoo Finance)
│   └── strategies.py         # Strategy implementations
│
├── templates/
│   └── index.html            # Main web interface
│
├── static/
│   ├── style.css             # Responsive CSS
│   ├── app.js                # Frontend JavaScript
│   └── collapsible.js        # UI interactions
│
└── Web Interface

1. Enter stock ticker symbols (e.g., AAPL, MSFT, GOOGL)
2. Set date range for backtesting
3. Choose a strategy or build custom allocations
4. Click "Run Backtest" to see results
5. View equity curve, metrics, and comparison table

### API Endpoints

#### POST `/api/backtest`
Run a backtest with specified parameters.

```json
{
  "symbols": ["AAPL", "MSFT", "GOOGL"],
  "start_date": "2023-01-01",
  "end_date": "2024-01-01",
  "initial_capital": 100000,
  "strategy": "balanced_portfolio",
  "allocations": {"AAPL": 0.33, "MSFT": 0.33, "GOOGL": 0.34}
}
```

#### POST `/api/compare`
Compare multiple strategies side-by-side.

```json
{
  "symbols": ["AAPL", "MSFT"],
  "start_date": "2023-01-01",
  "end_date": "2024-01-01",
  "initial_capital": 100000,
  "strategies": ["buy_and_hold", "balanced_portfolio"]
}
results = [result1, result2, result3]
comparator = Comparator(results)

print(comparator.summary())
best = comparator.get_best("total_return")
```

## Available Strategies

1. **buy_and_hold(symbol, percent_allocation)** - Single asset buy & hold
2. **balanced_portfolio(allocations)** - Static allocation to multiple assets
3. **momentum_strategy(short_window, long_window)** - Moving average crossover
4. **rebalance_strategy(allocations, frequency)** - Periodic rebalancing
5. **stock_bond_allocation(stock_allocation, rebalance)** - Traditional allocation

## Asset Types

- **STOCK**: Tech and dividend stocks with different volatility profiles
- **BOND**: Conservative fixed-income investment
- **CRYPTO**: Highly volatile alternative asset
- **COMMODITY**: Commodity price movements

## PeBuy & Hold** - Purchase and hold all assets equally
2. **Balanced Portfolio** - Custom allocation across assets
3. **Momentum Strategy** - Moving average crossover (20/50 day)
4. **Rebalancing Strategy** - Periodic rebalancing (monthly)

## Supported Assets

- **Stocks**: Any ticker available on Yahoo Finance (AAPL, MSFT, GOOGL, etc.)
- **ETFs**: Index funds, sector ETFs, bond ETFs
- **Crypto**: Major cryptocurrencies (BTC-USD, ETH-USD)
- **International**: Foreign stocks and indice
```

## What's Included

### Asset Types
- **STOCK (TECH)**: High volatilcompound return
- **Max Drawdown**: Largest peak-to-trough decline
- **Sharpe Ratio**: Risk-adjusted return (higher is better)
- **Volatility**: Standard deviation of returns

## Technology Stack

- **Backend**: Flask 3.0.3, Python 3.12
- **Data Source**: Yahoo Finance (yfinance)
- **Financial Libraries**: pandas, numpy, scipy
- **Frontend**: Vanilla JavaScript, Chart.js 3.9.1
- **Styling**: Custom CSS with mobile-first responsive design
- **Deployment**: Render (with gunicorn WSGI server)

## Development

### Requirements

- Python 3.12+
- pip packages listed in [requirements.txt](requirements.txt)

### Local Setup

```bash
# Clone the repository
git clone https://github.com/scmlewis/portfoiliolab.git
cd portfoiliolab

# IKnown Limitations

- No transaction costs or slippage modeling
- No dividend reinvestment
- Simple daily execution (no intraday trading)
- Requires internet connection for market data
- Rate limited by Yahoo Finance API

## Future Enhancements

- [ ] Transaction cost modeling
- [ ] More advanced strategies (RSI, MACD, Bollinger Bands)
- [ ] Parameter optimization tools
- [ ] Monte Carlo simulations
- [ ] Export results to CSV/PDF
- [ ] Portfolio optimization (Modern Portfolio Theory)
- [ ] Risk analytics dashboard
- [ ] Multi-currency support

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Archive

Old MVP files, standalone scripts, and development documentation have been moved to the `archive/` folder for reference.
- Export to CSV/Excel
