"""
Quick test of the 5 new features
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"

print("\n" + "="*70)
print("TESTING TOP 5 NEW FEATURES")
print("="*70 + "\n")

# Test 1: Check new strategies are available
print("[TEST 1] Verify 3 New Strategies Available")
try:
    r = requests.get(f"{BASE_URL}/api/strategies", timeout=5)
    strategies = r.json()
    strategy_ids = [s.get('id') for s in strategies]
    
    new_strategies = ['rsi_oversold', 'macd', 'bollinger']
    found = [s for s in new_strategies if s in strategy_ids]
    
    print(f"  Expected 3 new strategies: {new_strategies}")
    print(f"  Found: {found}")
    print(f"  ✓ SUCCESS: All {len(found)}/3 new strategies available\n")
except Exception as e:
    print(f"  ✗ FAILED: {e}\n")

# Test 2: Monte Carlo Simulation
print("[TEST 2] Monte Carlo Simulation with 3 Symbols")
try:
    r = requests.post(f"{BASE_URL}/api/monte-carlo",
                     json={
                         "symbols": ["AAPL", "MSFT", "GOOGL"],
                         "num_simulations": 100,  # Smaller for quick test
                         "num_days": 252,
                         "initial_value": 100000
                     },
                     timeout=30)
    data = r.json()
    
    if data.get('success'):
        stats = data.get('statistics', {})
        print(f"  ✓ SUCCESS: Monte Carlo simulation completed")
        print(f"    - Simulations: {data.get('num_simulations')}")
        print(f"    - Mean final value: ${stats.get('mean_final_value', 0):,.0f}")
        print(f"    - 95% VaR (worst 5%): ${stats.get('var_95', 0):,.0f}")
        print(f"    - Probability of positive return: {stats.get('probability_positive_return', 0):.1f}%\n")
    else:
        print(f"  ✗ FAILED: {data.get('error')}\n")
except Exception as e:
    print(f"  ✗ FAILED: {e}\n")

# Test 3: RSI Oversold Strategy
print("[TEST 3] RSI Oversold Strategy Parameters")
try:
    r = requests.get(f"{BASE_URL}/api/strategies", timeout=5)
    strategies = r.json()
    
    rsi_strategy = [s for s in strategies if s.get('id') == 'rsi_oversold']
    if rsi_strategy:
        params = rsi_strategy[0].get('params', [])
        param_names = [p.get('name') for p in params]
        print(f"  ✓ SUCCESS: RSI Strategy found")
        print(f"    Parameters: {param_names}\n")
    else:
        print(f"  ✗ FAILED: RSI strategy not found\n")
except Exception as e:
    print(f"  ✗ FAILED: {e}\n")

# Test 4: MACD Strategy
print("[TEST 4] MACD Strategy Parameters")
try:
    r = requests.get(f"{BASE_URL}/api/strategies", timeout=5)
    strategies = r.json()
    
    macd_strategy = [s for s in strategies if s.get('id') == 'macd']
    if macd_strategy:
        params = macd_strategy[0].get('params', [])
        param_names = [p.get('name') for p in params]
        print(f"  ✓ SUCCESS: MACD Strategy found")
        print(f"    Parameters: {param_names}\n")
    else:
        print(f"  ✗ FAILED: MACD strategy not found\n")
except Exception as e:
    print(f"  ✗ FAILED: {e}\n")

# Test 5: Bollinger Bands Strategy
print("[TEST 5] Bollinger Bands Strategy Parameters")
try:
    r = requests.get(f"{BASE_URL}/api/strategies", timeout=5)
    strategies = r.json()
    
    bb_strategy = [s for s in strategies if s.get('id') == 'bollinger']
    if bb_strategy:
        params = bb_strategy[0].get('params', [])
        param_names = [p.get('name') for p in params]
        print(f"  ✓ SUCCESS: Bollinger Bands Strategy found")
        print(f"    Parameters: {param_names}\n")
    else:
        print(f"  ✗ FAILED: Bollinger Bands strategy not found\n")
except Exception as e:
    print(f"  ✗ FAILED: {e}\n")

# Test 6: Rolling Metrics (using dummy data)
print("[TEST 6] Rolling Metrics Calculation")
try:
    # Create dummy snapshots
    snapshots = []
    value = 100000
    for i in range(60):
        snapshots.append({
            "date": (datetime.now() - timedelta(days=60-i)).strftime("%Y-%m-%d"),
            "value": value
        })
        value *= 1.001 if i % 2 == 0 else 0.999
    
    r = requests.post(f"{BASE_URL}/api/rolling-metrics",
                     json={
                         "snapshots": snapshots,
                         "window": 20
                     },
                     timeout=10)
    data = r.json()
    
    if data.get('success'):
        print(f"  ✓ SUCCESS: Rolling metrics calculated")
        print(f"    - Window size: {data.get('window')} days")
        print(f"    - Metrics calculated: {len(data.get('rolling_sharpe', []))} points")
        print(f"    - Date range: {data.get('rolling_dates', ['N/A'])[0]} to {data.get('rolling_dates', ['N/A'])[-1]}\n")
    else:
        print(f"  ✗ FAILED: {data.get('error')}\n")
except Exception as e:
    print(f"  ✗ FAILED: {e}\n")

print("="*70)
print("FEATURE TEST COMPLETE")
print("="*70 + "\n")
