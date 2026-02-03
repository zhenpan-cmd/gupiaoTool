#!/usr/bin/env python3
"""
高级股票分析工具 - 为Clawdbot设计
"""

import sys
import json
import pandas as pd
import numpy as np
import akshare as ak
import baostock as bs
import warnings
warnings.filterwarnings('ignore')

class AdvancedStockAnalyzer:
    """高级股票分析器"""
    
    def __init__(self):
        pass
    
    def calculate_technical_indicators(self, df):
        """计算技术指标"""
        df = df.copy()
        close = df['close'].astype(float)
        high = df['high'].astype(float)
        low = df['low'].astype(float)
        
        # 移动平均线
        df['ma_5'] = close.rolling(window=5).mean()
        df['ma_10'] = close.rolling(window=10).mean()
        df['ma_20'] = close.rolling(window=20).mean()
        
        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss.replace(0, np.nan)
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = close.ewm(span=12).mean()
        exp2 = close.ewm(span=26).mean()
        df['dif'] = exp1 - exp2
        df['dea'] = df['dif'].ewm(span=9).mean()
        df['macd'] = (df['dif'] - df['dea']) * 2
        
        # 布林带
        df['bb_middle'] = close.rolling(window=20).mean()
        bb_std = close.rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        
        # 波动率
        df['volatility'] = close.pct_change().rolling(window=20).std() * np.sqrt(252)
        
        return df
    
    def analyze_single_stock(self, symbol, start_date='2024-06-01', end_date='2024-12-31'):
        """深度分析单个股票"""
        try:
            import io
            import sys
            from contextlib import redirect_stdout, redirect_stderr
            
            # 捕获baostock的输出
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                # 登录baostock
                bs.login()
                
                # 获取数据
                rs = bs.query_history_k_data_plus(
                    symbol,
                    'date,code,open,high,low,close,volume',
                    start_date=start_date,
                    end_date=end_date,
                    frequency='d',
                    adjustflag='3'
                )
                
                if rs.error_code != '0':
                    bs.logout()
                    return {"error": f"获取数据失败: {rs.error_msg}"}
                
                data_list = []
                while (rs.error_code == '0') & (rs.next()):
                    data_list.append(rs.get_row_data())
                
                if not data_list:
                    return {"error": "未获取到数据"}
                
                result = pd.DataFrame(data_list, columns=rs.fields)
                
                # 转换数据类型
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    result[col] = pd.to_numeric(result[col], errors='coerce')
                
                # 删除包含NaN的行
                result = result.dropna()
                
                if result.empty:
                    return {"error": "数据清洗后无有效数据"}
                
                # 获取股票名称
                rs_name = bs.query_stock_basic(code=symbol)
                if rs_name.error_code == '0':
                    name_list = []
                    while (rs_name.error_code == '0') & (rs_name.next()):
                        name_list.append(rs_name.get_row_data())
                    if name_list:
                        stock_name = name_list[0][1]  # code_name
                    else:
                        stock_name = symbol
                else:
                    stock_name = symbol
                
                bs.logout()
                
                # 计算技术指标
                result = self.calculate_technical_indicators(result)
                
                # 获取最新数据
                latest = result.iloc[-1]
                prev = result.iloc[-2] if len(result) > 1 else result.iloc[-1]
                
                # 计算各种指标
                current_price = float(latest['close'])
                price_change_pct = float(((result['close'].iloc[-1] / result['close'].iloc[0]) - 1) * 100)
                rsi = float(latest['rsi']) if not pd.isna(latest['rsi']) else None
                volatility = float(latest['volatility']) if not pd.isna(latest['volatility']) else None
                
                # 趋势判断
                ma_short = float(latest['ma_5']) if not pd.isna(latest['ma_5']) else None
                ma_long = float(latest['ma_20']) if not pd.isna(latest['ma_20']) else None
                
                if ma_short and ma_long:
                    trend = "上升" if ma_short > ma_long else "下降"
                else:
                    trend = "未知"
                
                # MACD状态
                dif = float(latest['dif']) if not pd.isna(latest['dif']) else None
                dea = float(latest['dea']) if not pd.isna(latest['dea']) else None
                prev_dif = float(prev['dif']) if not pd.isna(prev['dif']) else None
                prev_dea = float(prev['dea']) if not pd.isna(prev['dea']) else None
                
                macd_state = "未知"
                if dif is not None and dea is not None:
                    if dif > dea and (prev_dif <= prev_dea if prev_dif is not None and prev_dea is not None else False):
                        macd_state = "金叉"
                    elif dif < dea and (prev_dif >= prev_dea if prev_dif is not None and prev_dea is not None else False):
                        macd_state = "死叉"
                    elif dif > dea:
                        macd_state = "多头"
                    else:
                        macd_state = "空头"
                
                # 布林带位置
                bb_position = "未知"
                if not pd.isna(latest['bb_upper']) and not pd.isna(latest['bb_lower']):
                    if current_price > latest['bb_upper']:
                        bb_position = "突破上轨"
                    elif current_price < latest['bb_lower']:
                        bb_position = "跌破下轨"
                    elif current_price > latest['bb_middle']:
                        bb_position = "中轨上方"
                    else:
                        bb_position = "中轨下方"
                
                # 支撑阻力位
                recent_high = float(result['high'].tail(20).max())
                recent_low = float(result['low'].tail(20).min())
                
                # 返回详细分析结果
                analysis_result = {
                    "symbol": symbol,
                    "name": stock_name,
                    "basic_info": {
                        "current_price": current_price,
                        "price_change_pct": price_change_pct,
                        "data_points": len(result),
                        "date_range": {
                            "start": str(result['date'].iloc[0]),
                            "end": str(result['date'].iloc[-1])
                        }
                    },
                    "technical_indicators": {
                        "rsi": rsi,
                        "volatility": volatility,
                        "trend": trend,
                        "macd_state": macd_state,
                        "bollinger_band_position": bb_position
                    },
                    "support_resistance": {
                        "resistance": recent_high,
                        "support": recent_low
                    },
                    "moving_averages": {
                        "ma_5": ma_short,
                        "ma_10": float(latest['ma_10']) if not pd.isna(latest['ma_10']) else None,
                        "ma_20": ma_long
                    }
                }
                
                return analysis_result
                
        except Exception as e:
            try:
                bs.logout()
            except:
                pass
            return {"error": f"分析过程中发生错误: {str(e)}"}
    
    def compare_stocks(self, symbols, start_date='2024-06-01', end_date='2024-12-31'):
        """比较多个股票"""
        try:
            comparison_results = {}
            
            for symbol in symbols:
                result = self.analyze_single_stock(symbol, start_date, end_date)
                if "error" not in result:
                    comparison_results[symbol] = {
                        "name": result["name"],
                        "current_price": result["basic_info"]["current_price"],
                        "price_change_pct": result["basic_info"]["price_change_pct"],
                        "rsi": result["technical_indicators"]["rsi"],
                        "volatility": result["technical_indicators"]["volatility"]
                    }
            
            return {"comparison": comparison_results}
            
        except Exception as e:
            return {"error": f"比较过程中发生错误: {str(e)}"}
    
    def search_stock(self, keyword):
        """搜索股票"""
        try:
            import io
            import sys
            from contextlib import redirect_stdout, redirect_stderr
            
            # 捕获baostock的输出
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                bs.login()
                rs = bs.query_stock_basic(code_name=keyword)
                
                if rs.error_code != '0':
                    bs.logout()
                    return {"error": f"搜索失败: {rs.error_msg}"}
                
                stocks = []
                while (rs.error_code == '0') & (rs.next()):
                    row_data = rs.get_row_data()
                    stocks.append({
                        "code": row_data[0],
                        "name": row_data[1],
                        "ipo_date": row_data[2],
                        "outstanding_share": row_data[3],
                        "totals": row_data[4]
                    })
                
                bs.logout()
                return {"stocks": stocks[:10]}  # 限制返回前10个结果
            
        except Exception as e:
            try:
                bs.logout()
            except:
                pass
            return {"error": f"搜索过程中发生错误: {str(e)}"}

def main():
    """主函数，处理命令行输入"""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "需要指定操作类型"}))
        return
    
    operation = sys.argv[1]
    analyzer = AdvancedStockAnalyzer()
    
    if operation == "analyze":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "需要指定股票代码"}))
            return
        
        symbol = sys.argv[2]
        start_date = sys.argv[3] if len(sys.argv) > 3 else '2024-06-01'
        end_date = sys.argv[4] if len(sys.argv) > 4 else '2024-12-31'
        
        result = analyzer.analyze_single_stock(symbol, start_date, end_date)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    elif operation == "compare":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "需要指定至少一个股票代码"}))
            return
        
        symbols = sys.argv[2].split(',')  # 以逗号分隔的股票代码
        start_date = sys.argv[3] if len(sys.argv) > 3 else '2024-06-01'
        end_date = sys.argv[4] if len(sys.argv) > 4 else '2024-12-31'
        
        result = analyzer.compare_stocks(symbols, start_date, end_date)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    elif operation == "search":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "需要指定搜索关键词"}))
            return
        
        keyword = sys.argv[2]
        result = analyzer.search_stock(keyword)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    else:
        print(json.dumps({"error": "无效的操作类型。支持: analyze, compare, search"}))

if __name__ == "__main__":
    main()