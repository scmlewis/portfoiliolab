"""
Comprehensive test suite for the investment backtester app
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def test_strategies():
    """Test: Load available strategies"""
    print_section("TEST 1: Load Available Strategies")
    try:
        response = requests.get(f"{BASE_URL}/api/strategies")
        data = response.json()
        
        if data['success']:
            print(f"✓ Successfully loaded {len(data['strategies'])} strategies")
            print(f"  Strategies: {', '.join([s['name'] for s in data['strategies'][:5]])}")
            return True
        else:
            print(f"✗ Failed to load strategies: {data.get('error')}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_symbols_autocomplete():
    """Test: Symbol autocomplete"""
    print_section("TEST 2: Symbol Autocomplete")
    try:
        response = requests.get(f"{BASE_URL}/api/symbols-autocomplete?q=AP")
        data = response.json()
        
        if data['success']:
            symbols = data['symbols'][:10]
            print(f"✓ Found {len(data['symbols'])} symbols starting with 'AP'")
            print(f"  Sample: {', '.join(symbols)}")
            return True
        else:
            print(f"✗ Failed: {data.get('error')}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_validate_symbols():
    """Test: Symbol validation"""
    print_section("TEST 3: Symbol Validation")
    try:
        # Test valid symbols
        response = requests.post(f"{BASE_URL}/api/validate-symbols",
                                json={"symbols": ["AAPL", "MSFT", "GOOGL"]})
        data = response.json()
        
        if data['success']:
            valid = [s for s, v in data['results'].items() if v]
            print(f"✓ Symbol validation successful")
            print(f"  Valid: {', '.join(valid)}")
            return True
        else:
            print(f"✗ Failed: {data.get('error')}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_load_real_data():
    """Test: Load real data from Yahoo Finance"""
    print_section("TEST 4: Load Real Data (Yahoo Finance)")
    try:
        symbols = ["AAPL", "MSFT"]
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
        
        response = requests.post(f"{BASE_URL}/api/load-real-data",
                                json={
                                    "symbols": symbols,
                                    "start_date": start_date,
                                    "end_date": end_date,
                                    "use_real_data": True
                                })
        data = response.json()
        
        if data['success']:
            print(f"✓ Successfully loaded real data")
            print(f"  Symbols loaded: {', '.join(data['loaded_symbols'])}")
            print(f"  Data points per symbol: {data.get('data_points', 'N/A')}")
            return True, data['loaded_symbols']
        else:
            print(f"✗ Failed: {data.get('error')}")
            return False, []
    except Exception as e:
        print(f"✗ Error: {e}")
        return False, []

def test_single_backtest():
    """Test: Run single strategy backtest"""
    print_section("TEST 5: Single Strategy Backtest")
    try:
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=120)).strftime("%Y-%m-%d")
        
        response = requests.post(f"{BASE_URL}/api/backtest",
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
                                })
        data = response.json()
        
        if data['success']:
            result = data['result']
            print(f"✓ Backtest successful!")
            print(f"  Strategy: {result.get('strategy_name')}")
            print(f"  Initial Capital: ${result.get('initial_capital'):,.0f}")
            print(f"  Final Value: ${result.get('final_value'):,.0f}")
            print(f"  Total Return: {result.get('total_return')}%")
            print(f"  Annual Return: {result.get('annual_return')}%")
            print(f"  Sharpe Ratio: {result.get('sharpe_ratio'):.2f}")
            print(f"  Max Drawdown: {result.get('max_drawdown')}%")
            return True
        else:
            print(f"✗ Failed: {data.get('error')}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_multi_strategy_compare():
    """Test: Compare multiple strategies"""
    print_section("TEST 6: Multi-Strategy Comparison")
    try:
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=120)).strftime("%Y-%m-%d")
        
        response = requests.post(f"{BASE_URL}/api/compare",
                                json={
                                    "symbols": ["AAPL", "MSFT"],
                                    "strategies": [
                                        {
                                            "name": "SMA_Crossover",
                                            "params": {
                                                "symbol": "AAPL",
                                                "fast_period": 20,
                                                "slow_period": 50,
                                                "allocation_json": '{"AAPL": 1.0, "MSFT": 0.0}'
                                            }
                                        },
                                        {
                                            "name": "RSI_Oversold",
                                            "params": {
                                                "symbol": "MSFT",
                                                "rsi_period": 14,
                                                "oversold_level": 30,
                                                "allocation_json": '{"AAPL": 0.0, "MSFT": 1.0}'
                                            }
                                        }
                                    ],
                                    "initial_capital": 10000,
                                    "start_date": start_date,
                                    "end_date": end_date,
                                    "num_days": 120
                                })
        data = response.json()
        
        if data['success']:
            print(f"✓ Comparison successful!")
            print(f"  Strategies compared: {len(data['results'])}")
            print(f"  Best return: {data.get('best_return')}%")
            print(f"  Best Sharpe: {data.get('best_sharpe')}")
            for i, result in enumerate(data['results'], 1):
                print(f"    {i}. {result.get('name')}: {result.get('return')}% return")
            return True
        else:
            print(f"✗ Failed: {data.get('error')}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_portfolio_optimization():
    """Test: Portfolio optimization"""
    print_section("TEST 7: Portfolio Optimization")
    try:
        response = requests.post(f"{BASE_URL}/api/optimize-portfolio",
                                json={
                                    "symbols": ["AAPL", "MSFT", "GOOGL"],
                                    "type": "sharpe"
                                })
        data = response.json()
        
        if data['success']:
            print(f"✓ Optimization successful!")
            print(f"  Expected Return: {data.get('expected_return')*100:.2f}%")
            print(f"  Volatility: {data.get('volatility')*100:.2f}%")
            print(f"  Sharpe Ratio: {data.get('sharpe_ratio'):.2f}")
            print(f"  Optimal Weights:")
            for symbol, weight in data.get('weights', {}).items():
                print(f"    {symbol}: {weight*100:.1f}%")
            return True
        else:
            print(f"✗ Failed: {data.get('error')}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_efficient_frontier():
    """Test: Efficient frontier calculation"""
    print_section("TEST 8: Efficient Frontier")
    try:
        response = requests.post(f"{BASE_URL}/api/efficient-frontier",
                                json={
                                    "symbols": ["AAPL", "MSFT", "GOOGL"],
                                    "num_points": 50
                                })
        data = response.json()
        
        if data['success']:
            print(f"✓ Frontier calculation successful!")
            print(f"  Frontier points: {len(data.get('frontier', []))}")
            print(f"  Min Variance Return: {data.get('min_variance', {}).get('expected_return')*100:.2f}%")
            print(f"  Max Sharpe Return: {data.get('max_sharpe', {}).get('expected_return')*100:.2f}%")
            return True
        else:
            print(f"✗ Failed: {data.get('error')}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_error_handling():
    """Test: Error handling with invalid inputs"""
    print_section("TEST 9: Error Handling")
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Invalid symbols
    total_tests += 1
    try:
        response = requests.post(f"{BASE_URL}/api/load-real-data",
                                json={
                                    "symbols": ["INVALID_SYMBOL_XYZ"],
                                    "start_date": "2024-01-01",
                                    "end_date": "2024-12-31",
                                    "use_real_data": True
                                })
        data = response.json()
        if not data['success']:
            print(f"✓ Invalid symbol error caught correctly")
            tests_passed += 1
        else:
            print(f"✗ Should have failed with invalid symbol")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
    
    # Test 2: Empty symbols list
    total_tests += 1
    try:
        response = requests.post(f"{BASE_URL}/api/backtest",
                                json={
                                    "symbols": [],
                                    "strategy": "SMA_Crossover",
                                    "strategy_params": {},
                                    "initial_capital": 10000
                                })
        data = response.json()
        if not data['success']:
            print(f"✓ Empty symbols error caught correctly")
            tests_passed += 1
        else:
            print(f"✗ Should have failed with empty symbols")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
    
    # Test 3: Missing required parameters
    total_tests += 1
    try:
        response = requests.post(f"{BASE_URL}/api/optimize-portfolio",
                                json={"symbols": []})
        data = response.json()
        if not data['success']:
            print(f"✓ Missing parameters error caught correctly")
            tests_passed += 1
        else:
            print(f"✗ Should have failed with missing parameters")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
    
    print(f"  Error handling tests: {tests_passed}/{total_tests} passed")
    return tests_passed == total_tests

def run_all_tests():
    """Run all test cases"""
    print("\n" + "="*70)
    print("  INVESTMENT BACKTESTER - COMPREHENSIVE TEST SUITE")
    print("="*70)
    print(f"  Testing at: {BASE_URL}")
    print(f"  Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Test 1-3: Basic API tests (no data loading needed)
    results.append(("Load Strategies", test_strategies()))
    results.append(("Symbol Autocomplete", test_symbols_autocomplete()))
    results.append(("Symbol Validation", test_validate_symbols()))
    
    # Test 4: Load real data
    success, symbols = test_load_real_data()
    results.append(("Load Real Data", success))
    
    # Test 5-8: Backtesting and optimization (only if data loaded)
    if success:
        results.append(("Single Backtest", test_single_backtest()))
        results.append(("Multi-Strategy Compare", test_multi_strategy_compare()))
        results.append(("Portfolio Optimization", test_portfolio_optimization()))
        results.append(("Efficient Frontier", test_efficient_frontier()))
    else:
        print("\n⚠ Skipping backtest/optimization tests (data load failed)")
        results.append(("Single Backtest", False))
        results.append(("Multi-Strategy Compare", False))
        results.append(("Portfolio Optimization", False))
        results.append(("Efficient Frontier", False))
    
    # Test 9: Error handling
    results.append(("Error Handling", test_error_handling()))
    
    # Summary
    print_section("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\n  Total: {passed}/{total} tests passed ({passed*100//total}%)")
    print(f"  End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
