# PortfolioLab

A Flask-based web application for backtesting investment portfolios with real market data, multiple strategies, and interactive visualizations.

 **Live Demo**: [https://portfoiliolab.onrender.com](https://portfoiliolab.onrender.com)

---

## Why this exists

Portfolio theory is taught with formulas and rarely touched by hand. PortfolioLab puts Monte Carlo simulation, Sharpe and VaR/CVaR in one toolkit so the maths becomes something you can poke at with your own numbers.

## Features

-  **Real Market Data**: Fetch live stock prices from Yahoo Finance
-  **7 Trading Strategies**: Buy & Hold, Balanced, Momentum, Rebalance, RSI, MACD, Bollinger
-  **Interactive Charts**: Visualize equity curves with Chart.js
-  **Mobile Responsive**: Clean, modern UI that works on all devices
-  **Quick Compare**: Side-by-side strategy comparison
-  **Portfolio Optimization**: Modern Portfolio Theory (MPT)
-  **Monte Carlo Simulation**: Risk analysis with 1000+ scenarios
-  **Performance Metrics**: Returns, Max Drawdown, Sharpe Ratio, VaR/CVaR

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Flask app
python app.py
```

Visit `http://localhost:5000` to use the web interface.

### Production Deployment (Render)

This app is deployed on [Render](https://render.com) with automatic deployments from GitHub.

#### One-Click Deploy

1. Fork this repository
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Click **New +** → **Web Service**
4. Connect your GitHub repository
5. Render will auto-detect the configuration from `render.yaml`
6. Click **Create Web Service**

#### Manual Configuration

If `render.yaml` isn't detected, configure manually:

| Setting | Value |
|---------|-------|
| **Name** | portfoiliolab |
| **Runtime** | Python |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app --workers 2 --threads 4 --timeout 120 --bind 0.0.0.0:$PORT` |
| **Python Version** | 3.12.7 |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface |
| `/api/strategies` | GET | List available strategies |
| `/api/symbols-autocomplete` | GET | Symbol search |
| `/api/backtest` | POST | Run single backtest |
| `/api/compare` | POST | Compare multiple strategies |
| `/api/optimize-portfolio` | POST | MPT optimization |
| `/api/efficient-frontier` | POST | Efficient frontier |
| `/api/monte-carlo` | POST | Monte Carlo simulation |
| `/api/rolling-metrics` | POST | Rolling Sharpe/volatility |

## Available Strategies

| Strategy | Description | Parameters |
|----------|-------------|------------|
| **Buy & Hold** | Single asset buy and hold | symbol, allocation |
| **Balanced Portfolio** | Static multi-asset allocation | allocations dict |
| **Momentum** | Moving average crossover | short_window, long_window |
| **Rebalance** | Periodic rebalancing | allocations, frequency |
| **RSI Oversold** | RSI-based mean reversion | symbol, rsi_period, oversold_level |
| **MACD** | MACD crossover signals | symbol, fast, slow, signal |
| **Bollinger Bands** | Band-based mean reversion | symbol, period, num_std |

## Technology Stack

- **Backend**: Flask 3.0+, Python 3.12
- **Data Source**: Yahoo Finance (yfinance)
- **Financial Libraries**: numpy, scipy
- **Frontend**: Vanilla JavaScript, Chart.js
- **Styling**: Custom CSS (Material 3 design)
- **Deployment**: Render (Gunicorn WSGI server)

## Project Structure

```
portfoiliolab/
├── app.py                     # Flask application and API endpoints
├── requirements.txt           # Python dependencies
├── Procfile                   # Render deployment configuration
├── runtime.txt                # Python version specification
├── render.yaml                # Render infrastructure as code
├── README.md                  # This file
│
├── src/                       # Core backtesting engine
│   ├── __init__.py
│   ├── assets.py              # Asset/PriceData dataclasses
│   ├── backtester.py          # Portfolio, Backtester, Comparator
│   ├── data_generator.py      # Sample data generation
│   └── strategies.py          # All 7 trading strategies
│
├── real_data.py               # Yahoo Finance integration
├── portfolio_optimizer.py     # Modern Portfolio Theory
├── monte_carlo.py             # Monte Carlo simulation
│
├── templates/
│   └── index.html             # Main web interface
│
├── static/
│   ├── style.css              # Responsive CSS (Material 3)
│   ├── app.js                 # Frontend JavaScript
│   └── collapsible.js         # UI interactions
│
└── test_strategies.py         # Comprehensive test suite
```

## Testing

```bash
# Run all tests
pytest test_strategies.py -v

# Run with coverage
pytest test_strategies.py --cov=src

# Run specific test class
pytest test_strategies.py::TestBuyAndHold -v
```

## Known Limitations

- No transaction costs or slippage modeling
- No dividend reinvestment
- Simple daily execution (no intraday trading)
- Requires internet connection for market data
- Rate limited by Yahoo Finance API
- Free tier spins down after 15 minutes of inactivity

## Future Enhancements

- [x] RSI, MACD, Bollinger Bands strategies
- [x] Monte Carlo simulations
- [x] Portfolio optimization (MPT)
- [ ] Transaction cost modeling
- [ ] Parameter optimization tools
- [ ] Export results to CSV/PDF
- [ ] Multi-currency support
- [ ] WebSocket for real-time updates

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
---

If this saved you time or gave you an idea, a ⭐ on the repo is appreciated — it helps others find it.
