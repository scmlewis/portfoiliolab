"""
Manual test to validate app functionality by interacting with actual API
"""
import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"

print("\n" + "="*70)
print("INVESTMENT BACKTESTER - FUNCTIONALITY TEST")
print("="*70 + "\n")

# Test 1: Load strategies
print("[TEST 1] Loading available strategies...")
try:
    r = requests.get(f"{BASE_URL}/api/strategies", timeout=5)
    strategies = r.json()
    print(f"  SUCCESS: Loaded {len(strategies)} strategies")
    for s in strategies[:3]:
        print(f"    - {s.get('name', 'Unknown')}")
except Exception as e:
    print(f"  FAILED: {e}")

# Test 2: Symbol autocomplete
print("\n[TEST 2] Testing symbol autocomplete (query='AP')...")
try:
    r = requests.get(f"{BASE_URL}/api/symbols-autocomplete?q=AP", timeout=5)
    data = r.json()
    if isinstance(data, dict) and 'symbols' in data:
        symbols = data['symbols'][:5]
    else:
        symbols = data[:5] if isinstance(data, list) else []
    print(f"  SUCCESS: Found suggestions")
    print(f"    {', '.join(symbols)}")
except Exception as e:
    print(f"  FAILED: {e}")

# Test 3: Load real data
print("\n[TEST 3] Loading real data (AAPL, MSFT - 60 days)...")
try:
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
    
    r = requests.post(f"{BASE_URL}/api/load-real-data",
                     json={
                         "symbols": ["AAPL", "MSFT"],
                         "start_date": start_date,
                         "end_date": end_date,
                         "use_real_data": True
                     },
                     timeout=30)
    data = r.json()
    
    # Check if response is successful
    if isinstance(data, dict):
        if data.get('success'):
            print(f"  SUCCESS: Data loaded")
            print(f"    Symbols: {', '.join(data.get('loaded_symbols', []))}")
            print(f"    Date range: {start_date} to {end_date}")
        else:
            print(f"  PARTIAL: {data}")
    else:
        print(f"  RESPONSE: {data}")
except Exception as e:
    print(f"  FAILED: {e}")

# Test 4: Single backtest
print("\n[TEST 4] Running single strategy backtest (SMA Crossover on AAPL)...")
try:
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=120)).strftime("%Y-%m-%d")
    
    r = requests.post(f"{BASE_URL}/api/backtest",
                     json={
                         "symbols": ["AAPL"],
                         "strategy": "SMA_Crossover",
                         "strategy_params": {
                             "symbol": "AAPL",
                             "fast_period": 20,
                             "slow_period": 50,
                             "allocation_json": '{"AAPL": 1.0}'
                         },
                         "initial_capital": 10000,
                         "start_date": start_date,
                         "end_date": end_date,
                         "num_days": 120
                     },
                     timeout=30)
    data = r.json()
    
    if isinstance(data, dict):
        if data.get('success'):
            result = data.get('result', {})
            print(f"  SUCCESS: Backtest completed")
            print(f"    Return: {result.get('total_return')}%")
            print(f"    Sharpe Ratio: {result.get('sharpe_ratio', 'N/A')}")
            print(f"    Max Drawdown: {result.get('max_drawdown')}%")
        else:
            print(f"  ERROR: {data.get('error', 'Unknown error')}")
    else:
        print(f"  RESPONSE: {type(data)} {str(data)[:100]}")
except Exception as e:
    print(f"  FAILED: {e}")

# Test 5: Portfolio optimization
print("\n[TEST 5] Running portfolio optimization (3 symbols)...")
try:
    r = requests.post(f"{BASE_URL}/api/optimize-portfolio",
                     json={
                         "symbols": ["AAPL", "MSFT", "GOOGL"],
                         "type": "sharpe"
                     },
                     timeout=30)
    data = r.json()
    
    if isinstance(data, dict):
        if data.get('success'):
            print(f"  SUCCESS: Optimization completed")
            print(f"    Expected Return: {data.get('expected_return')*100:.2f}%")
            print(f"    Volatility: {data.get('volatility')*100:.2f}%")
            print(f"    Sharpe Ratio: {data.get('sharpe_ratio'):.2f}")
        else:
            print(f"  ERROR: {data.get('error', 'Unknown error')}")
    else:
        print(f"  RESPONSE: {type(data)} {str(data)[:100]}")
except Exception as e:
    print(f"  FAILED: {e}")

# Test 6: Efficient frontier
print("\n[TEST 6] Calculating efficient frontier...")
try:
    r = requests.post(f"{BASE_URL}/api/efficient-frontier",
                     json={
                         "symbols": ["AAPL", "MSFT", "GOOGL"],
                         "num_points": 50
                     },
                     timeout=30)
    data = r.json()
    
    if isinstance(data, dict):
        if data.get('success'):
            frontier_points = len(data.get('frontier', []))
            print(f"  SUCCESS: Frontier calculated")
            print(f"    Points: {frontier_points}")
            print(f"    Max Sharpe: {data.get('max_sharpe', {}).get('sharpe_ratio', 'N/A')}")
        else:
            print(f"  ERROR: {data.get('error', 'Unknown error')}")
    else:
        print(f"  RESPONSE: {type(data)} {str(data)[:100]}")
except Exception as e:
    print(f"  FAILED: {e}")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70 + "\n")
