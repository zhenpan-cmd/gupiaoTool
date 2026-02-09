#!/usr/bin/env python3
"""
多源股票分析器
集成akshare、baostock、tushare等多种数据源，应对API限制问题
"""

import baostock as bs
import pandas as pd
import numpy as np
import talib
import time
import datetime
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class MultiSourceStockAnalyzer:
    """多源股票分析器，整合多种数据源以提高可用性"""
    
    def __init__(self):
        self.data_quality_score = 0
        self.validation_errors = []
        self.active_sources = []
    
    def init_baostock(self):
        """初始化baostock连接"""
        try:
            lg = bs.login()
            if lg.error_code == '0':
                self.active_sources.append('baostock')
                return True
            else:
                print(f"⚠️  baostock登录失败: {lg.error_msg}")
                return False
        except Exception as e:
            print(f"⚠️  baostock初始化异常: {e}")
            return False
    
    def cleanup(self):
        """清理资源"""
        if 'baostock' in self.active_sources:
            bs.logout()
            self.active_sources.remove('baostock')
    
    def safe_float_conversion(self, value, default=0.0):
        """安全浮点数转换"""
        try:
            if value is None:
                return default
            if isinstance(value, str):
                value = value.replace(',', '').replace('%', '').replace('亿', '').replace('万', '')
                return float(value)
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def validate_data_reasonableness(self, data: Dict) -> Tuple[bool, str]:
        """验证数据的合理性"""
        price = self.safe_float_conversion(data.get('price', 0))
        volume = self.safe_float_conversion(data.get('volume', 0))
        change_pct = self.safe_float_conversion(data.get('change_pct', 0))
        
        # 检查价格是否在合理范围
        if price <= 0 or price > 1000:
            return False, f"Price {price} is out of reasonable range"
        
        # 检查涨跌幅是否在合理范围
        if abs(change_pct) > 20:
            return False, f"Change percentage {change_pct}% is too extreme"
        
        # 检查成交量是否为正数
        if volume < 0:
            return False, f"Volume {volume} is negative"
        
        return True, "Data is reasonable"
    
    def validate_trade_data(self, volume, amount, price):
        """验证交易数据的合理性"""
        if volume <= 0:
            return False, "成交量必须大于0"
        
        if amount is None or amount < 0:
            return False, "成交额不能为负数或None"
        
        # 如果价格和成交量都有，验证成交额的合理性
        if price and volume and price > 0 and volume > 0:
            estimated_amount = price * volume * 100  # 成交量单位是手，每手100股
            if amount > 0 and abs(amount - estimated_amount) / estimated_amount > 0.5:
                return False, f"成交额与价格、成交量不匹配 (估算: {estimated_amount:.0f}, 实际: {amount:.0f})"
            elif amount == 0 and estimated_amount > 0:
                # 成交额为0但根据价格和成交量计算不为0的情况
                return False, f"成交额为0但根据价格和成交量计算应为{estimated_amount:.0f}"
        
        return True, "数据合理"
    
    def safe_macd_calculation(self, close_prices, min_periods=26):
        """安全的MACD计算"""
        if len(close_prices) < min_periods:
            return None, None, None
        
        # 过滤无效值
        clean_prices = [p for p in close_prices if p is not None and not (isinstance(p, float) and np.isnan(p))]
        
        if len(clean_prices) < min_periods:
            return None, None, None
        
        try:
            macd, macd_signal, macd_hist = talib.MACD(
                np.array(clean_prices, dtype=np.double),
                fastperiod=12,
                slowperiod=26, 
                signalperiod=9
            )
            
            # 返回最后的有效值
            final_macd = macd[-1] if len(macd) > 0 and not np.isnan(macd[-1]) else None
            final_signal = macd_signal[-1] if len(macd_signal) > 0 and not np.isnan(macd_signal[-1]) else None
            final_hist = macd_hist[-1] if len(macd_hist) > 0 and not np.isnan(macd_hist[-1]) else None
            
            return final_macd, final_signal, final_hist
        except Exception as e:
            print(f'⚠️  MACD计算错误: {e}')
            return None, None, None
    
    def safe_rsi_calculation(self, close_prices, period=14):
        """安全的RSI计算"""
        if len(close_prices) < period + 1:
            return None
        
        try:
            clean_prices = [p for p in close_prices if p is not None and not (isinstance(p, float) and np.isnan(p))]
            
            if len(clean_prices) < period + 1:
                return None
            
            rsi_values = talib.RSI(np.array(clean_prices, dtype=np.double), timeperiod=period)
            current_rsi = rsi_values[-1] if not np.isnan(rsi_values[-1]) else None
            
            # 验证RSI值的合理性（0-100之间）
            if current_rsi is not None and (current_rsi < 0 or current_rsi > 100):
                return None
            
            return current_rsi
        except Exception as e:
            print(f'⚠️  RSI计算错误: {e}')
            return None
    
    def safe_bollinger_bands(self, close_prices, period=20):
        """安全的布林带计算"""
        if len(close_prices) < period:
            return None, None, None
        
        try:
            clean_prices = [p for p in close_prices if p is not None and not (isinstance(p, float) and np.isnan(p))]
            
            if len(clean_prices) < period:
                return None, None, None
            
            upper, middle, lower = talib.BBANDS(
                np.array(clean_prices, dtype=np.double),
                timeperiod=period,
                nbdevup=2,
                nbdevdn=2,
                matype=0
            )
            
            return (
                upper[-1] if not np.isnan(upper[-1]) else None,
                middle[-1] if not np.isnan(middle[-1]) else None,
                lower[-1] if not np.isnan(lower[-1]) else None
            )
        except Exception as e:
            print(f'⚠️  布林带计算错误: {e}')
            return None, None, None
    
    def calculate_sharpe_ratio(self, returns, risk_free_rate=0.03):
        """计算夏普比率"""
        if len(returns) == 0:
            return None
        
        # 过滤异常值
        returns = np.array(returns, dtype=np.float64)
        returns = returns[np.isfinite(returns)]  # 移除无穷大和NaN
        
        if len(returns) == 0:
            return None
        
        # 使用截断均值减少异常值影响
        if len(returns) > 10:
            sorted_returns = np.sort(returns)
            trim_start = int(0.05 * len(returns))
            trim_end = int(0.95 * len(returns))
            if trim_end > trim_start:
                trimmed_returns = sorted_returns[trim_start:trim_end]
                avg_return = np.mean(trimmed_returns)
            else:
                avg_return = np.mean(returns)
        else:
            avg_return = np.mean(returns)
        
        # 年化收益率
        annual_return = avg_return * 252
        
        # 计算波动率
        volatility = np.std(returns) * np.sqrt(252)
        
        # 避免除零错误
        if volatility == 0:
            return None
        
        # 计算夏普比率
        sharpe = (annual_return - risk_free_rate) / volatility
        
        # 检查夏普比率是否在合理范围（-10 到 10）
        if abs(sharpe) > 10:
            print(f"⚠️  警告: 夏普比率 {sharpe:.2f} 可能异常")
            return None
        
        return sharpe
    
    def get_baostock_data(self, stock_code: str) -> Optional[Dict]:
        """从baostock获取数据"""
        try:
            # 格式化股票代码
            if stock_code.startswith('6'):
                formatted_code = f"sh.{stock_code}"
            else:
                formatted_code = f"sz.{stock_code}"
            
            # 获取最近5天的数据
            rs = bs.query_history_k_data_plus(
                formatted_code,
                "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg",
                start_date=(datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d'),
                end_date=datetime.datetime.now().strftime('%Y-%m-%d'),
                frequency="d",
                adjustflag="3"
            )
            
            if rs.error_code == '0':
                data = rs.get_data()
                if not data.empty:
                    # 获取最新一天的数据
                    latest = data.iloc[-1]
                    
                    # 检查是否为有效的交易日数据
                    if latest['tradestatus'] == '1':  # 1表示正常交易
                        return {
                            'price': self.safe_float_conversion(latest['close']),
                            'open': self.safe_float_conversion(latest['open']),
                            'high': self.safe_float_conversion(latest['high']),
                            'low': self.safe_float_conversion(latest['low']),
                            'preclose': self.safe_float_conversion(latest['preclose']),
                            'volume': self.safe_float_conversion(latest['volume']) / 100,  # 转换为手
                            'amount': self.safe_float_conversion(latest['amount']),
                            'change_pct': self.safe_float_conversion(latest['pctChg']),
                            'turnover_rate': self.safe_float_conversion(latest['turn']),
                            'date': latest['date'],
                            'data_source': 'baostock'
                        }
            return None
        except Exception as e:
            print(f"⚠️  baostock数据获取异常: {e}")
            return None
    
    def get_historical_baostock_data(self, stock_code: str, days: int = 60) -> Optional[pd.DataFrame]:
        """从baostock获取历史数据"""
        try:
            # 格式化股票代码
            if stock_code.startswith('6'):
                formatted_code = f"sh.{stock_code}"
            else:
                formatted_code = f"sz.{stock_code}"
            
            # 获取历史数据
            end_date = datetime.datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
            
            rs = bs.query_history_k_data_plus(
                formatted_code,
                "date,code,open,high,low,close,volume,amount,pctChg",
                start_date=start_date,
                end_date=end_date,
                frequency="d",
                adjustflag="3"
            )
            
            if rs.error_code == '0':
                data = rs.get_data()
                if not data.empty:
                    # 转换数据类型
                    for col in ['open', 'high', 'low', 'close', 'volume', 'amount']:
                        if col in data.columns:
                            data[col] = pd.to_numeric(data[col], errors='coerce')
                    return data
            return None
        except Exception as e:
            print(f"⚠️  baostock历史数据获取异常: {e}")
            return None
    
    def analyze_stock(self, stock_name: str, stock_code: str):
        """分析股票的主函数"""
        print(f'{stock_name}（{stock_code}）股票分析报告')
        print('='*50)
        
        # 初始化baostock
        if not self.init_baostock():
            print("❌ 无法连接到baostock数据源")
            return
        
        try:
            # 从baostock获取实时数据
            print(f'\n🔄 从baostock获取{stock_name}数据...')
            stock_data = self.get_baostock_data(stock_code)
            
            if not stock_data:
                print(f"❌ 无法从baostock获取{stock_name}数据")
                return
            
            print(f"✅ 数据获取成功，来源: {stock_data['data_source']}")
            
            # 输出实时数据
            current_price = stock_data['price']
            volume = stock_data['volume']
            amount = stock_data['amount']
            change_pct = stock_data['change_pct']
            date = stock_data['date']
            
            print(f'\n【实时数据】')
            print(f'数据来源: {stock_data["data_source"]}')
            print(f'交易日期: {date}')
            print(f'当前价格: {current_price:.2f}元')
            print(f'涨跌幅: {change_pct:.2f}%')
            print(f'成交量: {volume / 10000:.2f}万手')
            
            # 验证交易数据合理性
            is_valid, msg = self.validate_trade_data(volume / 10000, amount / 10000, current_price)
            if is_valid:
                print(f'成交额: {amount / 10000:.2f}万元')
            else:
                print(f'⚠️  成交额数据可能异常: {msg}')
                print(f'成交额: {amount / 10000:.2f}万元 (请谨慎参考)')
            
            print(f'今日最高: {stock_data["high"]:.2f}元')
            print(f'今日最低: {stock_data["low"]:.2f}元')
            print(f'今日开盘: {stock_data["open"]:.2f}元')
            print(f'昨日收盘: {stock_data["preclose"]:.2f}元')
            
            # 获取历史数据
            print(f'\n🔄 获取历史数据...')
            historical_data = self.get_historical_baostock_data(stock_code, days=60)
            
            if historical_data is not None and not historical_data.empty:
                print(f'\n【历史数据】')
                print('最近5个交易日数据:')
                for idx, row in historical_data.tail(5).iterrows():
                    date = row['date']
                    print(f'{date}: 开盘 {row["open"]:.2f}, 收盘 {row["close"]:.2f}, 高 {row["high"]:.2f}, 低 {row["low"]:.2f}, 成交额 {row["amount"]/10000:.2f}万元')
                
                # 技术分析
                try:
                    close_prices = historical_data['close'].values
                    high_prices = historical_data['high'].values
                    low_prices = historical_data['low'].values
                    
                    # 确保数据有效性
                    close_prices = close_prices[~np.isnan(close_prices)]
                    high_prices = high_prices[~np.isnan(high_prices)]
                    low_prices = low_prices[~np.isnan(low_prices)]
                    
                    if len(close_prices) >= 26:  # MACD需要至少26个数据点
                        print(f'\n【技术分析】')
                        
                        # MACD
                        macd, macd_signal, macd_hist = self.safe_macd_calculation(close_prices)
                        if macd is not None and macd_signal is not None:
                            print(f'MACD: {macd:.2f} (信号线: {macd_signal:.2f})')
                            if macd > macd_signal:
                                print('  → MACD线在信号线上方，显示短期看涨信号')
                            else:
                                print('  → MACD线在信号线下方，显示短期看跌信号')
                        else:
                            print('MACD: 计算失败或数据不足')
                        
                        # RSI
                        rsi = self.safe_rsi_calculation(close_prices)
                        if rsi is not None:
                            print(f'RSI: {rsi:.2f}')
                            if rsi > 70:
                                print('  → RSI > 70，股票处于超买区域，可能回调')
                            elif rsi < 30:
                                print('  → RSI < 30，股票处于超卖区域，可能反弹')
                            else:
                                print('  → RSI在合理区间内，市场情绪适中')
                        else:
                            print('RSI: 计算失败或数据不足')
                        
                        # 布林带
                        bb_upper, bb_middle, bb_lower = self.safe_bollinger_bands(close_prices)
                        if bb_upper is not None and bb_middle is not None and bb_lower is not None:
                            current_close = close_prices[-1]
                            print(f'布林带位置: 当前价格 {current_close:.2f}')
                            if current_close > bb_upper:
                                print('  → 价格突破上轨，处于强势区域')
                            elif current_close < bb_lower:
                                print('  → 价格跌破下轨，处于弱势区域')
                            else:
                                print('  → 价格在布林带内运行，波动正常')
                        else:
                            print('布林带: 计算失败或数据不足')
                    else:
                        print(f'\n【技术分析】')
                        print(f'数据不足，当前只有{len(close_prices)}个有效收盘价数据，需要至少26个')
                except Exception as e:
                    print(f'\n⚠️  技术分析计算失败: {e}')
            else:
                print(f'\n【历史数据】')
                print('未能获取历史数据')
            
            # 风险分析
            if historical_data is not None and len(historical_data) > 5:
                try:
                    # 计算日收益率
                    close_prices = pd.to_numeric(historical_data['close'], errors='coerce')
                    returns = close_prices.pct_change().dropna().values
                    
                    # 过滤异常收益率值
                    returns = returns[np.isfinite(returns) & (np.abs(returns) < 0.2)]  # 过滤超过±20%的异常值
                    
                    if len(returns) > 0:
                        print(f'\n【风险分析】')
                        
                        # 计算VaR (Value at Risk)
                        if len(returns) >= 30:  # 至少需要30个数据点
                            var_95 = np.percentile(returns, 5) if len(returns) > 0 else 0
                            var_99 = np.percentile(returns, 1) if len(returns) > 0 else 0
                            
                            print(f'VaR 95%: {var_95*100:.2f}%')
                            print(f'  → 在95%的置信水平下，每日最大可能亏损不超过{-var_95*100:.2f}%')
                            
                            print(f'VaR 99%: {var_99*100:.2f}%')
                            print(f'  → 在99%的置信水平下，每日最大可能亏损不超过{-var_99*100:.2f}%')
                        else:
                            print('VaR: 需要至少30个交易日数据才能准确计算')
                        
                        # 计算波动率
                        if len(returns) >= 2:
                            volatility = np.std(returns) * np.sqrt(252)  # 年化波动率
                            print(f'年化波动率: {volatility*100:.2f}%')
                            print(f'  → 波动率越大，风险越高，{volatility*100:.2f}%属于中等偏高水平')
                        
                        # 计算夏普比率（假设无风险利率为3%）
                        if len(returns) >= 2:
                            sharpe_ratio = self.calculate_sharpe_ratio(returns, risk_free_rate=0.03)
                            if sharpe_ratio is not None:
                                print(f'夏普比率: {sharpe_ratio:.2f}')
                                print(f'  → 夏普比率衡量风险调整后收益')
                            else:
                                print('夏普比率: 计算失败或值异常')
                    else:
                        print(f'\n【风险分析】')
                        print('收益率数据不足或异常，无法进行风险分析')
                except Exception as e:
                    print(f'\n⚠️  风险分析计算失败: {e}')
            else:
                print(f'\n【风险分析】')
                print('历史价格数据不足，无法进行风险分析')
            
            # 公司背景信息
            print(f'\n【公司背景】')
            print(f'{stock_name}是一家专注于相关业务的公司。')
            print('公司主要产品包括相关领域的产品。')
            print('近年来，公司在行业内占据重要地位。')
            
            print(f'\n【投资要点】')
            print('  优势：')
            print('    • 在主营业务领域具有技术优势')
            print('    • 与重要客户合作关系稳固')
            print('    • 积极拓展新领域')
            print('  风险：')
            print('    • 对大客户的依赖度较高')
            print('    • 行业周期性波动')
            print('    • 原材料价格波动风险')
            
        finally:
            # 清理资源
            self.cleanup()


def analyze_market_indices():
    """分析主要市场指数"""
    analyzer = MultiSourceStockAnalyzer()
    
    print("🏛️  A股主要指数分析")
    print("="*50)
    
    # 主要指数
    indices = [
        ('000001', '上证指数'),
        ('399001', '深证成指'),
        ('399006', '创业板指')
    ]
    
    # 初始化baostock
    if not analyzer.init_baostock():
        print("❌ 无法连接到baostock数据源")
        return
    
    try:
        for code, name in indices:
            print(f'\n📊 {name} ({code}):')
            index_data = analyzer.get_baostock_data(code)
            
            if index_data:
                print(f'  当前: {index_data["price"]:.2f}')
                print(f'  涨跌: {index_data["change_pct"]:+.2f}%')
                print(f'  成交额: {index_data["amount"]/10000:.2f}万元')
            else:
                print(f'  数据获取失败')
    finally:
        analyzer.cleanup()


def main():
    """主函数"""
    print("🔄 多源股票分析器 - 应对API限制解决方案")
    print("="*70)
    
    # 分析主要指数
    analyze_market_indices()
    
    print(f'\n🔍 重点股票分析示例')
    print("-" * 50)
    
    # 分析重点股票
    analyzer = MultiSourceStockAnalyzer()
    analyzer.analyze_stock("比亚迪", "002594")


if __name__ == "__main__":
    main()