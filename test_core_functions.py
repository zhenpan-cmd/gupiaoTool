#!/usr/bin/env python3
"""
gupiaoTool核心功能验证脚本
逐步验证关键功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_module_imports():
    """测试核心模块导入"""
    print("Testing module imports...")
    
    modules = [
        'validation_framework',
        'safe_stock_analyzer',
        'advanced_stock_analyzer'
    ]
    
    for module_name in modules:
        try:
            __import__(module_name)
            print(f"✓ {module_name} imported successfully")
        except ImportError as e:
            print(f"✗ Failed to import {module_name}: {e}")
            return False
    
    return True

def test_stock_validator():
    """测试股票验证器"""
    print("\nTesting stock validator...")
    
    try:
        from validation_framework import StockAnalysisValidator
        
        validator = StockAnalysisValidator()
        
        # 测试已知股票
        is_valid, code = validator.validate_before_analysis("比亚迪", "002594")
        if is_valid and code == "002594":
            print("✓ Stock validator works correctly")
        else:
            print(f"✗ Stock validator failed: valid={is_valid}, code={code}")
            return False
        
        # 测试错误代码检测
        is_valid, correct_code = validator.validate_before_analysis("屹唐股份", "300346")
        if not is_valid and correct_code == "688729":
            print("✓ Error code detection works correctly")
        else:
            print(f"✗ Error code detection failed: valid={is_valid}, correct_code={correct_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Stock validator test failed: {e}")
        return False

def test_safe_analyzer():
    """测试安全分析器"""
    print("\nTesting safe analyzer...")
    
    try:
        from safe_stock_analyzer import SafeStockAnalyzer
        
        analyzer = SafeStockAnalyzer()
        
        # 测试代码验证
        is_valid, msg = analyzer.validate_stock_code("比亚迪", "002594")
        if is_valid:
            print("✓ Safe analyzer code validation works")
        else:
            print(f"✗ Safe analyzer code validation failed: {msg}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Safe analyzer test failed: {e}")
        return False

def test_basic_libs():
    """测试基础库"""
    print("\nTesting basic libraries...")
    
    libs = [
        ('pandas', 'pd'),
        ('numpy', 'np'),
        ('akshare', 'ak'),
        ('easyquotation', 'eq')
    ]
    
    for lib_name, alias in libs:
        try:
            lib = __import__(lib_name)
            print(f"✓ {lib_name} imported successfully")
        except ImportError:
            print(f"⚠ {lib_name} not available")
    
    return True

def test_technical_analysis():
    """测试技术分析功能"""
    print("\nTesting technical analysis functions...")
    
    try:
        import numpy as np
        
        # 创建模拟数据
        prices = np.array([100, 102, 101, 103, 105, 104, 106, 108, 107, 109])
        
        # 测试talib（如果可用）
        try:
            import talib
            rsi = talib.RSI(prices, timeperiod=5)
            if len(rsi) > 0 and not np.isnan(rsi[-1]):
                print("✓ TA-Lib technical indicators work")
            else:
                print("⚠ TA-Lib RSI calculation returned NaN")
        except ImportError:
            print("⚠ TA-Lib not installed")
        
        return True
        
    except Exception as e:
        print(f"✗ Technical analysis test failed: {e}")
        return False

def test_risk_calculations():
    """测试风险计算功能"""
    print("\nTesting risk calculations...")
    
    try:
        import numpy as np
        
        # 创建模拟收益率数据
        returns = np.array([-0.02, 0.01, -0.01, 0.03, -0.005, 0.02, -0.015, 0.01, 0.005, -0.002])
        
        # 计算VaR
        var_95 = np.percentile(returns, 5)
        print(f"✓ VaR calculation works: {var_95:.4f}")
        
        # 计算波动率
        volatility = np.std(returns)
        print(f"✓ Volatility calculation works: {volatility:.4f}")
        
        return True
        
    except Exception as e:
        print(f"✗ Risk calculations test failed: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 Running gupiaoTool Core Functions Test")
    print("="*50)
    
    tests = [
        ("Module Imports", test_module_imports),
        ("Stock Validator", test_stock_validator),
        ("Safe Analyzer", test_safe_analyzer),
        ("Basic Libraries", test_basic_libs),
        ("Technical Analysis", test_technical_analysis),
        ("Risk Calculations", test_risk_calculations)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "="*50)
    print("📊 TEST RESULTS SUMMARY")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All core functions are working properly!")
        return True
    else:
        print(f"\n⚠️  {total - passed} tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)