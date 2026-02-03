#!/usr/bin/env python3
"""
股票分析能力自测用例
测试所有已声明的股票分析能力
"""

import sys
import traceback
import pandas as pd
import numpy as np

def test_imports():
    """测试所有依赖库是否正确导入"""
    print("=== 测试依赖库导入 ===")
    libraries = [
        # 技术分析
        ('talib', 'TA-Lib'),
        ('ta', 'ta技术分析库'),
        # 数据获取
        ('akshare', 'AkShare'),
        ('baostock', 'Baostock'),
        ('yfinance', 'YFinance'),
        ('easyquotation', 'EasyQuotation'),
        # 可视化
        ('matplotlib', 'Matplotlib'),
        ('seaborn', 'Seaborn'),
        ('plotly', 'Plotly'),
        # 数据处理
        ('pandas', 'Pandas'),
        ('numpy', 'Numpy'),
        ('scipy', 'Scipy'),
        ('statsmodels', 'Statsmodels')
    ]
    
    results = {}
    for lib, name in libraries:
        try:
            if '.' in lib:
                parts = lib.split('.')
                module = __import__(parts[0])
                for part in parts[1:]:
                    module = getattr(module, part)
            else:
                __import__(lib)
            print(f"✓ {name} ({lib}) 导入成功")
            results[lib] = True
        except ImportError as e:
            print(f"✗ {name} ({lib}) 导入失败: {e}")
            results[lib] = False
    
    return results

def test_technical_indicators():
    """测试技术指标计算能力"""
    print("\n=== 测试技术指标计算 ===")
    results = {}
    
    try:
        import talib
        import numpy as np
        
        # 创建模拟数据
        close_prices = np.array([100, 102, 101, 103, 105, 104, 106, 108, 107, 109] * 10, dtype=float)
        high_prices = close_prices + np.random.rand(len(close_prices)) * 2
        low_prices = close_prices - np.random.rand(len(close_prices)) * 2
        open_prices = close_prices - np.random.rand(len(close_prices))
        
        # 测试MACD
        try:
            macd, macd_signal, macd_hist = talib.MACD(close_prices)
            print("✓ MACD 计算成功")
            results['MACD'] = True
        except Exception as e:
            print(f"✗ MACD 计算失败: {e}")
            results['MACD'] = False
        
        # 测试布林带
        try:
            upper, middle, lower = talib.BBANDS(close_prices)
            print("✓ 布林带 计算成功")
            results['Bollinger Bands'] = True
        except Exception as e:
            print(f"✗ 布林带 计算失败: {e}")
            results['Bollinger Bands'] = False
        
        # 测试KDJ
        try:
            k, d = talib.STOCH(high_prices, low_prices, close_prices)
            print("✓ KDJ 计算成功")
            results['KDJ'] = True
        except Exception as e:
            print(f"✗ KDJ 计算失败: {e}")
            results['KDJ'] = False
        
        # 测试RSI
        try:
            rsi = talib.RSI(close_prices)
            print("✓ RSI 计算成功")
            results['RSI'] = True
        except Exception as e:
            print(f"✗ RSI 计算失败: {e}")
            results['RSI'] = False
        
        # 测试威廉指标
        try:
            wr = talib.WILLR(high_prices, low_prices, close_prices)
            print("✓ 威廉指标 计算成功")
            results['Williams %R'] = True
        except Exception as e:
            print(f"✗ 威廉指标 计算失败: {e}")
            results['Williams %R'] = False
            
    except ImportError:
        print("✗ TA-Lib 未安装，跳过技术指标测试")
        results = {k: False for k in ['MACD', 'Bollinger Bands', 'KDJ', 'RSI', 'Williams %R']}
    
    return results

def test_visualization():
    """测试可视化能力"""
    print("\n=== 测试可视化能力 ===")
    results = {}
    
    try:
        from matplotlib import pyplot as plt
        import numpy as np
        
        # 测试matplotlib
        try:
            fig, ax = plt.subplots(figsize=(8, 6))
            x = np.linspace(0, 10, 100)
            y = np.sin(x)
            ax.plot(x, y)
            ax.set_title("Test Plot")
            plt.close(fig)  # 关闭图形以释放内存
            print("✓ Matplotlib 绘图成功")
            results['Matplotlib'] = True
        except Exception as e:
            print(f"✗ Matplotlib 绘图失败: {e}")
            results['Matplotlib'] = False
            
    except ImportError:
        print("✗ Matplotlib 未安装")
        results['Matplotlib'] = False
    
    try:
        import seaborn as sns
        import pandas as pd
        import numpy as np
        
        # 测试seaborn
        try:
            data = pd.DataFrame({
                'x': np.random.randn(100),
                'y': np.random.randn(100)
            })
            fig = sns.scatterplot(data=data, x='x', y='y')
            del fig  # 删除图形引用
            print("✓ Seaborn 绘图成功")
            results['Seaborn'] = True
        except Exception as e:
            print(f"✗ Seaborn 绘图失败: {e}")
            results['Seaborn'] = False
            
    except ImportError:
        print("✗ Seaborn 未安装")
        results['Seaborn'] = False
    
    try:
        import plotly.graph_objects as go
        
        # 测试plotly
        try:
            fig = go.Figure(data=go.Bar(x=['A', 'B', 'C'], y=[1, 3, 2]))
            del fig  # 删除图形引用
            print("✓ Plotly 绘图成功")
            results['Plotly'] = True
        except Exception as e:
            print(f"✗ Plotly 绘图失败: {e}")
            results['Plotly'] = False
            
    except ImportError:
        print("✗ Plotly 未安装")
        results['Plotly'] = False
    
    return results

def test_data_acquisition():
    """测试数据获取能力"""
    print("\n=== 测试数据获取能力 ===")
    results = {}
    
    # 测试EasyQuotation
    try:
        import easyquotation
        try:
            api = easyquotation.use('sina')
            data = api.real(['002594'])
            if '002594' in data and data['002594']:
                print("✓ EasyQuotation (新浪) 数据获取成功")
                results['EasyQuotation_Sina'] = True
            else:
                print("✗ EasyQuotation (新浪) 数据获取返回空值")
                results['EasyQuotation_Sina'] = False
        except Exception as e:
            print(f"✗ EasyQuotation (新浪) 数据获取失败: {e}")
            results['EasyQuotation_Sina'] = False
    except ImportError:
        print("✗ EasyQuotation 未安装")
        results['EasyQuotation_Sina'] = False
    
    # 测试YFinance
    try:
        import yfinance as yf
        try:
            ticker = yf.Ticker('AAPL')
            info = ticker.info
            if info and 'symbol' in info:
                print("✓ YFinance 数据获取成功")
                results['YFinance'] = True
            else:
                print("✗ YFinance 数据获取返回空值")
                results['YFinance'] = False
        except Exception as e:
            print(f"✗ YFinance 数据获取失败: {e}")
            results['YFinance'] = False
    except ImportError:
        print("✗ YFinance 未安装")
        results['YFinance'] = False
    
    # 测试AkShare
    try:
        import akshare as ak
        try:
            # 测试获取实时数据
            stock_data = ak.stock_zh_a_spot_em()
            if not stock_data.empty and len(stock_data) > 0:
                print("✓ AkShare 实时数据获取成功")
                results['AkShare_Realtime'] = True
            else:
                print("✗ AkShare 实时数据获取返回空值")
                results['AkShare_Realtime'] = False
        except Exception as e:
            print(f"✗ AkShare 实时数据获取失败: {e}")
            results['AkShare_Realtime'] = False
    except ImportError:
        print("✗ AkShare 未安装")
        results['AkShare_Realtime'] = False
    
    # 测试Baostock
    try:
        import baostock as bs
        try:
            lg = bs.login()
            if lg.error_msg == 'success':
                rs = bs.query_history_k_data_plus('sh.000001', 'date,close', start_date='2025-01-01', end_date='2025-01-10', frequency='d', adjustflag='3')
                data = rs.get_data()
                if not data.empty and len(data) > 0:
                    print("✓ Baostock 数据获取成功")
                    bs.logout()
                    results['Baostock'] = True
                else:
                    print("✗ Baostock 数据获取返回空值")
                    bs.logout()
                    results['Baostock'] = False
            else:
                print(f"✗ Baostock 登录失败: {lg.error_msg}")
                results['Baostock'] = False
        except Exception as e:
            print(f"✗ Baostock 数据获取失败: {e}")
            try:
                bs.logout()
            except:
                pass
            results['Baostock'] = False
    except ImportError:
        print("✗ Baostock 未安装")
        results['Baostock'] = False
    
    return results

def test_fundamental_analysis():
    """测试基本面分析能力"""
    print("\n=== 测试基本面分析能力 ===")
    results = {}
    
    try:
        import akshare as ak
        
        # 测试财务指标获取
        try:
            fin_indicator = ak.stock_financial_abstract_ths(symbol='002594')
            if not fin_indicator.empty:
                latest_fin = fin_indicator.iloc[-1]
                print("✓ 财务指标获取成功")
                results['Financial_Indicators'] = True
            else:
                print("✗ 财务指标获取返回空值")
                results['Financial_Indicators'] = False
        except Exception as e:
            print(f"✗ 财务指标获取失败: {e}")
            results['Financial_Indicators'] = False
        
        # 测试财务报表获取
        try:
            balance_sheet = ak.stock_financial_report_sina(stock='002594', symbol='资产负债表')
            if not balance_sheet.empty:
                print("✓ 资产负债表获取成功")
                results['Balance_Sheet'] = True
            else:
                print("✗ 资产负债表获取返回空值")
                results['Balance_Sheet'] = False
        except Exception as e:
            print(f"✗ 资产负债表获取失败: {e}")
            results['Balance_Sheet'] = False
        
        try:
            income_statement = ak.stock_financial_report_sina(stock='002594', symbol='利润表')
            if not income_statement.empty:
                print("✓ 利润表获取成功")
                results['Income_Statement'] = True
            else:
                print("✗ 利润表获取返回空值")
                results['Income_Statement'] = False
        except Exception as e:
            print(f"✗ 利润表获取失败: {e}")
            results['Income_Statement'] = False
            
    except ImportError:
        print("✗ AkShare 未安装，跳过基本面分析测试")
        results = {k: False for k in ['Financial_Indicators', 'Balance_Sheet', 'Income_Statement']}
    
    return results

def test_risk_management():
    """测试风险管理能力"""
    print("\n=== 测试风险管理能力 ===")
    results = {}
    
    try:
        import numpy as np
        import scipy.stats as stats
        
        # 生成模拟价格数据
        np.random.seed(42)
        returns = np.random.normal(0.001, 0.02, 252)  # 一年的日收益率
        
        # 测试VaR计算
        try:
            var_95 = np.percentile(returns, 5)
            var_99 = np.percentile(returns, 1)
            print("✓ VaR 计算成功")
            results['VaR'] = True
        except Exception as e:
            print(f"✗ VaR 计算失败: {e}")
            results['VaR'] = False
        
        # 测试夏普比率计算
        try:
            risk_free_rate = 0.03 / 252  # 日无风险利率
            sharpe_ratio = (np.mean(returns) - risk_free_rate) / np.std(returns)
            print("✓ 夏普比率计算成功")
            results['Sharpe_Ratio'] = True
        except Exception as e:
            print(f"✗ 夏普比率计算失败: {e}")
            results['Sharpe_Ratio'] = False
        
        # 测试最大回撤计算
        try:
            cumulative_returns = np.cumprod(1 + returns)
            running_max = np.maximum.accumulate(cumulative_returns)
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = np.min(drawdown)
            print("✓ 最大回撤计算成功")
            results['Max_Drawdown'] = True
        except Exception as e:
            print(f"✗ 最大回撤计算失败: {e}")
            results['Max_Drawdown'] = False
            
    except ImportError:
        print("✗ SciPy 未安装，跳过风险管理测试")
        results = {k: False for k in ['VaR', 'Sharpe_Ratio', 'Max_Drawdown']}
    
    return results

def run_all_tests():
    """运行所有测试"""
    print("开始执行股票分析能力自测...")
    
    all_results = {}
    
    all_results['imports'] = test_imports()
    all_results['technical'] = test_technical_indicators()
    all_results['visualization'] = test_visualization()
    all_results['data_acquisition'] = test_data_acquisition()
    all_results['fundamental'] = test_fundamental_analysis()
    all_results['risk_management'] = test_risk_management()
    
    # 汇总结果
    print("\n" + "="*50)
    print("自测结果汇总:")
    print("="*50)
    
    total_tests = 0
    passed_tests = 0
    
    for category, results in all_results.items():
        print(f"\n{category.upper()}:")
        for test, result in results.items():
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"  {test}: {status}")
            total_tests += 1
            if result:
                passed_tests += 1
    
    print(f"\n总计: {passed_tests}/{total_tests} 测试通过")
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"成功率: {success_rate:.1f}%")
    
    return all_results, success_rate

if __name__ == "__main__":
    try:
        results, rate = run_all_tests()
        if rate >= 80:
            print(f"\n🎉 测试完成! 整体成功率 {rate:.1f}%, 能力基本可用")
            sys.exit(0)
        else:
            print(f"\n⚠️  测试完成! 整体成功率 {rate:.1f}%, 部分能力存在问题")
            sys.exit(1)
    except Exception as e:
        print(f"测试执行出错: {e}")
        traceback.print_exc()
        sys.exit(1)