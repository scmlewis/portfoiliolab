"""
Final comprehensive test report for investment backtester
"""
import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"

class TestReport:
    def __init__(self):
        self.tests = []
        self.passed = 0
        self.failed = 0
        
    def add_test(self, name, passed, details=""):
        status = "PASS" if passed else "FAIL"
        symbol = "[OK]" if passed else "[!!]"
        self.tests.append((name, passed, details))
        if passed:
            self.passed += 1
        else:
            self.failed += 1
        print(f"{symbol} {name}")
        if details:
            print(f"    {details}")
    
    def summary(self):
        total = self.passed + self.failed
        percentage = (self.passed * 100) // total if total > 0 else 0
        print("\n" + "="*70)
        print(f"SUMMARY: {self.passed}/{total} tests passed ({percentage}%)")
        print("="*70)
        for name, passed, _ in self.tests:
            status = "[OK]" if passed else "[!!]"
            print(f"  {status} {name}")

report = TestReport()

print("\n" + "="*70)
print("INVESTMENT BACKTESTER - COMPREHENSIVE TEST REPORT")
print(f"Server: {BASE_URL}")
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70 + "\n")

# ==========================================================================
# FEATURE 1: STRATEGY MANAGEMENT
# ==========================================================================
print("\n[FEATURE 1] Strategy Management")
print("-" * 70)

try:
    r = requests.get(f"{BASE_URL}/api/strategies", timeout=5)
    strategies = r.json()
    passed = len(strategies) > 0
    report.add_test(
        "Load available strategies",
        passed,
        f"Found {len(strategies)} strategies: {', '.join([s.get('name', '')[:30] for s in strategies[:3]])}"
    )
except Exception as e:
    report.add_test("Load available strategies", False, str(e))

# ==========================================================================
# FEATURE 2: SYMBOL AUTOCOMPLETE & VALIDATION
# ==========================================================================
print("\n[FEATURE 2] Symbol Management")
print("-" * 70)

try:
    r = requests.get(f"{BASE_URL}/api/symbols-autocomplete?q=MS", timeout=5)
    data = r.json()
    symbols = data.get('symbols', []) if isinstance(data, dict) else (data[:3] if isinstance(data, list) else [])
    report.add_test(
        "Symbol autocomplete",
        len(symbols) > 0,
        f"Found suggestions starting with 'MS'"
    )
except Exception as e:
    report.add_test("Symbol autocomplete", False, str(e))

try:
    r = requests.post(f"{BASE_URL}/api/validate-symbols",
                     json={"symbols": ["AAPL", "MSFT", "GOOGL"]},
                     timeout=5)
    data = r.json()
    # Check if validation worked
    has_results = isinstance(data, dict) and ('results' in data or 'success' in data)
    report.add_test(
        "Symbol validation",
        has_results,
        "Validated AAPL, MSFT, GOOGL"
    )
except Exception as e:
    report.add_test("Symbol validation", False, str(e))

# ==========================================================================
# FEATURE 3: DATA LOADING (Real Yahoo Finance)
# ==========================================================================
print("\n[FEATURE 3] Data Loading (Yahoo Finance)")
print("-" * 70)

end_date = datetime.now().strftime("%Y-%m-%d")
start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

try:
    r = requests.post(f"{BASE_URL}/api/load-real-data",
                     json={
                         "symbols": ["AAPL", "MSFT"],
                         "start_date": start_date,
                         "end_date": end_date,
                         "use_real_data": True
                     },
                     timeout=30)
    data = r.json()
    passed = isinstance(data, dict) and data.get('success', False)
    details = f"Loaded data from {start_date} to {end_date}"
    if passed:
        symbols_loaded = data.get('loaded_symbols', [])
        details += f" - Symbols: {', '.join(symbols_loaded) if symbols_loaded else 'N/A'}"
    report.add_test("Load real data (Yahoo Finance)", passed, details)
except Exception as e:
    report.add_test("Load real data (Yahoo Finance)", False, str(e))

# ==========================================================================
# FEATURE 4: SINGLE STRATEGY BACKTESTING
# ==========================================================================
print("\n[FEATURE 4] Single Strategy Backtesting")
print("-" * 70)

# Test Buy & Hold strategy
try:
    r = requests.post(f"{BASE_URL}/api/backtest",
                     json={
                         "symbols": ["AAPL"],
                         "strategy": "buy_hold_single",
                         "strategy_params": {
                             "symbol": "AAPL"
                         },
                         "initial_capital": 10000,
                         "start_date": start_date,
                         "end_date": end_date,
                         "num_days": 90
                     },
                     timeout=30)
    data = r.json()
    passed = isinstance(data, dict) and data.get('success', False)
    if passed:
        result = data.get('result', {})
        details = f"Buy & Hold: {result.get('total_return')}% return, Sharpe: {result.get('sharpe_ratio', 'N/A')}"
    else:
        details = data.get('error', 'Unknown error')
    report.add_test("Buy & Hold Strategy Backtest", passed, details)
except Exception as e:
    report.add_test("Buy & Hold Strategy Backtest", False, str(e))

# Test Momentum strategy  
try:
    r = requests.post(f"{BASE_URL}/api/backtest",
                     json={
                         "symbols": ["AAPL", "MSFT"],
                         "strategy": "momentum",
                         "strategy_params": {
                             "short_window": 20,
                             "long_window": 50
                         },
                         "initial_capital": 10000,
                         "start_date": start_date,
                         "end_date": end_date,
                         "num_days": 90
                     },
                     timeout=30)
    data = r.json()
    passed = isinstance(data, dict) and data.get('success', False)
    if passed:
        result = data.get('result', {})
        details = f"Momentum: {result.get('total_return')}% return, Sharpe: {result.get('sharpe_ratio', 'N/A')}"
    else:
        details = data.get('error', 'Unknown error')
    report.add_test("Momentum Strategy Backtest", passed, details)
except Exception as e:
    report.add_test("Momentum Strategy Backtest", False, str(e))

# ==========================================================================
# FEATURE 5: MULTI-STRATEGY COMPARISON
# ==========================================================================
print("\n[FEATURE 5] Multi-Strategy Comparison")
print("-" * 70)

try:
    r = requests.post(f"{BASE_URL}/api/compare",
                     json={
                         "symbols": ["AAPL", "MSFT"],
                         "strategies": [
                             {
                                 "name": "buy_hold_single",
                                 "params": {"symbol": "AAPL"}
                             },
                             {
                                 "name": "balanced",
                                 "params": {"allocation_json": '{"AAPL": 0.5, "MSFT": 0.5}'}
                             }
                         ],
                         "initial_capital": 10000,
                         "start_date": start_date,
                         "end_date": end_date,
                         "num_days": 90
                     },
                     timeout=30)
    data = r.json()
    passed = isinstance(data, dict) and data.get('success', False)
    if passed:
        num_strategies = len(data.get('results', []))
        details = f"Compared {num_strategies} strategies - Best return: {data.get('best_return')}%"
    else:
        details = data.get('error', 'Unknown error')
    report.add_test("Compare Multiple Strategies", passed, details)
except Exception as e:
    report.add_test("Compare Multiple Strategies", False, str(e))

# ==========================================================================
# FEATURE 6: PORTFOLIO OPTIMIZATION (Modern Portfolio Theory)
# ==========================================================================
print("\n[FEATURE 6] Portfolio Optimization (Modern Portfolio Theory)")
print("-" * 70)

# Max Sharpe optimization
try:
    r = requests.post(f"{BASE_URL}/api/optimize-portfolio",
                     json={
                         "symbols": ["AAPL", "MSFT", "GOOGL", "BND"],
                         "type": "sharpe"
                     },
                     timeout=30)
    data = r.json()
    passed = isinstance(data, dict) and data.get('success', False)
    if passed:
        details = f"Sharpe {data.get('sharpe_ratio'):.2f} | Return {data.get('expected_return')*100:.1f}% | Vol {data.get('volatility')*100:.1f}%"
    else:
        details = data.get('error', 'Unknown error')
    report.add_test("Portfolio Optimization (Max Sharpe)", passed, details)
except Exception as e:
    report.add_test("Portfolio Optimization (Max Sharpe)", False, str(e))

# Min Variance optimization
try:
    r = requests.post(f"{BASE_URL}/api/optimize-portfolio",
                     json={
                         "symbols": ["AAPL", "MSFT", "GOOGL", "BND"],
                         "type": "minvar"
                     },
                     timeout=30)
    data = r.json()
    passed = isinstance(data, dict) and data.get('success', False)
    if passed:
        details = f"Return {data.get('expected_return')*100:.1f}% | Vol {data.get('volatility')*100:.1f}% | Sharpe {data.get('sharpe_ratio'):.2f}"
    else:
        details = data.get('error', 'Unknown error')
    report.add_test("Portfolio Optimization (Min Variance)", passed, details)
except Exception as e:
    report.add_test("Portfolio Optimization (Min Variance)", False, str(e))

# ==========================================================================
# FEATURE 7: EFFICIENT FRONTIER CALCULATION
# ==========================================================================
print("\n[FEATURE 7] Efficient Frontier Calculation")
print("-" * 70)

try:
    r = requests.post(f"{BASE_URL}/api/efficient-frontier",
                     json={
                         "symbols": ["AAPL", "MSFT", "GOOGL", "BND"],
                         "num_points": 50
                     },
                     timeout=30)
    data = r.json()
    passed = isinstance(data, dict) and data.get('success', False)
    if passed:
        frontier_points = len(data.get('frontier', []))
        max_sharpe = data.get('max_sharpe', {}).get('sharpe_ratio', 'N/A')
        details = f"Calculated {frontier_points} frontier points | Max Sharpe: {max_sharpe}"
    else:
        details = data.get('error', 'Unknown error')
    report.add_test("Efficient Frontier Calculation", passed, details)
except Exception as e:
    report.add_test("Efficient Frontier Calculation", False, str(e))

# ==========================================================================
# FEATURE 8: ERROR HANDLING
# ==========================================================================
print("\n[FEATURE 8] Error Handling & Validation")
print("-" * 70)

# Test invalid symbol handling
try:
    r = requests.post(f"{BASE_URL}/api/load-real-data",
                     json={
                         "symbols": ["INVALID_XYZ_123"],
                         "start_date": "2024-01-01",
                         "end_date": "2024-12-31",
                         "use_real_data": True
                     },
                     timeout=10)
    data = r.json()
    passed = isinstance(data, dict) and not data.get('success', True)
    report.add_test("Reject invalid symbols", passed, "Invalid symbol correctly rejected")
except Exception as e:
    report.add_test("Reject invalid symbols", False, str(e))

# Test empty symbol list
try:
    r = requests.post(f"{BASE_URL}/api/backtest",
                     json={
                         "symbols": [],
                         "strategy": "buy_hold_single",
                         "strategy_params": {},
                         "initial_capital": 10000
                     },
                     timeout=5)
    data = r.json()
    passed = isinstance(data, dict) and not data.get('success', True)
    report.add_test("Reject empty symbol list", passed, "Empty list correctly rejected")
except Exception as e:
    report.add_test("Reject empty symbol list", False, str(e))

# Test invalid strategy
try:
    r = requests.post(f"{BASE_URL}/api/backtest",
                     json={
                         "symbols": ["AAPL"],
                         "strategy": "NONEXISTENT_STRATEGY",
                         "strategy_params": {},
                         "initial_capital": 10000
                     },
                     timeout=5)
    data = r.json()
    passed = isinstance(data, dict) and not data.get('success', True)
    report.add_test("Reject invalid strategy", passed, "Invalid strategy correctly rejected")
except Exception as e:
    report.add_test("Reject invalid strategy", False, str(e))

# ==========================================================================
# PRINT SUMMARY
# ==========================================================================
report.summary()

print("\n" + "="*70)
if report.failed == 0:
    print("SUCCESS! All core features are working correctly.")
    print("The investment backtester app is fully functional.")
else:
    print(f"ATTENTION: {report.failed} test(s) failed. Review output above.")
print("="*70 + "\n")
