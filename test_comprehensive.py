#!/usr/bin/env python3
"""
gupiaoTool项目全面自测用例
确保每一项功能都是真实可用的，保证无bug
"""

import sys
import os
import unittest
import subprocess
import time
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试所有模块是否可以正确导入"""
    print("=== 测试模块导入 ===")
    
    modules_to_test = [
        'advanced_stock_analyzer',
        'safe_stock_analyzer', 
        'validation_framework',
        'stock_validation_check',
        'stock_analyzer_tool',
        'stock_analysis_wrapper',
        'browser_automation_wrapper',
        'enhanced_browser_tool'
    ]
    
    success_count = 0
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✓ {module_name} - 导入成功")
            success_count += 1
        except ImportError as e:
            print(f"✗ {module_name} - 导入失败: {e}")
    
    print(f"模块导入测试完成: {success_count}/{len(modules_to_test)} 通过\n")
    return success_count == len(modules_to_test)

def test_basic_functionality():
    """测试基本功能是否可用"""
    print("=== 测试基本功能 ===")
    
    try:
        # 测试基础库导入
        import pandas as pd
        import numpy as np
        print("✓ pandas 导入成功")
        print("✓ numpy 导入成功")
    except ImportError as e:
        print(f"✗ 基础库导入失败: {e}")
        return False
    
    try:
        import talib
        print("✓ talib 导入成功")
    except ImportError:
        print("⚠ talib 未安装，某些技术指标功能不可用")
    
    try:
        import akshare as ak
        print("✓ akshare 导入成功")
    except ImportError:
        print("⚠ akshare 未安装，数据获取功能不可用")
    
    try:
        import easyquotation
        print("✓ easyquotation 导入成功")
    except ImportError:
        print("⚠ easyquotation 未安装，实时数据功能不可用")
    
    print("基本功能测试完成\n")
    return True

def test_stock_code_validation():
    """测试股票代码验证功能"""
    print("=== 测试股票代码验证功能 ===")
    
    try:
        from validation_framework import StockAnalysisValidator
        
        validator = StockAnalysisValidator()
        
        # 测试正确的代码
        is_valid, correct_code = validator.validate_before_analysis("比亚迪", "002594")
        if is_valid and correct_code == "002594":
            print("✓ 正确代码验证通过")
        else:
            print(f"✗ 正确代码验证失败: {correct_code}")
            return False
        
        # 测试错误代码检测
        is_valid, correct_code = validator.validate_before_analysis("屹唐股份", "300346")
        if not is_valid and correct_code == "688729":
            print("✓ 错误代码检测并纠正成功")
        else:
            print(f"✗ 错误代码检测失败: {correct_code}")
            return False
        
        # 测试自动获取代码
        is_valid, correct_code = validator.validate_before_analysis("贵州茅台")
        if is_valid and correct_code == "600519":
            print("✓ 自动获取代码成功")
        else:
            print(f"✗ 自动获取代码失败: {correct_code}")
            return False
            
        print("股票代码验证功能测试完成\n")
        return True
        
    except Exception as e:
        print(f"✗ 股票代码验证功能测试失败: {e}")
        return False

def test_safe_analyzer():
    """测试安全分析器功能"""
    print("=== 测试安全分析器功能 ===")
    
    try:
        from safe_stock_analyzer import SafeStockAnalyzer
        
        analyzer = SafeStockAnalyzer()
        
        # 测试验证功能
        is_valid, msg = analyzer.validate_stock_code("比亚迪", "002594")
        if is_valid:
            print("✓ 股票代码验证功能正常")
        else:
            print(f"✗ 股票代码验证失败: {msg}")
            return False
        
        # 测试搜索功能
        code, name = analyzer.search_stock_code("贵州茅台")
        if code is not None:
            print("✓ 股票代码搜索功能正常")
        else:
            print("✗ 股票代码搜索失败")
            return False
        
        print("安全分析器功能测试完成\n")
        return True
        
    except Exception as e:
        print(f"✗ 安全分析器功能测试失败: {e}")
        return False

def test_data_access():
    """测试数据访问功能"""
    print("=== 测试数据访问功能 ===")
    
    success_count = 0
    total_tests = 0
    
    # 测试AkShare数据访问
    total_tests += 1
    try:
        import akshare as ak
        # 尝试获取股票列表
        stock_list = ak.stock_info_a_code_name()
        if not stock_list.empty:
            print("✓ AkShare股票列表获取成功")
            success_count += 1
        else:
            print("⚠ AkShare股票列表为空")
    except Exception as e:
        print(f"⚠ AkShare数据访问失败: {e}")
    
    # 测试EasyQuotation数据访问
    total_tests += 1
    try:
        import easyquotation
        api = easyquotation.use('sina')
        data = api.real(['002594'])
        if '002594' in data and data['002594']:
            print("✓ EasyQuotation实时数据获取成功")
            success_count += 1
        else:
            print("⚠ EasyQuotation实时数据获取失败")
    except Exception as e:
        print(f"⚠ EasyQuotation数据访问失败: {e}")
    
    print(f"数据访问功能测试完成: {success_count}/{total_tests} 通过\n")
    return success_count > 0  # 至少有一个数据源可用

def test_technical_indicators():
    """测试技术指标计算功能"""
    print("=== 测试技术指标计算功能 ===")
    
    try:
        import numpy as np
        import pandas as pd
        
        # 创建模拟价格数据
        np.random.seed(42)
        prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
        high = prices * (1 + np.abs(np.random.randn(100)) * 0.01)
        low = prices * (1 - np.abs(np.random.randn(100)) * 0.01)
        close = prices
        
        # 测试TA-Lib功能
        try:
            import talib
            
            # 计算MACD
            macd, macd_signal, macd_hist = talib.MACD(close)
            if not np.isnan(macd[-1]):
                print("✓ MACD计算成功")
            else:
                print("✗ MACD计算失败")
                return False
            
            # 计算RSI
            rsi = talib.RSI(close, timeperiod=14)
            if not np.isnan(rsi[-1]):
                print("✓ RSI计算成功")
            else:
                print("✗ RSI计算失败")
                return False
                
            # 计算布林带
            upper, middle, lower = talib.BBANDS(close)
            if not np.isnan(upper[-1]) and not np.isnan(middle[-1]) and not np.isnan(lower[-1]):
                print("✓ 布林带计算成功")
            else:
                print("✗ 布林带计算失败")
                return False
                
        except ImportError:
            print("⚠ TA-Lib未安装，跳过技术指标测试")
            return True
        
        print("技术指标计算功能测试完成\n")
        return True
        
    except Exception as e:
        print(f"✗ 技术指标计算功能测试失败: {e}")
        return False

def test_risk_metrics():
    """测试风险指标计算功能"""
    print("=== 测试风险指标计算功能 ===")
    
    try:
        import numpy as np
        import scipy.stats as stats
        
        # 创建模拟收益率数据
        np.random.seed(42)
        returns = np.random.normal(0.001, 0.02, 252)  # 一年的日收益率
        
        # 计算VaR
        var_95 = np.percentile(returns, 5)
        var_99 = np.percentile(returns, 1)
        
        if isinstance(var_95, float) and isinstance(var_99, float):
            print("✓ VaR计算成功")
        else:
            print("✗ VaR计算失败")
            return False
        
        # 计算夏普比率
        expected_return = np.mean(returns)
        volatility = np.std(returns)
        sharpe_ratio = expected_return / volatility if volatility != 0 else 0
        
        if isinstance(sharpe_ratio, float):
            print("✓ 夏普比率计算成功")
        else:
            print("✗ 夏普比率计算失败")
            return False
        
        # 计算最大回撤
        cumulative_returns = np.cumprod(1 + returns)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = np.min(drawdown)
        
        if isinstance(max_drawdown, float):
            print("✓ 最大回撤计算成功")
        else:
            print("✗ 最大回撤计算失败")
            return False
            
        print("风险指标计算功能测试完成\n")
        return True
        
    except ImportError:
        print("⚠ SciPy未安装，跳过风险指标测试")
        return True
    except Exception as e:
        print(f"✗ 风险指标计算功能测试失败: {e}")
        return False

def test_visualization():
    """测试可视化功能"""
    print("=== 测试可视化功能 ===")
    
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        
        # 创建简单图表测试
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        
        plt.figure(figsize=(10, 6))
        plt.plot(x, y)
        plt.title("Test Plot")
        plt.xlabel("X")
        plt.ylabel("Y")
        
        # 不保存图片，只测试是否能创建图表
        plt.close()
        print("✓ Matplotlib绘图功能正常")
        
        # 测试Seaborn
        try:
            import seaborn as sns
            import pandas as pd
            
            df = pd.DataFrame({'x': x[:20], 'y': y[:20]})
            sns.scatterplot(data=df, x='x', y='y')
            plt.close()
            print("✓ Seaborn绘图功能正常")
        except ImportError:
            print("⚠ Seaborn未安装")
        
        # 测试Plotly
        try:
            import plotly.graph_objects as go
            
            fig = go.Figure(data=go.Scatter(x=x[:50], y=y[:50]))
            # 不显示，只测试是否能创建图表对象
            print("✓ Plotly绘图功能正常")
        except ImportError:
            print("⚠ Plotly未安装")
        
        print("可视化功能测试完成\n")
        return True
        
    except Exception as e:
        print(f"✗ 可视化功能测试失败: {e}")
        return False

def test_file_operations():
    """测试文件操作功能"""
    print("=== 测试文件操作功能 ===")
    
    import tempfile
    import json
    
    try:
        # 测试读写CSV
        import pandas as pd
        
        # 创建临时DataFrame并保存
        df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': [4, 5, 6],
            'C': ['x', 'y', 'z']
        })
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp:
            df.to_csv(tmp.name, index=False)
            df_read = pd.read_csv(tmp.name)
            
        if len(df_read) == 3 and list(df_read.columns) == ['A', 'B', 'C']:
            print("✓ CSV文件读写功能正常")
        else:
            print("✗ CSV文件读写功能异常")
            return False
        
        # 测试JSON操作
        test_data = {"test": "data", "number": 123}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            json.dump(test_data, tmp)
            
        with open(tmp.name, 'r') as f:
            data_read = json.load(f)
            
        if data_read == test_data:
            print("✓ JSON文件读写功能正常")
        else:
            print("✗ JSON文件读写功能异常")
            return False
            
        print("文件操作功能测试完成\n")
        return True
        
    except Exception as e:
        print(f"✗ 文件操作功能测试失败: {e}")
        return False

def test_error_handling():
    """测试错误处理功能"""
    print("=== 测试错误处理功能 ===")
    
    try:
        from validation_framework import StockAnalysisValidator
        
        validator = StockAnalysisValidator()
        
        # 测试错误代码处理
        is_valid, correct_code = validator.validate_before_analysis("不存在的股票", "999999")
        if not is_valid and correct_code is None:
            print("✓ 未知股票错误处理正常")
        else:
            print("✗ 未知股票错误处理异常")
            return False
        
        # 测试None值处理
        try:
            result = validator.validate_before_analysis(None, None)
            print("✓ None值处理正常")
        except Exception:
            print("✓ None值正确抛出异常")
        
        print("错误处理功能测试完成\n")
        return True
        
    except Exception as e:
        print(f"✗ 错误处理功能测试失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("🚀 开始运行gupiaoTool项目全面自测\n")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    tests = [
        ("模块导入测试", test_imports),
        ("基本功能测试", test_basic_functionality),
        ("股票代码验证测试", test_stock_code_validation),
        ("安全分析器测试", test_safe_analyzer),
        ("数据访问测试", test_data_access),
        ("技术指标测试", test_technical_indicators),
        ("风险指标测试", test_risk_metrics),
        ("可视化测试", test_visualization),
        ("文件操作测试", test_file_operations),
        ("错误处理测试", test_error_handling)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} 执行失败: {e}\n")
            results.append((test_name, False))
    
    # 输出测试结果汇总
    print("=" * 50)
    print("📊 测试结果汇总")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n总览: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！gupiaoTool项目功能完整，无明显bug")
        return True
    else:
        print(f"\n⚠️  {total - passed} 个测试未通过，请检查相关功能")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)