"""Flask web application for the Investment Backtester."""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime, timedelta
import traceback

from src.backtester import Backtester, Comparator, Portfolio
from src.strategies import Strategies
from src.data_generator import create_sample_assets
from src.assets import AssetType
from real_data import load_real_data, YahooFinanceDataProvider
from portfolio_optimizer import PortfolioOptimizer, calculate_returns_from_prices
from monte_carlo import PortfolioMonteCarloSimulator, calculate_rolling_metrics


app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_asset_type_options():
    """Get available asset types."""
    return [
        {'value': 'STOCK', 'label': 'Stock'},
        {'value': 'BOND', 'label': 'Bond'},
        {'value': 'CRYPTO', 'label': 'Cryptocurrency'},
        {'value': 'COMMODITY', 'label': 'Commodity'},
    ]


def get_strategy_options():
    """Get available strategies."""
    return [
        {
            'id': 'buy_hold_single',
            'name': 'Buy & Hold (Single Asset)',
            'params': [
                {'name': 'symbol', 'type': 'text', 'label': 'Symbol', 'value': ''}
            ]
        },
        {
            'id': 'balanced',
            'name': 'Balanced Portfolio',
            'params': [
                {'name': 'allocation_json', 'type': 'text', 'label': 'JSON Allocation', 'value': '{"VTI": 0.5, "BND": 0.5}'}
            ]
        },
        {
            'id': 'momentum',
            'name': 'Momentum Strategy',
            'params': [
                {'name': 'short_window', 'type': 'number', 'label': 'Short MA Window', 'value': '20'},
                {'name': 'long_window', 'type': 'number', 'label': 'Long MA Window', 'value': '50'}
            ]
        },
        {
            'id': 'rebalance',
            'name': 'Rebalancing Strategy',
            'params': [
                {'name': 'allocation_json', 'type': 'text', 'label': 'JSON Allocation', 'value': '{"VTI": 0.5, "BND": 0.5}'},
                {'name': 'frequency', 'type': 'number', 'label': 'Rebalance Days', 'value': '63'}
            ]
        },
        {
            'id': 'rsi_oversold',
            'name': 'RSI Oversold Strategy',
            'params': [
                {'name': 'symbol', 'type': 'text', 'label': 'Symbol', 'value': ''},
                {'name': 'rsi_period', 'type': 'number', 'label': 'RSI Period', 'value': '14'},
                {'name': 'oversold_level', 'type': 'number', 'label': 'Oversold Level', 'value': '30'},
                {'name': 'allocation', 'type': 'number', 'label': 'Allocation %', 'value': '1.0'}
            ]
        },
        {
            'id': 'macd',
            'name': 'MACD Crossover Strategy',
            'params': [
                {'name': 'symbol', 'type': 'text', 'label': 'Symbol', 'value': ''},
                {'name': 'fast', 'type': 'number', 'label': 'Fast EMA', 'value': '12'},
                {'name': 'slow', 'type': 'number', 'label': 'Slow EMA', 'value': '26'},
                {'name': 'signal', 'type': 'number', 'label': 'Signal Line', 'value': '9'},
                {'name': 'allocation', 'type': 'number', 'label': 'Allocation %', 'value': '1.0'}
            ]
        },
        {
            'id': 'bollinger',
            'name': 'Bollinger Bands Strategy',
            'params': [
                {'name': 'symbol', 'type': 'text', 'label': 'Symbol', 'value': ''},
                {'name': 'period', 'type': 'number', 'label': 'Period', 'value': '20'},
                {'name': 'num_std', 'type': 'number', 'label': 'Standard Deviations', 'value': '2.0'},
                {'name': 'allocation', 'type': 'number', 'label': 'Allocation %', 'value': '1.0'}
            ]
        },
    ]


def _safe_float(value, default=0.0):
    """Safely convert value to float."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value, default=0):
    """Safely convert value to int."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _load_assets(symbols, num_days, use_real_data=True):
    """Load assets - real or sample data."""
    num_days = _safe_int(num_days, 252)
    num_days = max(10, min(num_days, 3650))

    if use_real_data and symbols:
        symbol_dict = {s: AssetType.STOCK for s in symbols}
        assets = load_real_data(symbol_dict, num_days)
        if assets:
            return assets, False
        return create_sample_assets(num_days=num_days), True
    return create_sample_assets(num_days=num_days), True


# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')


@app.route('/api/asset-types')
def api_asset_types():
    """Get available asset types."""
    return jsonify(get_asset_type_options())


@app.route('/api/strategies')
def api_strategies():
    """Get available strategies."""
    return jsonify(get_strategy_options())


# ============================================================================
# SYMBOL DATABASE
# ============================================================================

SYMBOLS_DB = [
    # === Large Cap US Stocks ===
    {'s': 'AAPL', 'n': 'Apple Inc.', 'c': 'Technology'},
    {'s': 'MSFT', 'n': 'Microsoft Corp.', 'c': 'Technology'},
    {'s': 'GOOGL', 'n': 'Alphabet Inc. (Class A)', 'c': 'Technology'},
    {'s': 'GOOG', 'n': 'Alphabet Inc. (Class C)', 'c': 'Technology'},
    {'s': 'AMZN', 'n': 'Amazon.com Inc.', 'c': 'Technology'},
    {'s': 'NVDA', 'n': 'NVIDIA Corp.', 'c': 'Technology'},
    {'s': 'META', 'n': 'Meta Platforms Inc.', 'c': 'Technology'},
    {'s': 'TSLA', 'n': 'Tesla Inc.', 'c': 'Technology'},
    {'s': 'BRK.B', 'n': 'Berkshire Hathaway (B)', 'c': 'Finance'},
    {'s': 'JPM', 'n': 'JPMorgan Chase & Co.', 'c': 'Finance'},
    {'s': 'V', 'n': 'Visa Inc.', 'c': 'Finance'},
    {'s': 'MA', 'n': 'Mastercard Inc.', 'c': 'Finance'},
    {'s': 'JNJ', 'n': 'Johnson & Johnson', 'c': 'Healthcare'},
    {'s': 'UNH', 'n': 'UnitedHealth Group', 'c': 'Healthcare'},
    {'s': 'LLY', 'n': 'Eli Lilly & Co.', 'c': 'Healthcare'},
    {'s': 'PFE', 'n': 'Pfizer Inc.', 'c': 'Healthcare'},
    {'s': 'ABBV', 'n': 'AbbVie Inc.', 'c': 'Healthcare'},
    {'s': 'MRK', 'n': 'Merck & Co.', 'c': 'Healthcare'},
    {'s': 'ABT', 'n': 'Abbott Laboratories', 'c': 'Healthcare'},
    {'s': 'TMO', 'n': 'Thermo Fisher Scientific', 'c': 'Healthcare'},
    {'s': 'AMGN', 'n': 'Amgen Inc.', 'c': 'Healthcare'},
    {'s': 'ISRG', 'n': 'Intuitive Surgical', 'c': 'Healthcare'},
    {'s': 'MDT', 'n': 'Medtronic plc', 'c': 'Healthcare'},
    {'s': 'BMY', 'n': 'Bristol-Myers Squibb', 'c': 'Healthcare'},
    {'s': 'GILD', 'n': 'Gilead Sciences', 'c': 'Healthcare'},
    {'s': 'CRM', 'n': 'Salesforce Inc.', 'c': 'Technology'},
    {'s': 'ADBE', 'n': 'Adobe Inc.', 'c': 'Technology'},
    {'s': 'NOW', 'n': 'ServiceNow Inc.', 'c': 'Technology'},
    {'s': 'INTC', 'n': 'Intel Corp.', 'c': 'Technology'},
    {'s': 'AMD', 'n': 'Advanced Micro Devices', 'c': 'Technology'},
    {'s': 'QCOM', 'n': 'Qualcomm Inc.', 'c': 'Technology'},
    {'s': 'AVGO', 'n': 'Broadcom Inc.', 'c': 'Technology'},
    {'s': 'TXN', 'n': 'Texas Instruments', 'c': 'Technology'},
    {'s': 'CSCO', 'n': 'Cisco Systems', 'c': 'Technology'},
    {'s': 'NFLX', 'n': 'Netflix Inc.', 'c': 'Technology'},
    {'s': 'DIS', 'n': 'Walt Disney Co.', 'c': 'Entertainment'},
    {'s': 'CMCSA', 'n': 'Comcast Corp.', 'c': 'Entertainment'},
    {'s': 'VZ', 'n': 'Verizon Communications', 'c': 'Telecom'},
    {'s': 'T', 'n': 'AT&T Inc.', 'c': 'Telecom'},
    {'s': 'PYPL', 'n': 'PayPal Holdings', 'c': 'Finance'},
    {'s': 'ADP', 'n': 'ADP Inc.', 'c': 'Technology'},
    {'s': 'COST', 'n': 'Costco Wholesale', 'c': 'Consumer'},
    {'s': 'WMT', 'n': 'Walmart Inc.', 'c': 'Consumer'},
    {'s': 'PG', 'n': 'Procter & Gamble', 'c': 'Consumer'},
    {'s': 'KO', 'n': 'Coca-Cola Co.', 'c': 'Consumer'},
    {'s': 'PEP', 'n': 'PepsiCo Inc.', 'c': 'Consumer'},
    {'s': 'MCD', 'n': "McDonald's Corp.", 'c': 'Consumer'},
    {'s': 'NKE', 'n': 'Nike Inc.', 'c': 'Consumer'},
    {'s': 'SBUX', 'n': 'Starbucks Corp.', 'c': 'Consumer'},
    {'s': 'HD', 'n': 'Home Depot Inc.', 'c': 'Consumer'},
    {'s': 'LOW', "n": "Lowe's Companies", 'c': 'Consumer'},
    {'s': 'TJX', 'n': 'TJX Companies', 'c': 'Consumer'},
    {'s': 'BKNG', 'n': 'Booking Holdings', 'c': 'Travel'},
    {'s': 'MAR', 'n': 'Marriott International', 'c': 'Travel'},
    {'s': 'BA', 'n': 'Boeing Co.', 'c': 'Industrial'},
    {'s': 'CAT', 'n': 'Caterpillar Inc.', 'c': 'Industrial'},
    {'s': 'DE', 'n': 'Deere & Company', 'c': 'Industrial'},
    {'s': 'HON', 'n': 'Honeywell International', 'c': 'Industrial'},
    {'s': 'UPS', 'n': 'United Parcel Service', 'c': 'Industrial'},
    {'s': 'RTX', 'n': 'RTX Corp.', 'c': 'Industrial'},
    {'s': 'LMT', 'n': 'Lockheed Martin', 'c': 'Industrial'},
    {'s': 'GE', 'n': 'GE Aerospace', 'c': 'Industrial'},
    {'s': 'MMM', 'n': '3M Company', 'c': 'Industrial'},
    {'s': 'AXP', 'n': 'American Express', 'c': 'Finance'},
    {'s': 'BLK', 'n': 'BlackRock Inc.', 'c': 'Finance'},
    {'s': 'SCHW', 'n': 'Charles Schwab', 'c': 'Finance'},
    {'s': 'GS', 'n': 'Goldman Sachs', 'c': 'Finance'},
    {'s': 'MS', 'n': 'Morgan Stanley', 'c': 'Finance'},
    {'s': 'C', 'n': 'Citigroup Inc.', 'c': 'Finance'},
    {'s': 'MMC', 'n': 'Marsh & McLennan', 'c': 'Finance'},
    {'s': 'CB', 'n': 'Chubb Ltd.', 'c': 'Finance'},
    {'s': 'AON', 'n': 'Aon plc', 'c': 'Finance'},
    {'s': 'CME', 'n': 'CME Group Inc.', 'c': 'Finance'},
    {'s': 'ICE', 'n': 'Intercontinental Exchange', 'c': 'Finance'},
    {'s': 'SPGI', 'n': 'S&P Global Inc.', 'c': 'Finance'},
    {'s': 'MCO', 'n': "Moody's Corp.", 'c': 'Finance'},
    {'s': 'TFC', 'n': 'Truist Financial', 'c': 'Finance'},
    {'s': 'PNC', 'n': 'PNC Financial Services', 'c': 'Finance'},
    {'s': 'USB', 'n': 'U.S. Bancorp', 'c': 'Finance'},
    {'s': 'TGT', 'n': 'Target Corp.', 'c': 'Consumer'},
    {'s': 'ROST', 'n': 'Ross Stores', 'c': 'Consumer'},
    {'s': 'DG', 'n': 'Dollar General', 'c': 'Consumer'},
    {'s': 'CL', 'n': 'Colgate-Palmolive', 'c': 'Consumer'},
    {'s': 'KMB', 'n': 'Kimberly-Clark', 'c': 'Consumer'},
    {'s': 'MO', 'n': 'Altria Group', 'c': 'Consumer'},
    {'s': 'PM', 'n': 'Philip Morris International', 'c': 'Consumer'},
    {'s': 'EL', 'n': 'Estee Lauder Companies', 'c': 'Consumer'},
    {'s': 'STZ', 'n': 'Constellation Brands', 'c': 'Consumer'},
    {'s': 'KHC', 'n': 'Kraft Heinz Co.', 'c': 'Consumer'},
    {'s': 'GIS', 'n': 'General Mills', 'c': 'Consumer'},
    {'s': 'SYY', 'n': 'Sysco Corp.', 'c': 'Consumer'},
    {'s': 'ADM', 'n': 'Archer-Daniels-Midland', 'c': 'Consumer'},
    {'s': 'EXPD', 'n': 'Expeditors International', 'c': 'Industrial'},

    # === Mid Cap Stocks ===
    {'s': 'SNOW', 'n': 'Snowflake Inc.', 'c': 'Technology'},
    {'s': 'PLTR', 'n': 'Palantir Technologies', 'c': 'Technology'},
    {'s': 'SQ', 'n': 'Block Inc.', 'c': 'Technology'},
    {'s': 'SHOP', 'n': 'Shopify Inc.', 'c': 'Technology'},
    {'s': 'ZS', 'n': 'Zscaler Inc.', 'c': 'Technology'},
    {'s': 'PANW', 'n': 'Palo Alto Networks', 'c': 'Technology'},
    {'s': 'CRWD', 'n': 'CrowdStrike Holdings', 'c': 'Technology'},
    {'s': 'DDOG', 'n': 'Datadog Inc.', 'c': 'Technology'},
    {'s': 'NET', 'n': 'Cloudflare Inc.', 'c': 'Technology'},
    {'s': 'MDB', 'n': 'MongoDB Inc.', 'c': 'Technology'},
    {'s': 'UBER', 'n': 'Uber Technologies', 'c': 'Technology'},
    {'s': 'ABNB', 'n': 'Airbnb Inc.', 'c': 'Technology'},
    {'s': 'COIN', 'n': 'Coinbase Global', 'c': 'Finance'},
    {'s': 'RIVN', 'n': 'Rivian Automotive', 'c': 'Automotive'},
    {'s': 'LCID', 'n': 'Lucid Group', 'c': 'Automotive'},
    {'s': 'SOFI', 'n': 'SoFi Technologies', 'c': 'Finance'},
    {'s': 'HOOD', 'n': 'Robinhood Markets', 'c': 'Finance'},
    {'s': 'DUOL', 'n': 'Duolingo Inc.', 'c': 'Technology'},
    {'s': 'CRSP', 'n': 'CRISPR Therapeutics', 'c': 'Healthcare'},
    {'s': 'DKNG', 'n': 'DraftKings Inc.', 'c': 'Entertainment'},
    {'s': 'RBLX', 'n': 'Roblox Corp.', 'c': 'Entertainment'},
    {'s': 'U', 'n': 'Unity Software', 'c': 'Technology'},
    {'s': 'TTD', 'n': 'The Trade Desk', 'c': 'Technology'},
    {'s': 'ROKU', 'n': 'Roku Inc.', 'c': 'Technology'},
    {'s': 'PATH', 'n': 'UiPath Inc.', 'c': 'Technology'},
    {'s': 'AI', 'n': 'C3.ai Inc.', 'c': 'Technology'},
    {'s': 'ARM', 'n': 'Arm Holdings', 'c': 'Technology'},
    {'s': 'IONQ', 'n': 'IonQ Inc.', 'c': 'Technology'},
    {'s': 'SMCI', 'n': 'Super Micro Computer', 'c': 'Technology'},
    {'s': 'MARA', 'n': 'Marathon Digital Holdings', 'c': 'Crypto'},
    {'s': 'RIOT', 'n': 'Riot Platforms', 'c': 'Crypto'},

    # === International ===
    {'s': 'BABA', 'n': 'Alibaba Group', 'c': 'International'},
    {'s': 'JD', 'n': 'JD.com Inc.', 'c': 'International'},
    {'s': 'PDD', 'n': 'PDD Holdings (Temu)', 'c': 'International'},
    {'s': 'NIO', 'n': 'NIO Inc.', 'c': 'International'},
    {'s': 'TSM', 'n': 'Taiwan Semiconductor', 'c': 'International'},
    {'s': 'ASML', 'n': 'ASML Holding', 'c': 'International'},
    {'s': 'NVO', 'n': 'Novo Nordisk', 'c': 'International'},
    {'s': 'SAP', 'n': 'SAP SE', 'c': 'International'},
    {'s': 'SONY', 'n': 'Sony Group Corp.', 'c': 'International'},
    {'s': 'TM', 'n': 'Toyota Motor Corp.', 'c': 'International'},
    {'s': 'HSBC', 'n': 'HSBC Holdings', 'c': 'International'},
    {'s': 'UL', 'n': 'Unilever plc', 'c': 'International'},
    {'s': 'BP', 'n': 'BP plc', 'c': 'International'},
    {'s': 'SHEL', 'n': 'Shell plc', 'c': 'International'},
    {'s': 'RIO', 'n': 'Rio Tinto Group', 'c': 'International'},
    {'s': 'BHP', 'n': 'BHP Group', 'c': 'International'},
    {'s': 'SNY', 'n': 'Sanofi', 'c': 'International'},
    {'s': 'AZN', 'n': 'AstraZeneca', 'c': 'International'},
    {'s': 'ROCHE', 'n': 'Roche Holding', 'c': 'International'},

    # === ETFs - US Equity ===
    {'s': 'SPY', 'n': 'SPDR S&P 500 ETF', 'c': 'ETF'},
    {'s': 'VOO', 'n': 'Vanguard S&P 500 ETF', 'c': 'ETF'},
    {'s': 'VTI', 'n': 'Vanguard Total Stock Market', 'c': 'ETF'},
    {'s': 'IVV', 'n': 'iShares Core S&P 500', 'c': 'ETF'},
    {'s': 'QQQ', 'n': 'Invesco QQQ (Nasdaq 100)', 'c': 'ETF'},
    {'s': 'VGT', 'n': 'Vanguard Information Technology', 'c': 'ETF'},
    {'s': 'XLK', 'n': 'Technology Select Sector SPDR', 'c': 'ETF'},
    {'s': 'XLF', 'n': 'Financial Select Sector SPDR', 'c': 'ETF'},
    {'s': 'XLE', 'n': 'Energy Select Sector SPDR', 'c': 'ETF'},
    {'s': 'XLV', 'n': 'Health Care Select Sector SPDR', 'c': 'ETF'},
    {'s': 'XLI', 'n': 'Industrial Select Sector SPDR', 'c': 'ETF'},
    {'s': 'XLP', 'n': 'Consumer Staples Select Sector SPDR', 'c': 'ETF'},
    {'s': 'XLY', 'n': 'Consumer Discretionary Select Sector SPDR', 'c': 'ETF'},
    {'s': 'XLU', 'n': 'Utilities Select Sector SPDR', 'c': 'ETF'},
    {'s': 'XLRE', 'n': 'Real Estate Select Sector SPDR', 'c': 'ETF'},
    {'s': 'XLB', 'n': 'Materials Select Sector SPDR', 'c': 'ETF'},
    {'s': 'XLC', 'n': 'Communication Services Select Sector SPDR', 'c': 'ETF'},
    {'s': 'SPLG', 'n': 'SPDR Portfolio S&P 500', 'c': 'ETF'},
    {'s': 'SCHX', 'n': 'Schwab U.S. Large-Cap ETF', 'c': 'ETF'},
    {'s': 'VT', 'n': 'Vanguard Total World Stock', 'c': 'ETF'},

    # === ETFs - International ===
    {'s': 'VXUS', 'n': 'Vanguard Total Intl Stock', 'c': 'ETF'},
    {'s': 'VEA', 'n': 'Vanguard FTSE Developed Markets', 'c': 'ETF'},
    {'s': 'VWO', 'n': 'Vanguard FTSE Emerging Markets', 'c': 'ETF'},
    {'s': 'EFA', 'n': 'iShares MSCI EAFE', 'c': 'ETF'},
    {'s': 'EEM', 'n': 'iShares MSCI Emerging Markets', 'c': 'ETF'},
    {'s': 'IWM', 'n': 'iShares Russell 2000', 'c': 'ETF'},
    {'s': 'IJH', 'n': 'iShares Core S&P Mid-Cap', 'c': 'ETF'},
    {'s': 'IJR', 'n': 'iShares Core S&P Small-Cap', 'c': 'ETF'},
    {'s': 'VXF', 'n': 'Vanguard Extended Market', 'c': 'ETF'},
    {'s': 'SPDW', 'n': 'SPDR Portfolio Developed World ex-US', 'c': 'ETF'},
    {'s': 'SPEM', 'n': 'SPDR Portfolio Emerging Markets', 'c': 'ETF'},
    {'s': 'AOR', 'n': 'iShares Core Growth Allocation', 'c': 'ETF'},
    {'s': 'AOM', 'n': 'iShares Core Moderate Allocation', 'c': 'ETF'},

    # === ETFs - Fixed Income ===
    {'s': 'BND', 'n': 'Vanguard Total Bond Market', 'c': 'Bond ETF'},
    {'s': 'AGG', 'n': 'iShares Core U.S. Aggregate Bond', 'c': 'Bond ETF'},
    {'s': 'TLT', 'n': 'iShares 20+ Year Treasury Bond', 'c': 'Bond ETF'},
    {'s': 'IEF', 'n': 'iShares 7-10 Year Treasury Bond', 'c': 'Bond ETF'},
    {'s': 'SHY', 'n': 'iShares 1-3 Year Treasury Bond', 'c': 'Bond ETF'},
    {'s': 'BNDX', 'n': 'Vanguard Total Intl Bond', 'c': 'Bond ETF'},
    {'s': 'LQD', 'n': 'iShares Investment Grade Corporate Bond', 'c': 'Bond ETF'},
    {'s': 'HYG', 'n': 'iShares High Yield Corporate Bond', 'c': 'Bond ETF'},
    {'s': 'TIP', 'n': 'iShares TIPS Bond', 'c': 'Bond ETF'},
    {'s': 'SCHZ', 'n': 'Schwab U.S. Aggregate Bond', 'c': 'Bond ETF'},
    {'s': 'VCIT', 'n': 'Vanguard Intermediate-Term Corporate Bond', 'c': 'Bond ETF'},
    {'s': 'VCSH', 'n': 'Vanguard Short-Term Corporate Bond', 'c': 'Bond ETF'},
    {'s': 'MUB', 'n': 'iShares National Muni Bond', 'c': 'Bond ETF'},
    {'s': 'VTEB', 'n': 'Vanguard Tax-Exempt Bond', 'c': 'Bond ETF'},

    # === ETFs - Commodities & Alternatives ===
    {'s': 'GLD', 'n': 'SPDR Gold Shares', 'c': 'Commodity ETF'},
    {'s': 'IAU', 'n': 'iShares Gold Trust', 'c': 'Commodity ETF'},
    {'s': 'SLV', 'n': 'iShares Silver Trust', 'c': 'Commodity ETF'},
    {'s': 'USO', 'n': 'United States Oil Fund', 'c': 'Commodity ETF'},
    {'s': 'UNG', 'n': 'United States Natural Gas Fund', 'c': 'Commodity ETF'},
    {'s': 'DBC', 'n': 'Invesco DB Commodity Index', 'c': 'Commodity ETF'},
    {'s': 'PDBC', 'n': 'Invesco Optimum Yield Diversified Commodity', 'c': 'Commodity ETF'},
    {'s': 'VNQ', 'n': 'Vanguard Real Estate ETF', 'c': 'Real Estate ETF'},
    {'s': 'SCHH', 'n': 'Schwab U.S. REIT ETF', 'c': 'Real Estate ETF'},

    # === ETFs - Thematic & Growth ===
    {'s': 'ARKK', 'n': 'ARK Innovation ETF', 'c': 'Thematic ETF'},
    {'s': 'ARKG', 'n': 'ARK Genomic Revolution', 'c': 'Thematic ETF'},
    {'s': 'ICLN', 'n': 'iShares Global Clean Energy', 'c': 'Thematic ETF'},
    {'s': 'SOXX', 'n': 'iShares Semiconductor ETF', 'c': 'Thematic ETF'},
    {'s': 'SMH', 'n': 'VanEck Semiconductor ETF', 'c': 'Thematic ETF'},
    {'s': 'HACK', 'n': 'Procure Cybersecurity ETF', 'c': 'Thematic ETF'},
    {'s': 'BETZ', 'n': 'Roundhill Sports Betting & iGaming', 'c': 'Thematic ETF'},
    {'s': 'SKYY', 'n': 'First Trust Cloud Computing', 'c': 'Thematic ETF'},
    {'s': 'KWEB', 'n': 'KraneShares CSI China Internet', 'c': 'Thematic ETF'},

    # === ETFs - Dividend ===
    {'s': 'VYM', 'n': 'Vanguard High Dividend Yield', 'c': 'Dividend ETF'},
    {'s': 'SCHD', 'n': 'Schwab U.S. Dividend Equity', 'c': 'Dividend ETF'},
    {'s': 'HDV', 'n': 'iShares Core High Dividend', 'c': 'Dividend ETF'},
    {'s': 'DVY', 'n': 'iShares Select Dividend', 'c': 'Dividend ETF'},
    {'s': 'VIG', 'n': 'Vanguard Dividend Appreciation', 'c': 'Dividend ETF'},
    {'s': 'DGRO', 'n': 'iShares Core Dividend Growth', 'c': 'Dividend ETF'},

    # === Crypto (via ETFs/trusts) ===
    {'s': 'BITO', 'n': 'ProShares Bitcoin Strategy', 'c': 'Crypto ETF'},
    {'s': 'IBIT', 'n': 'iShares Bitcoin Trust', 'c': 'Crypto ETF'},
    {'s': 'GBTC', 'n': 'Grayscale Bitcoin Trust', 'c': 'Crypto ETF'},
    {'s': 'ETHE', 'n': 'Grayscale Ethereum Trust', 'c': 'Crypto ETF'},

    # === Preferred Shares / Mixed ===
    {'s': 'SCHP', 'n': 'Schwab U.S. TIPS ETF', 'c': 'Bond ETF'},
    {'s': 'VGSH', 'n': 'Vanguard Short-Term Treasury', 'c': 'Bond ETF'},
    {'s': 'VGIT', 'n': 'Vanguard Intermediate-Term Treasury', 'c': 'Bond ETF'},
    {'s': 'VGLT', 'n': 'Vanguard Long-Term Treasury', 'c': 'Bond ETF'},

    # === Mutual Fund Tickers ===
    {'s': 'VTSAX', 'n': 'Vanguard Total Stock Mkt Index', 'c': 'Mutual Fund'},
    {'s': 'VBTLX', 'n': 'Vanguard Total Bond Mkt Index', 'c': 'Mutual Fund'},
    {'s': 'VTIAX', 'n': 'Vanguard Total Intl Stock Index', 'c': 'Mutual Fund'},
    {'s': 'VFIAX', 'n': 'Vanguard 500 Index Fund', 'c': 'Mutual Fund'},
    {'s': 'VWUSX', 'n': 'Vanguard US Growth Fund', 'c': 'Mutual Fund'},
    {'s': 'PRGFX', 'n': 'T. Rowe Price Growth Stock', 'c': 'Mutual Fund'},

    # === Misc ===
    {'s': 'SCHB', 'n': 'Schwab U.S. Broad Market', 'c': 'ETF'},
    {'s': 'SCHF', 'n': 'Schwab International Equity', 'c': 'ETF'},
    {'s': 'SCHE', 'n': 'Schwab Emerging Markets Equity', 'c': 'ETF'},
]

POPULAR_SYMBOLS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META',
    'SPY', 'QQQ', 'VTI', 'VOO', 'BND', 'AGG', 'GLD', 'VXUS', 'TLT'
]


@app.route('/api/symbols-autocomplete')
def api_symbols_autocomplete():
    """Get autocomplete suggestions for stock symbols."""
    query = request.args.get('q', '').strip().upper()

    if not query:
        popular = [s for s in SYMBOLS_DB if s['s'] in POPULAR_SYMBOLS][:12]
        return jsonify({'results': [{'symbol': p['s'], 'name': p['n'], 'category': p['c']} for p in popular]})

    matched = []
    query_lower = query.lower()
    for item in SYMBOLS_DB:
        if (item['s'].startswith(query) or
            query in item['s'] or
            query_lower in item['n'].lower()):
            matched.append(item)
        if len(matched) >= 20:
            break

    return jsonify({
        'results': [{'symbol': m['s'], 'name': m['n'], 'category': m['c']} for m in matched]
    })


@app.route('/api/popular-symbols')
def api_popular_symbols():
    """Get popular symbol suggestions."""
    popular = [s for s in SYMBOLS_DB if s['s'] in POPULAR_SYMBOLS]
    return jsonify({
        'symbols': [{'symbol': p['s'], 'name': p['n']} for p in popular]
    })


@app.route('/api/validate-symbols', methods=['POST'])
def api_validate_symbols():
    """Validate if symbols exist in Yahoo Finance."""
    try:
        data = request.json
        if not data:
            return jsonify({'valid': False, 'error': 'No data provided'})

        symbols_raw = data.get('symbols', '')
        if isinstance(symbols_raw, str):
            symbols = [s.strip().upper() for s in symbols_raw.split(',') if s.strip()]
        elif isinstance(symbols_raw, list):
            symbols = [str(s).strip().upper() for s in symbols_raw if s]
        else:
            return jsonify({'valid': False, 'error': 'Invalid symbols format'})

        if not symbols:
            return jsonify({'valid': False, 'error': 'No symbols provided'})

        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

        loaded_symbols = []
        missing_symbols = []

        for symbol in symbols:
            asset = YahooFinanceDataProvider.fetch_stock_data(
                symbol, start_date, end_date, max_retries=1, verbose=False
            )
            if asset:
                loaded_symbols.append(symbol)
            else:
                missing_symbols.append(symbol)

        if not loaded_symbols:
            return jsonify({'valid': False, 'error': 'No valid symbols found'})

        return jsonify({
            'valid': True,
            'loaded_symbols': loaded_symbols,
            'missing_symbols': missing_symbols,
            'error': f'Could not load data for: {", ".join(missing_symbols)}' if missing_symbols else None
        })
    except Exception as e:
        return jsonify({'valid': False, 'error': f'Validation error: {str(e)}'})


@app.route('/api/load-real-data', methods=['POST'])
def api_load_real_data():
    """Load real data from Yahoo Finance. Also validates symbols inline."""
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        symbols_raw = data.get('symbols', [])
        if isinstance(symbols_raw, str):
            symbols = [s.strip().upper() for s in symbols_raw.split(',') if s.strip()]
        elif isinstance(symbols_raw, list):
            symbols = [str(s).strip().upper() for s in symbols_raw if s]
        else:
            return jsonify({'success': False, 'error': 'Invalid symbols format'}), 400

        num_days = _safe_int(data.get('num_days', 252), 252)

        if not symbols:
            return jsonify({'success': False, 'error': 'No symbols provided'}), 400

        print(f"\n{'='*60}")
        print(f"Loading real data for: {', '.join(symbols)}")
        print(f"{'='*60}")

        symbol_dict = {s: AssetType.STOCK for s in symbols}
        assets = load_real_data(symbol_dict, num_days)

        if not assets:
            print("\nFailed to load real data, falling back to sample data...")
            assets = create_sample_assets()
            return jsonify({
                'success': True,
                'assets': list(assets.keys()),
                'loaded_symbols': [],
                'missing_symbols': symbols,
                'message': f'Yahoo Finance unavailable. Using sample data ({len(assets)} assets)',
                'warning': 'Using sample data instead of real data'
            })

        loaded = list(assets.keys())
        missing = [s for s in symbols if s not in loaded]

        print(f"\nSuccessfully loaded real data for {len(assets)} symbols")
        return jsonify({
            'success': True,
            'assets': loaded,
            'loaded_symbols': loaded,
            'missing_symbols': missing,
            'message': f'Loaded real data for {len(assets)} assets from Yahoo Finance'
        })

    except Exception as e:
        traceback.print_exc()
        print(f"\nError: {e}")
        try:
            assets = create_sample_assets()
            return jsonify({
                'success': True,
                'assets': list(assets.keys()),
                'loaded_symbols': [],
                'missing_symbols': [],
                'message': f'Error loading real data. Using sample data ({len(assets)} assets)',
                'warning': f'Error: {str(e)}'
            })
        except Exception as inner_e:
            return jsonify({'success': False, 'error': f'Failed to load data: {str(inner_e)}'}), 500


@app.route('/api/backtest', methods=['POST'])
def api_backtest():
    """Run a backtest."""
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        use_real_data = data.get('use_real_data', False)
        symbols = data.get('symbols', [])
        strategy_id = data.get('strategy_id', '')
        strategy_params = data.get('strategy_params', {})
        initial_capital = max(1000, _safe_float(data.get('initial_capital', 100000), 100000))
        num_days = _safe_int(data.get('num_days', 252), 252)

        if not strategy_id:
            return jsonify({'success': False, 'error': 'No strategy selected'}), 400

        assets, _ = _load_assets(symbols, num_days, use_real_data)
        backtester = Backtester(assets)

        strategy_func = _get_strategy_func(strategy_id, strategy_params, assets)
        if not strategy_func:
            return jsonify({'success': False, 'error': 'Invalid strategy'}), 400

        result = backtester.run(
            strategy_func=strategy_func,
            initial_capital=initial_capital,
            strategy_name=f"Strategy: {strategy_id}"
        )

        return jsonify({
            'success': True,
            'result': {
                'strategy_name': result.strategy_name,
                'initial_capital': result.initial_capital,
                'final_value': round(result.final_value, 2),
                'total_return': round(result.total_return * 100, 2),
                'annual_return': round(result.annual_return * 100, 2),
                'max_drawdown': round(result.max_drawdown * 100, 2),
                'sharpe_ratio': round(result.sharpe_ratio, 2),
                'start_date': result.start_date,
                'end_date': result.end_date,
                'snapshots': [
                    {
                        'date': snap.date,
                        'value': round(snap.total_value, 2),
                        'returns': round(snap.returns * 100, 2)
                    }
                    for snap in result.snapshots[::max(1, len(result.snapshots)//50)]
                ]
            }
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/compare', methods=['POST'])
def api_compare():
    """Compare multiple strategies."""
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        use_real_data = data.get('use_real_data', False)
        symbols = data.get('symbols', [])
        strategies = data.get('strategies', [])
        initial_capital = max(1000, _safe_float(data.get('initial_capital', 100000), 100000))
        num_days = _safe_int(data.get('num_days', 252), 252)

        if not strategies:
            return jsonify({'success': False, 'error': 'No strategies provided'}), 400

        assets, _ = _load_assets(symbols, num_days, use_real_data)
        backtester = Backtester(assets)
        results = []
        comparison_rows = []

        for strategy_def in strategies:
            strategy_id = strategy_def.get('strategy_id', '')
            strategy_params = strategy_def.get('params', {})
            strategy_name = strategy_def.get('name', strategy_id)

            strategy_func = _get_strategy_func(strategy_id, strategy_params, assets)
            if not strategy_func:
                continue

            result = backtester.run(
                strategy_func=strategy_func,
                initial_capital=initial_capital,
                strategy_name=strategy_name
            )
            results.append(result)

            sampled_snapshots = result.snapshots[::max(1, len(result.snapshots)//50)]

            comparison_rows.append({
                'name': result.strategy_name,
                'initial': round(result.initial_capital, 2),
                'final': round(result.final_value, 2),
                'return': round(result.total_return * 100, 2),
                'annual': round(result.annual_return * 100, 2),
                'max_dd': round(result.max_drawdown * 100, 2),
                'sharpe': round(result.sharpe_ratio, 2),
                'snapshots': [
                    {
                        'date': snap.date,
                        'value': round(snap.total_value, 2),
                        'returns': round(snap.returns * 100, 2)
                    }
                    for snap in sampled_snapshots
                ]
            })

        if not results:
            return jsonify({'success': False, 'error': 'No successful backtests'}), 500

        return jsonify({
            'success': True,
            'results': comparison_rows,
            'best_return': max(results, key=lambda r: r.total_return).strategy_name,
            'best_sharpe': max(results, key=lambda r: r.sharpe_ratio).strategy_name,
            'best_dd': min(results, key=lambda r: r.max_drawdown).strategy_name
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/default-symbols')
def api_default_symbols():
    """Get default symbols."""
    return jsonify({
        'symbols': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'],
        'descriptions': {
            'AAPL': 'Apple Inc.',
            'MSFT': 'Microsoft Corporation',
            'GOOGL': 'Alphabet (Google)',
            'AMZN': 'Amazon.com Inc.',
            'TSLA': 'Tesla Inc.',
            'BND': 'Bond ETF',
        }
    })


# ============================================================================
# STRATEGY BUILDERS
# ============================================================================

def _get_strategy_func(strategy_id, params, assets):
    """Build strategy function from ID and parameters."""
    try:
        if strategy_id == 'buy_hold_single':
            symbol = params.get('symbol', 'AAPL')
            return Strategies.buy_and_hold(symbol)

        elif strategy_id == 'balanced':
            allocation_json = params.get('allocation_json', '{}')
            allocation = json.loads(allocation_json)
            return Strategies.balanced_portfolio(allocation)

        elif strategy_id == 'momentum':
            short_window = max(5, _safe_int(params.get('short_window', 20), 20))
            long_window = max(short_window + 1, _safe_int(params.get('long_window', 50), 50))
            return Strategies.momentum_strategy(short_window, long_window)

        elif strategy_id == 'rebalance':
            allocation_json = params.get('allocation_json', '{}')
            allocation = json.loads(allocation_json)
            frequency = max(1, _safe_int(params.get('frequency', 63), 63))
            return Strategies.rebalance_strategy(allocation, frequency)

        elif strategy_id == 'rsi_oversold':
            symbol = params.get('symbol', '')
            if not symbol:
                return None
            rsi_period = max(2, _safe_int(params.get('rsi_period', 14), 14))
            oversold_level = max(1, min(99, _safe_int(params.get('oversold_level', 30), 30)))
            allocation = max(0.01, min(1.0, _safe_float(params.get('allocation', 1.0), 1.0)))
            return Strategies.rsi_oversold_strategy(symbol, rsi_period, oversold_level, allocation)

        elif strategy_id == 'macd':
            symbol = params.get('symbol', '')
            if not symbol:
                return None
            fast = max(2, _safe_int(params.get('fast', 12), 12))
            slow = max(fast + 1, _safe_int(params.get('slow', 26), 26))
            signal = max(1, _safe_int(params.get('signal', 9), 9))
            allocation = max(0.01, min(1.0, _safe_float(params.get('allocation', 1.0), 1.0)))
            return Strategies.macd_strategy(symbol, fast, slow, signal, allocation)

        elif strategy_id == 'bollinger':
            symbol = params.get('symbol', '')
            if not symbol:
                return None
            period = max(2, _safe_int(params.get('period', 20), 20))
            num_std = max(0.1, _safe_float(params.get('num_std', 2.0), 2.0))
            allocation = max(0.01, min(1.0, _safe_float(params.get('allocation', 1.0), 1.0)))
            return Strategies.bollinger_bands_strategy(symbol, period, num_std, allocation)

        return None
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Error building strategy {strategy_id}: {e}")
        return None


# ============================================================================
# PORTFOLIO OPTIMIZATION ENDPOINTS
# ============================================================================

@app.route('/api/optimize-portfolio', methods=['POST'])
def api_optimize_portfolio():
    """Optimize portfolio using Modern Portfolio Theory."""
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        symbols = data.get('symbols', [])
        optimization_type = data.get('type', 'sharpe')

        if not symbols:
            return jsonify({'success': False, 'error': 'No symbols provided'}), 400

        assets, _ = _load_assets(symbols, 252, True)

        if len(assets) < 2:
            return jsonify({
                'success': False,
                'error': f'Need at least 2 symbols with data. Got {len(assets)}/{len(symbols)}'
            }), 400

        returns_dict = {}
        for symbol in symbols:
            if symbol in assets:
                returns_dict[symbol] = calculate_returns_from_prices(assets[symbol].price_data.prices)

        if len(returns_dict) < 2:
            return jsonify({'success': False, 'error': 'Insufficient data for optimization'}), 400

        optimizer = PortfolioOptimizer(returns_dict)

        if optimization_type == 'minvar':
            result = optimizer.optimize_min_variance()
        else:
            result = optimizer.optimize_max_sharpe()

        asset_stats = optimizer.get_asset_statistics()
        correlation = optimizer.get_correlation_matrix()

        return jsonify({
            'success': True,
            'weights': result.weights,
            'expected_return': result.expected_return,
            'volatility': result.volatility,
            'sharpe_ratio': result.sharpe_ratio,
            'asset_stats': asset_stats,
            'correlation': correlation,
            'message': f'Optimal portfolio found with Sharpe ratio {result.sharpe_ratio:.2f}'
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/efficient-frontier', methods=['POST'])
def api_efficient_frontier():
    """Calculate efficient frontier for given assets."""
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        symbols = data.get('symbols', [])
        num_points = min(100, max(5, _safe_int(data.get('num_points', 50), 50)))

        if not symbols:
            return jsonify({'success': False, 'error': 'No symbols provided'}), 400

        assets, _ = _load_assets(symbols, 252, True)

        if len(assets) < 2:
            return jsonify({
                'success': False,
                'error': f'Need at least 2 symbols with data'
            }), 400

        returns_dict = {}
        for symbol in symbols:
            if symbol in assets:
                returns_dict[symbol] = calculate_returns_from_prices(assets[symbol].price_data.prices)

        optimizer = PortfolioOptimizer(returns_dict)
        frontier = optimizer.efficient_frontier(num_points=num_points)

        frontier_data = [{'volatility': vol, 'return': ret, 'weights': weights} for vol, ret, weights in frontier]
        max_sharpe = optimizer.optimize_max_sharpe()
        min_var = optimizer.optimize_min_variance()

        return jsonify({
            'success': True,
            'frontier': frontier_data,
            'max_sharpe': {
                'volatility': max_sharpe.volatility,
                'return': max_sharpe.expected_return,
                'weights': max_sharpe.weights,
                'sharpe_ratio': max_sharpe.sharpe_ratio
            },
            'min_variance': {
                'volatility': min_var.volatility,
                'return': min_var.expected_return,
                'weights': min_var.weights,
                'sharpe_ratio': min_var.sharpe_ratio
            },
            'message': f'Efficient frontier with {len(frontier_data)} points calculated'
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/monte-carlo', methods=['POST'])
def api_monte_carlo():
    """Run Monte Carlo simulation on portfolio."""
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        symbols = data.get('symbols', [])
        num_simulations = min(5000, max(100, _safe_int(data.get('num_simulations', 1000), 1000)))
        num_days = max(10, min(1000, _safe_int(data.get('num_days', 252), 252)))
        initial_value = max(100, _safe_float(data.get('initial_value', 100000), 100000))

        if not symbols:
            return jsonify({'success': False, 'error': 'No symbols provided'}), 400

        assets, _ = _load_assets(symbols, num_days + 50, True)

        if len(assets) < len(symbols):
            return jsonify({
                'success': False,
                'error': f'Could not load data for all symbols. Got {len(assets)}/{len(symbols)}'
            }), 500

        returns_dict = {}
        for symbol in symbols:
            if symbol in assets:
                prices = assets[symbol].price_data.prices
                returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
                returns_dict[symbol] = returns

        weights = {symbol: 1.0 / len(symbols) for symbol in symbols}

        simulator = PortfolioMonteCarloSimulator(returns_dict, weights)
        results = simulator.simulate(
            num_simulations=num_simulations,
            days=num_days,
            initial_value=initial_value
        )

        return jsonify(results)

    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/rolling-metrics', methods=['POST'])
def api_rolling_metrics():
    """Calculate rolling Sharpe, returns, and volatility."""
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        snapshots = data.get('snapshots', [])
        window = max(5, min(100, _safe_int(data.get('window', 20), 20)))

        if not snapshots:
            return jsonify({'success': False, 'error': 'No snapshots provided'}), 400

        results = calculate_rolling_metrics(snapshots, window=window)

        return jsonify({
            'success': True,
            'rolling_sharpe': results['rolling_sharpe'],
            'rolling_returns': results['rolling_returns'],
            'rolling_volatility': results['rolling_volatility'],
            'rolling_dates': results['rolling_dates'],
            'window': results['window'],
            'message': f'Calculated rolling metrics with {window}-day window'
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Server error'}), 500


if __name__ == '__main__':
    print("\n" + "="*80)
    print("PORTFOLIOLAB - INVESTMENT BACKTESTER")
    print("="*80)
    print("\nStarting Flask server on http://localhost:5000")
    print("Tip: Use Ctrl+C to stop the server")
    print("="*80 + "\n")

    app.run(debug=False, port=5000, use_reloader=False)
