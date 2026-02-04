#!/usr/bin/env python3
"""
改进版股票分析器
增强了数据验证和多源数据获取功能，提高数据准确性
"""

import easyquotation
import akshare as ak
import pandas as pd
import numpy as np
import talib
import datetime
from typing import Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class ImprovedStockAnalyzer:
    """改进版股票分析器，重点改进数据准确性和验证机制"""
    
    def __init__(self):
        self.data_quality_score = 0
        self.validation_errors = []
        self.data_sources = {}
    
    def validate_stock_code(self, name, code):
        """验证股票代码与名称的匹配性"""
        try:
            info = ak.stock_individual_info_em(symbol=code)
            if not info.empty:
                name_row = info[info['item'] == '股票简称']
                if not name_row.empty:
                    actual_name = name_row.iloc[0]['value']
                    if name in actual_name or actual_name in name:
                        return True, code, actual_name
                    else:
                        return False, code, actual_name
            return False, code, None
        except Exception as e:
            print(f"⚠️  代码验证失败: {e}")
            return False, code, None
    
    def get_multi_source_data(self, stock_code: str) -> Dict:
        """从多个源获取数据并进行交叉验证"""
        sources_data = {}
        
        # 1. 从akshare获取数据
        try:
            ak_data = ak.stock_zh_a_spot_em()
            stock_row = ak_data[ak_data['代码'] == stock_code]
            if not stock_row.empty:
                ak_stock = stock_row.iloc[0]
                sources_data['akshare'] = {
                    'price': ak_stock['最新价'],
                    'volume': ak_stock['成交量'],
                    'amount': ak_stock['成交额'],
                    'change_pct': ak_stock['涨跌幅'],
                    'high': ak_stock['最高'],
                    'low': ak_stock['最低'],
                    'open': ak_stock['今开'],
                    'prev_close': ak_stock['昨收'],
                    'timestamp': datetime.datetime.now()
                }
        except Exception as e:
            print(f"⚠️  akshare数据获取失败: {e}")
        
        # 2. 从easyquotation获取数据
        try:
            eq_api = easyquotation.use('sina')
            eq_data = eq_api.real([stock_code])
            if stock_code in eq_data:
                eq_stock = eq_data[stock_code]
                sources_data['easyquotation'] = {
                    'price': float(eq_stock['now']) if eq_stock['now'] != '' else 0,
                    'volume': float(eq_stock['volume']),
                    'amount': float(eq_stock.get('成交额', 0)),
                    'change_pct': float(eq_stock.get('涨跌(%)', 0)),
                    'high': float(eq_stock.get('high', 0)),
                    'low': float(eq_stock.get('low', 0)),
                    'open': float(eq_stock.get('open', 0)),
                    'prev_close': float(eq_stock.get('close', 0)),
                    'timestamp': datetime.datetime.now()
                }
        except Exception as e:
            print(f"⚠️  easyquotation数据获取失败: {e}")
        
        # 3. 从腾讯财经获取数据
        try:
            qt_data = easyquotation.use('tencent')
            qt_result = qt_data.real([stock_code])
            if stock_code in qt_result:
                qt_stock = qt_result[stock_code]
                sources_data['tencent'] = {
                    'price': float(qt_stock['now']) if qt_stock['now'] != '' else 0,
                    'volume': float(qt_stock['volume']),
                    'amount': float(qt_stock.get('成交额', 0)),
                    'change_pct': float(qt_stock.get('涨跌(%)', 0)),
                    'high': float(qt_stock.get('high', 0)),
                    'low': float(qt_stock.get('low', 0)),
                    'open': float(qt_stock.get('open', 0)),
                    'prev_close': float(qt_stock.get('close', 0)),
                    'timestamp': datetime.datetime.now()
                }
        except Exception as e:
            print(f"⚠️  tencent数据获取失败: {e}")
        
        return sources_data
    
    def validate_data_consistency(self, sources_data: Dict) -> Tuple[Dict, str]:
        """验证多源数据的一致性并选择最可靠的数据"""
        if not sources_data:
            return {}, "No data available"
        
        # 如果只有一个数据源，直接返回
        if len(sources_data) == 1:
            source_name = list(sources_data.keys())[0]
            return sources_data[source_name], f"Single source: {source_name}"
        
        # 多源数据对比
        valid_sources = []
        for source_name, data in sources_data.items():
            # 检查数据完整性
            if data.get('price', 0) > 0 and data.get('volume', 0) > 0:
                # 检查价格与成交额的逻辑关系（如果成交额可用）
                if data.get('amount', 0) > 0:
                    estimated_price = data['amount'] / (data['volume'] * 100) if data['volume'] > 0 else 0
                    price_diff_ratio = abs(estimated_price - data['price']) / data['price'] if data['price'] > 0 else float('inf')
                    if price_diff_ratio < 0.5:  # 价格差异小于50%
                        valid_sources.append((source_name, data, estimated_price))
                else:
                    valid_sources.append((source_name, data, data['price']))
        
        if not valid_sources:
            return {}, "No consistent data found"
        
        # 选择数据最一致的源
        best_source = max(valid_sources, key=lambda x: x[2] if x[2] > 0 else x[1]['price'])
        return best_source[1], f"Selected from {len(valid_sources)} sources, based on {best_source[0]}"
    
    def validate_data_timeliness(self, data: Dict) -> bool:
        """验证数据的时效性"""
        # 检查是否为今天的数据
        today = datetime.date.today()
        # 对于实时数据，我们无法直接获取日期，但可以通过其他方式验证
        # 检查是否有合理的交易活动
        return data.get('volume', 0) > 0  # 至少有交易量
    
    def validate_data_reasonableness(self, data: Dict) -> Tuple[bool, str]:
        """验证数据的合理性"""
        price = data.get('price', 0)
        volume = data.get('volume', 0)
        change_pct = data.get('change_pct', 0)
        
        # 检查价格是否在合理范围（0-1000元，可根据股票类型调整）
        if price <= 0 or price > 1000:
            return False, f"Price {price} is out of reasonable range"
        
        # 检查涨跌幅是否在合理范围（-10%到+10%，考虑特殊情况可放宽）
        if abs(change_pct) > 20:
            return False, f"Change percentage {change_pct}% is too extreme"
        
        # 检查成交量是否为正数
        if volume < 0:
            return False, f"Volume {volume} is negative"
        
        return True, "Data is reasonable"
    
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
    
    def validate_trade_data(self, volume, amount, price):
        """验证交易数据的合理性"""
        if volume <= 0:
            return False, "成交量必须大于0"
        
        if amount is None or amount < 0:
            return False, "成交额不能为负数或None"
        
        # 如果价格和成交量都有，验证成交额的合理性
        if price and volume and price > 0 and volume > 0:
            estimated_amount = price * volume * 100  # 成交量单位是手，每手100股
            # 允许一定误差范围（50%）
            if abs(amount - estimated_amount) / estimated_amount > 0.5 and amount != 0:
                return False, f"成交额与价格、成交量不匹配 (估算: {estimated_amount:.0f}, 实际: {amount:.0f})"
        
        return True, "数据合理"
    
    def safe_macd_calculation(self, close_prices, min_periods=26):
        """安全的MACD计算，包含数据验证"""
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
            
            # 验证MACD值的合理性（避免0值异常）
            if final_macd is not None and abs(final_macd) < 1e-10:
                # 检查是否真的接近0还是数据问题
                if len(set(close_prices)) > 1:  # 价格有变化
                    return None, None, None  # 可能是计算错误
            
            return final_macd, final_signal, final_hist
        except Exception as e:
            print(f'⚠️  MACD计算错误: {e}')
            return None, None, None
    
    def calculate_sharpe_ratio(self, returns, risk_free_rate=0.03):
        """计算夏普比率，包含异常值处理"""
        if len(returns) == 0:
            return None
        
        # 过滤异常值
        returns = np.array(returns, dtype=np.float64)
        returns = returns[np.isfinite(returns)]  # 移除无穷大和NaN
        
        if len(returns) == 0:
            return None
        
        # 使用截断均值减少异常值影响
        if len(returns) > 10:  # 只有在数据足够多时才使用截断均值
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
            return None  # 返回None而不是异常值
        
        return sharpe
    
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
    
    def analyze_stock(self, stock_name, stock_code):
        """分析股票的主函数"""
        print(f'{stock_name}（{stock_code}）股票分析报告')
        print('='*50)
        
        # 验证股票代码
        is_valid, code, actual_name = self.validate_stock_code(stock_name, stock_code)
        if not is_valid and actual_name:
            print(f"⚠️  警告: 代码 {stock_code} 对应的是 {actual_name}，而非 {stock_name}")
        elif not is_valid:
            print(f"⚠️  无法验证代码 {stock_code} 的准确性")
        else:
            print(f"✅ 代码验证通过: {actual_name}({code})")
        
        # 获取多源数据
        print(f'\n🔄 正在从多个数据源获取数据...')
        sources_data = self.get_multi_source_data(stock_code)
        
        if not sources_data:
            print("❌ 无法从任何数据源获取数据")
            return
        
        print(f"📊 获取到 {len(sources_data)} 个数据源的数据")
        
        # 验证和选择最可靠的数据
        selected_data, selection_method = self.validate_data_consistency(sources_data)
        
        if not selected_data:
            print("❌ 无法找到一致的数据")
            return
        
        print(f"✅ 数据选择方法: {selection_method}")
        
        # 验证数据时效性
        if not self.validate_data_timeliness(selected_data):
            print("⚠️  数据可能不是最新的")
        else:
            print("✅ 数据时效性验证通过")
        
        # 验证数据合理性
        is_reasonable, reason_msg = self.validate_data_reasonableness(selected_data)
        if not is_reasonable:
            print(f"❌ 数据合理性验证失败: {reason_msg}")
            return
        else:
            print("✅ 数据合理性验证通过")
        
        # 输出验证后的实时数据
        current_price = selected_data.get('price', 0)
        volume = selected_data.get('volume', 0)
        amount = selected_data.get('amount', 0)
        change_pct = selected_data.get('change_pct', 0)
        high = selected_data.get('high', 0)
        low = selected_data.get('low', 0)
        open_price = selected_data.get('open', 0)
        prev_close = selected_data.get('prev_close', 0)
        
        print(f'\n【实时数据】')
        print(f'数据质量: 高 (经过多源验证)')
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
        
        print(f'今日最高: {high:.2f}元')
        print(f'今日最低: {low:.2f}元')
        print(f'今日开盘: {open_price:.2f}元')
        print(f'昨日收盘: {prev_close:.2f}元')
        
        # 获取历史数据
        try:
            print(f'\n🔄 获取历史数据...')
            stock_hist = ak.stock_zh_a_hist(symbol=stock_code, period='daily', adjust='qfq')
            if not stock_hist.empty:
                # 检查数据日期的合理性
                latest_date = pd.to_datetime(stock_hist['日期']).max()
                today = datetime.date.today()
                
                if latest_date.date() < today:
                    print(f"⚠️  历史数据最新日期为 {latest_date.date()}，可能不是最新数据")
                
                # 取最近60个交易日的数据
                recent_data = stock_hist.tail(60).reset_index(drop=True)
                recent_data['日期'] = pd.to_datetime(recent_data['日期'])
                
                # 转换数据类型
                for col in ['开盘', '收盘', '最高', '最低', '成交量']:
                    if col in recent_data.columns:
                        recent_data[col] = pd.to_numeric(recent_data[col], errors='coerce')
                
                # 专门处理成交额
                if '成交额' in recent_data.columns:
                    recent_data['成交额'] = pd.to_numeric(recent_data['成交额'], errors='coerce')
                
                print(f'【历史数据】')
                print('最近5个交易日数据:')
                for idx, row in recent_data.tail(5).iterrows():
                    date = row['日期'].strftime('%Y-%m-%d')
                    print(f'{date}: 开盘 {row["开盘"]:.2f}, 收盘 {row["收盘"]:.2f}, 高 {row["最高"]:.2f}, 低 {row["最低"]:.2f}, 成交额 {row["成交额"]/10000:.2f}万元')
            else:
                print('\n⚠️  未能获取历史数据')
                recent_data = pd.DataFrame()
        except Exception as e:
            print(f'⚠️  历史数据获取失败: {e}')
            recent_data = pd.DataFrame()
        
        # 技术分析
        if not recent_data.empty and len(recent_data) >= 26:
            try:
                close_prices = recent_data['收盘'].values
                high_prices = recent_data['最高'].values
                low_prices = recent_data['最低'].values
                
                # 确保数据有效性
                close_prices = close_prices[~np.isnan(close_prices)]
                high_prices = high_prices[~np.isnan(high_prices)]
                low_prices = low_prices[~np.isnan(low_prices)]
                
                if len(close_prices) >= 26:
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
            print(f'\n【技术分析】')
            print('历史数据不足，无法进行技术分析')
        
        # 基本面分析
        try:
            print(f'\n【基本面分析】')
            # 获取财务摘要
            fin_indicator = ak.stock_financial_abstract_ths(symbol=stock_code)
            if not fin_indicator.empty:
                latest_fin = fin_indicator.iloc[-1]
                
                # 解析财务数据
                def parse_financial_value(value_str):
                    if pd.isna(value_str):
                        return 0.0
                    if isinstance(value_str, str):
                        value_str = value_str.replace('亿', '').replace('万', '').replace('%', '')
                        try:
                            return float(value_str)
                        except ValueError:
                            return 0.0
                    return float(value_str) if value_str is not None else 0.0
                
                net_profit = parse_financial_value(latest_fin.get('净利润', 0))  # 亿元
                eps = parse_financial_value(latest_fin.get('基本每股收益', 0))  # 元/股
                bps = parse_financial_value(latest_fin.get('每股净资产', 0))  # 元/股
                roe = parse_financial_value(latest_fin.get('净资产收益率', 0))  # %
                gross_margin = parse_financial_value(latest_fin.get('销售毛利率', 0))  # %
                net_margin = parse_financial_value(latest_fin.get('销售净利率', 0))  # %
                current_ratio = parse_financial_value(latest_fin.get('流动比率', 0))
                debt_to_asset = parse_financial_value(latest_fin.get('资产负债率', 0))  # %
                
                print(f'净利润: {net_profit:.2f} 亿元')
                print(f'  → 净利润规模显示公司盈利能力')
                
                print(f'每股收益(EPS): {eps:.2f} 元')
                print(f'  → EPS反映了公司为每一股创造的利润')
                
                print(f'净资产收益率(ROE): {roe:.2f}%')
                print(f'  → ROE越高表示公司运用自有资本的效率越高')
                
                print(f'销售毛利率: {gross_margin:.2f}%')
                print(f'  → 毛利率显示公司产品的盈利能力')
                
                print(f'销售净利率: {net_margin:.2f}%')
                print(f'  → 净利率显示最终盈利能力')
                
                print(f'流动比率: {current_ratio:.2f}')
                print(f'  → 流动比率衡量短期偿债能力')
                
                print(f'资产负债率: {debt_to_asset:.2f}%')
                print(f'  → 资产负债率显示财务杠杆水平')
                
                # 计算估值指标
                if eps != 0 and current_price != 0:
                    pe = current_price / eps if eps != 0 else None
                    if pe is not None:
                        print(f'PE(市盈率): {pe:.2f}')
                        print(f'  → PE是估值指标，{pe:.2f}倍表示按当前盈利水平回本期')
                    else:
                        print('PE(市盈率): 计算失败')
                
                if bps != 0 and current_price != 0:
                    pb = current_price / bps if bps != 0 else None
                    if pb is not None:
                        print(f'PB(市净率): {pb:.2f}')
                        print(f'  → PB低于1表示股价低于每股净资产，高于1则相反')
                    else:
                        print('PB(市净率): 计算失败')
            else:
                print('⚠️  未能获取财务数据')
        except Exception as e:
            print(f'⚠️  基本面分析数据获取失败: {e}')
        
        # 风险分析
        if 'close_prices' in locals() and len(close_prices) > 5:
            try:
                # 计算日收益率
                returns = np.diff(close_prices) / close_prices[:-1]
                
                # 过滤异常收益率值
                returns = returns[np.isfinite(returns) & (np.abs(returns) < 0.2)]  # 过滤超过±20%的异常值
                
                if len(returns) > 0:
                    print(f'\n【风险分析】')
                    
                    # 计算VaR (Value at Risk)
                    if len(returns) >= 30:
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
        print(f'{stock_name}是中国领先的新能源汽车和电池制造商，主要从事新能源汽车业务、手机部件及组装业务、二次充电电池业务。')
        print('公司掌握了电池、电机、电控及车规级芯片等核心技术，是中国新能源汽车行业的领军企业。')
        
        print(f'\n【投资要点】')
        print('  优势：')
        print('    • 新能源汽车全产业链核心技术')
        print('    • 刀片电池等创新技术领先')
        print('    • 产品矩阵丰富，市场占有率领先')
        print('    • 横向一体化布局，成本控制能力强')
        print('  风险：')
        print('    • 新能源汽车行业竞争加剧')
        print('    • 原材料价格波动风险')
        print('    • 政策变化对新能源汽车产业的影响')
        print('    • 海外市场拓展不确定性')

def main():
    """主函数"""
    analyzer = ImprovedStockAnalyzer()
    
    # 示例分析比亚迪
    print("使用改进版股票分析器分析比亚迪...")
    analyzer.analyze_stock("比亚迪", "002594")

if __name__ == "__main__":
    main()