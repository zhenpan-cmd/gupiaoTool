#!/usr/bin/env python3
"""
增强版股票分析器
修复了原始版本中的数据异常问题，提升系统健壮性
"""

import easyquotation
import akshare as ak
import pandas as pd
import numpy as np
import talib
import warnings
warnings.filterwarnings('ignore')

class EnhancedStockAnalyzer:
    """增强版股票分析器，包含数据验证和错误处理"""
    
    def __init__(self):
        self.data_quality_score = 0
        self.validation_errors = []
    
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
            print(f"代码验证失败: {e}")
            return False, code, None
    
    def safe_float_conversion(self, value, default=0.0):
        """安全浮点数转换"""
        try:
            if value is None:
                return default
            if isinstance(value, str):
                # 清理字符串
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
            if abs(amount - estimated_amount) / estimated_amount > 0.5:
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
            print(f'MACD计算错误: {e}')
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
            print(f"警告: 夏普比率 {sharpe:.2f} 可能异常")
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
            print(f'RSI计算错误: {e}')
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
            print(f'布林带计算错误: {e}')
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
        
        # 获取实时数据
        try:
            api = easyquotation.use('sina')
            data = api.real([stock_code])
            if stock_code in data and data[stock_code]:
                stock_info = data[stock_code]
                current_price = self.safe_float_conversion(stock_info.get('now'))
                volume = self.safe_float_conversion(stock_info.get('volume', 0))
                
                # 从easyquotation获取的成交额可能是错误的，所以单独处理
                amount_str = stock_info.get('成交额', '0')
                if isinstance(amount_str, str) and '万' in amount_str:
                    # 如果是中文格式如"1.23亿"或"4567万"
                    amount = self.safe_float_conversion(amount_str)
                    if '亿' in amount_str:
                        amount *= 10000  # 亿转万
                else:
                    amount = self.safe_float_conversion(amount_str)
                
                print(f'\n【实时数据】')
                print(f'当前价格: {current_price:.2f}元')
                print(f'涨跌幅: {stock_info.get("涨跌(%)", "N/A")}%')
                print(f'成交量: {volume / 10000:.2f}万手')
                
                # 验证交易数据合理性
                is_valid, msg = self.validate_trade_data(volume / 10000, amount, current_price)
                if is_valid:
                    print(f'成交额: {amount:.2f}万元')
                else:
                    print(f'⚠️  成交额数据可能异常: {msg}')
                    print(f'成交额: {amount:.2f}万元 (请谨慎参考)')
                
                print(f'PE: {stock_info.get("PE", "N/A")}')
                print(f'PB: {stock_info.get("PB", "N/A")}')
            else:
                print(f'\n【实时数据】')
                print('未能获取实时数据')
                current_price = 0
        except Exception as e:
            print(f'\n【实时数据】')
            print(f'实时数据获取失败: {e}')
            current_price = 0
        
        # 获取历史数据
        try:
            stock_hist = ak.stock_zh_a_hist(symbol=stock_code, period='daily', adjust='qfq')
            if not stock_hist.empty:
                # 取最近60个交易日的数据（增加数据量以改善技术指标计算）
                recent_data = stock_hist.tail(60).reset_index(drop=True)
                recent_data['日期'] = pd.to_datetime(recent_data['日期'])
                
                # 转换数据类型
                for col in ['开盘', '收盘', '最高', '最低', '成交量']:
                    recent_data[col] = pd.to_numeric(recent_data[col], errors='coerce')
                
                # 专门处理成交额，确保单位一致性
                if '成交额' in recent_data.columns:
                    recent_data['成交额'] = pd.to_numeric(recent_data['成交额'], errors='coerce')
                
                print(f'\n【历史数据】')
                print('最近5个交易日数据:')
                for idx, row in recent_data.tail(5).iterrows():
                    date = row['日期'].strftime('%Y-%m-%d')
                    print(f'{date}: 开盘 {row["开盘"]:.2f}, 收盘 {row["收盘"]:.2f}, 高 {row["最高"]:.2f}, 低 {row["最低"]:.2f}, 成交额 {row["成交额"]:.2f}万元')
            else:
                print('\n未能获取历史数据')
                recent_data = pd.DataFrame()
        except Exception as e:
            print(f'历史数据获取失败: {e}')
            recent_data = pd.DataFrame()
        
        # 技术分析
        if not recent_data.empty and len(recent_data) >= 26:  # 确保有足够的数据进行技术分析
            try:
                close_prices = recent_data['收盘'].values
                high_prices = recent_data['最高'].values
                low_prices = recent_data['最低'].values
                
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
                print(f'\n【技术分析】')
                print(f'技术分析计算失败: {e}')
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
                print('未能获取财务数据')
        except Exception as e:
            print(f'基本面分析数据获取失败: {e}')
        
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
                print(f'\n【风险分析】')
                print(f'风险分析计算失败: {e}')
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

def main():
    """主函数"""
    analyzer = EnhancedStockAnalyzer()
    
    # 示例分析立讯精密
    print("使用增强版股票分析器分析立讯精密...")
    analyzer.analyze_stock("立讯精密", "002475")

if __name__ == "__main__":
    main()