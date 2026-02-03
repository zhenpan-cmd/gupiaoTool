#!/usr/bin/env python3
"""
简化版股票分析能力自测用例
"""

import sys
import traceback
import pandas as pd
import numpy as np

def test_basic_imports():
    """测试基本库导入"""
    print("=== 测试基本库导入 ===")
    
    libs_to_test = [
        ('talib', 'TA-Lib'),
        ('ta', 'ta技术分析库'),
        ('akshare', 'AkShare'),
        ('baostock', 'Baostock'),
        ('yfinance', 'YFinance'),
        ('easyquotation', 'EasyQuotation'),
        ('pandas', 'Pandas'),
        ('numpy', 'Numpy'),
        ('scipy', 'Scipy'),
        ('statsmodels', 'Statsmodels')
    ]
    
    results = {}
    for lib, name in libs_to_test:
        try:
            __import__(lib)
            print(f"✓ {name} ({lib}) 导入成功")
            results[lib] = True
        except ImportError as e:
            print(f"✗ {name} ({lib}) 导入失败")
            results[lib] = False
    
    return results

def test_advanced_features():
    """测试高级功能"""
    print("\n=== 测试高级功能 ===")
    
    results = {}
    
    # 测试TA-Lib功能
    try:
        import talib
        import numpy as np
        
        # 创建测试数据
        close_prices = np.array([100, 102, 101, 103, 105, 104, 106, 108, 107, 109] * 10, dtype=float)
        
        # 测试MACD
        try:
            macd, macd_signal, macd_hist = talib.MACD(close_prices)
            print("✓ TA-Lib MACD 计算成功")
            results['talib_macd'] = True
        except Exception as e:
            print(f"✗ TA-Lib MACD 计算失败: {e}")
            results['talib_macd'] = False
            
        # 测试RSI
        try:
            rsi = talib.RSI(close_prices)
            print("✓ TA-Lib RSI 计算成功")
            results['talib_rsi'] = True
        except Exception as e:
            print(f"✗ TA-Lib RSI 计算失败: {e}")
            results['talib_rsi'] = False
            
    except ImportError:
        print("✗ TA-Lib 未安装")
        results['talib_macd'] = False
        results['talib_rsi'] = False
    
    # 测试TA库功能
    try:
        import ta
        import pandas as pd
        import numpy as np
        
        # 创建测试数据
        df = pd.DataFrame({
            'close': [100, 102, 101, 103, 105, 104, 106, 108, 107, 109] * 10
        })
        
        # 测试RSI
        try:
            rsi = ta.momentum.rsi(df['close'], window=14)
            print("✓ TA库 RSI 计算成功")
            results['ta_rsi'] = True
        except Exception as e:
            print(f"✗ TA库 RSI 计算失败: {e}")
            results['ta_rsi'] = False
            
    except ImportError:
        print("✗ TA库 未安装")
        results['ta_rsi'] = False
    
    # 测试可视化库
    try:
        import matplotlib
        print("✓ Matplotlib 导入成功")
        results['matplotlib'] = True
    except ImportError:
        print("✗ Matplotlib 未安装")
        results['matplotlib'] = False
    
    try:
        import seaborn
        print("✓ Seaborn 导入成功")
        results['seaborn'] = True
    except ImportError:
        print("✗ Seaborn 未安装")
        results['seaborn'] = False
    
    try:
        import plotly
        print("✓ Plotly 导入成功")
        results['plotly'] = True
    except ImportError:
        print("✗ Plotly 未安装")
        results['plotly'] = False
    
    # 测试数据获取
    try:
        import easyquotation
        try:
            api = easyquotation.use('sina')
            data = api.real(['002594'])
            if '002594' in data and data['002594']:
                print("✓ EasyQuotation 数据获取成功")
                results['easyquotation'] = True
            else:
                print("✗ EasyQuotation 数据获取返回空值")
                results['easyquotation'] = False
        except Exception as e:
            print(f"✗ EasyQuotation 数据获取失败: {e}")
            results['easyquotation'] = False
    except ImportError:
        print("✗ EasyQuotation 未安装")
        results['easyquotation'] = False
    
    try:
        import akshare as ak
        try:
            stock_data = ak.stock_zh_a_spot_em()
            if not stock_data.empty and len(stock_data) > 0:
                print("✓ AkShare 实时数据获取成功")
                results['akshare_realtime'] = True
            else:
                print("✗ AkShare 实时数据获取返回空值")
                results['akshare_realtime'] = False
        except Exception as e:
            print(f"✗ AkShare 实时数据获取失败: {e}")
            results['akshare_realtime'] = False
    except ImportError:
        print("✗ AkShare 未安装")
        results['akshare_realtime'] = False
    
    # 测试风险管理计算
    try:
        import numpy as np
        returns = np.random.normal(0.001, 0.02, 100)
        
        # 测试VaR
        try:
            var_95 = np.percentile(returns, 5)
            print("✓ VaR 计算成功")
            results['var_calc'] = True
        except Exception as e:
            print(f"✗ VaR 计算失败: {e}")
            results['var_calc'] = False
        
        # 测试夏普比率
        try:
            sharpe = np.mean(returns) / np.std(returns)
            print("✓ 夏普比率计算成功")
            results['sharpe_calc'] = True
        except Exception as e:
            print(f"✗ 夏普比率计算失败: {e}")
            results['sharpe_calc'] = False
            
    except Exception as e:
        print(f"✗ 风险管理计算失败: {e}")
        results['var_calc'] = False
        results['sharpe_calc'] = False
    
    return results

def run_test():
    """运行测试"""
    print("开始执行股票分析能力自测...")
    
    import_results = test_basic_imports()
    feature_results = test_advanced_features()
    
    all_results = {**import_results, **feature_results}
    
    # 输出汇总
    print("\n" + "="*50)
    print("测试结果汇总:")
    print("="*50)
    
    total = len(all_results)
    passed = sum(1 for v in all_results.values() if v)
    
    for name, result in all_results.items():
        status = "PASS" if result else "FAIL"
        print(f"{name:20}: {status}")
    
    print(f"\n总计: {passed}/{total} 通过")
    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"成功率: {success_rate:.1f}%")
    
    if success_rate >= 70:
        print(f"\n🎉 测试完成! 整体成功率 {success_rate:.1f}%, 核心能力基本可用")
        return True
    else:
        print(f"\n⚠️  测试完成! 整体成功率 {success_rate:.1f}%, 部分能力存在问题")
        return False

if __name__ == "__main__":
    try:
        success = run_test()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"测试执行出错: {e}")
        traceback.print_exc()
        sys.exit(1)