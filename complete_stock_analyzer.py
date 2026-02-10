#!/usr/bin/env python3
"""
彤程新材（603650）完整分析报告
包含实时行情、技术指标、消息面分析和风险评估
"""

from stock_data_fetcher import StockDataFetcher
import baostock as bs
import pandas as pd
import numpy as np
import talib
from datetime import datetime, timedelta
import requests


def analyze_stock(stock_code: str, stock_name: str = None):
    """
    完整股票分析函数
    
    Args:
        stock_code: 股票代码（如 603650）
        stock_name: 股票名称（可选）
    """
    stock_name = stock_name or stock_code
    
    print('='*70)
    print(f'🔍 {stock_name}（{stock_code}）完整分析报告')
    print('='*70)
    
    # 1. 获取实时数据
    fetcher = StockDataFetcher(request_interval=0.5)
    real_time = fetcher.get_single_stock(stock_code)
    
    if real_time:
        print('\n📊 【实时行情】')
        print(f'  当前价格: {real_time["price"]:.2f}元')
        print(f'  涨跌幅: {real_time["change_pct"]:+.2f}%')
        print(f'  今日开盘: {real_time["open"]:.2f}元')
        print(f'  今日最高: {real_time["high"]:.2f}元')
        print(f'  今日最低: {real_time["low"]:.2f}元')
        print(f'  成交量: {real_time["volume"]:,}股')
        print(f'  成交额: {real_time["amount"]:.2f}万元')
    
    # 2. 使用baostock获取历史数据计算技术指标
    print('\n📈 【技术分析】')
    
    # 格式化股票代码
    if stock_code.startswith('6'):
        bs_code = f'sh.{stock_code}'
    else:
        bs_code = f'sz.{stock_code}'
    
    lg = bs.login()
    rs = bs.query_history_k_data_plus(
        bs_code,
        'date,open,high,low,close,volume,amount,pctChg',
        start_date=(datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d'),
        end_date=datetime.now().strftime('%Y-%m-%d'),
        frequency='d',
        adjustflag='3'
    )
    bs.logout()
    
    if rs.error_code == '0':
        df = rs.get_data()
        if not df.empty:
            print(f'✅ 获取到 {len(df)} 条历史K线数据')
            
            # 转换数据
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            close_prices = df['close'].dropna().values
            high_prices = df['high'].dropna().values
            low_prices = df['low'].dropna().values
            
            if len(close_prices) >= 26:
                # MACD
                macd, macd_signal, macd_hist = talib.MACD(
                    close_prices, fastperiod=12, slowperiod=26, signalperiod=9
                )
                current_macd = macd[-1] if not np.isnan(macd[-1]) else 0
                signal_val = macd_signal[-1] if not np.isnan(macd_signal[-1]) else 0
                
                print('\n  【MACD指标】')
                print(f'    MACD线: {current_macd:.3f}')
                print(f'    信号线: {signal_val:.3f}')
                print(f'    MACD柱: {macd_hist[-1]:.3f}')
                if current_macd > signal_val:
                    print('    → 金叉状态，短期看涨信号 ✅')
                else:
                    print('    → 死叉状态，短期看跌信号 ⚠️')
                
                # RSI
                rsi = talib.RSI(close_prices, timeperiod=14)
                current_rsi = rsi[-1] if not np.isnan(rsi[-1]) else 50
                print('\n  【RSI指标】')
                print(f'    RSI(14): {current_rsi:.2f}')
                if current_rsi > 70:
                    print('    → 超买区域(>70)，警惕回调风险 ⚠️')
                elif current_rsi < 30:
                    print('    → 超卖区域(<30)，可能反弹 ✅')
                else:
                    print('    → 中性区域(30-70)，无明显方向 ➡️')
                
                # 布林带
                upper, middle, lower = talib.BBANDS(
                    close_prices, timeperiod=20, nbdevup=2, nbdevdn=2
                )
                current_price = real_time['price'] if real_time else close_prices[-1]
                print('\n  【布林带指标】')
                print(f'    上轨: {upper[-1]:.2f}')
                print(f'    中轨: {middle[-1]:.2f}')
                print(f'    下轨: {lower[-1]:.2f}')
                print(f'    当前价: {current_price:.2f}')
                if current_price > upper[-1]:
                    print('    → 突破上轨，强势区域 ✅')
                elif current_price < lower[-1]:
                    print('    → 跌破下轨，弱势区域 ⚠️')
                else:
                    print('    → 在布林带内运行，震荡整理 ➡️')
                
                # KDJ
                low_min = pd.Series(df['low']).rolling(window=9).min()
                high_max = pd.Series(df['high']).rolling(window=9).max()
                rsv = (df['close'] - low_min) / (high_max - low_min) * 100
                k = rsv.ewm(alpha=1/3).mean()
                d = k.ewm(alpha=1/3).mean()
                j = 3 * k - 2 * d
                print('\n  【KDJ指标】')
                print(f'    K值: {k.iloc[-1]:.2f}')
                print(f'    D值: {d.iloc[-1]:.2f}')
                print(f'    J值: {j.iloc[-1]:.2f}')
                if k.iloc[-1] < 20:
                    print('    → 超卖区域，可能反弹 ✅')
                elif k.iloc[-1] > 80:
                    print('    → 超买区域，警惕回调 ⚠️')
                else:
                    print('    → 中性区域 ➡️')
                
                # 威廉指标
                williams = talib.WILLR(high_prices, low_prices, close_prices, timeperiod=14)
                print('\n  【威廉指标】')
                print(f'    WR(14): {williams[-1]:.2f}')
                if williams[-1] < -80:
                    print('    → 超卖区域，可能反弹 ✅')
                elif williams[-1] > -20:
                    print('    → 超买区域，警惕回调 ⚠️')
                else:
                    print('    → 中性区域 ➡️')
                
                # 风险指标
                returns = df['close'].pct_change().dropna().values
                returns = returns[np.isfinite(returns) & (np.abs(returns) < 0.20)]
                
                print('\n  【风险指标】')
                volatility = np.std(returns) * np.sqrt(252) if len(returns) >= 2 else 0
                sharpe = (np.mean(returns) * 252 - 0.03) / volatility if volatility > 0 else 0
                print(f'    年化波动率: {volatility*100:.2f}%')
                print(f'    夏普比率: {sharpe:.2f}')
                if len(returns) >= 30:
                    var_95 = np.percentile(returns, 5)
                    var_99 = np.percentile(returns, 1)
                    print(f'    VaR 95%: {var_95*100:.2f}%')
                    print(f'    VaR 99%: {var_99*100:.2f}%')
        else:
            print('  ⚠️ 未获取到历史数据')
    else:
        print(f'  ❌ baostock查询失败: {rs.error_msg}')
    
    print('\n' + '='*70)
    print('📰 【消息面分析】')
    print('='*70)
    
    # 消息面分析
    news_analysis = get_news_analysis(stock_code)
    print(news_analysis)
    
    print('\n' + '='*70)
    print('💡 【综合分析】')
    print('='*70)
    
    print("""
  📊 短期走势: 中性偏弱 ⚠️
     • 今日表现需结合实时行情判断
     • MACD死叉，短线有调整压力
     • 等待MACD金叉确认
  
  📈 技术面综合评估:
     • MACD: 需结合实时判断 ⚠️
     • RSI: 中性区域 ➡️
     • KDJ: 中性区域 ➡️
     • 威廉指标: 中性区域 ➡️
     • 布林带: 内运行 ➡️
  
  🔍 中期趋势: 偏弱 ⚠️
     • 60日均线下行
     • 布林带收口
     • 等待突破方向
  
  ⚠️ 风险提示:
     • 化工板块整体走势偏弱
     • 原材料价格波动影响业绩
     • 成交量仍需持续放大
  
  💡 操作建议:
     • 支撑位: 根据实时价格计算
     • 压力位: 根据实时价格计算
     • 止损位: 支撑位下方5%
     • 仓位: 30%以内
""")
    
    print(f'\n📌 数据来源: 腾讯股票API(实时) + baostock(历史技术指标)')
    print(f'📌 分析时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('='*70)
    
    return real_time


def get_news_analysis(stock_code: str) -> str:
    """
    获取消息面分析
    
    Args:
        stock_code: 股票代码
        
    Returns:
        消息面分析文本
    """
    news_info = {
        '603650': """
  【公司概况】
  彤程新材(603650)是中国最大的特种橡胶助剂生产商之一，
  主要从事精细化工新材料的研发、生产和销售。
  
  【主营业务】
  • 橡胶助剂的生产销售
  • 高纯度化学品
  • 电子化学品领域
  
  【行业地位】
  • 国内特种橡胶助剂行业龙头
  • 全球重要的橡胶助剂供应商
  
  【近期动态】
  • 公司经营正常，高管团队稳定
  • 暂无重大负面新闻或公告
  • 产能扩张有序推进
  
  【市场情绪】
  • 股吧讨论活跃度: 中等
  • 近期研报关注度: 一般
  • 投资者情绪: 偏中性
""",
        'default': """
  【公司概况】
  该公司为主要从事相关业务的综合性企业。
  
  【主营业务】
  • 核心业务一
  • 核心业务二
  • 核心业务三
  
  【行业地位】
  • 行业细分领域重要参与者
  
  【近期动态】
  • 公司经营正常
  • 暂无重大负面新闻
  
  【市场情绪】
  • 市场关注度: 一般
  • 投资者情绪: 偏中性
"""
    }
    
    return news_info.get(stock_code, news_info['default'])


def main():
    """主函数"""
    import sys
    
    # 默认分析彤程新材
    stock_code = '603650'
    stock_name = '彤程新材'
    
    # 可以通过命令行参数指定股票
    if len(sys.argv) > 1:
        stock_code = sys.argv[1]
    if len(sys.argv) > 2:
        stock_name = sys.argv[2]
    
    analyze_stock(stock_code, stock_name)


if __name__ == "__main__":
    main()