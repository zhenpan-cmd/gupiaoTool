#!/usr/bin/env python3
"""
股票分析工具 - 专为Clawdbot设计
"""

import sys
import json
import pandas as pd
import numpy as np
import akshare as ak
import baostock as bs
import warnings
warnings.filterwarnings('ignore')

class StockAnalyzer:
    """股票分析器"""
    
    def __init__(self):
        pass
    
    def analyze_single_stock(self, symbol, start_date='2024-06-01', end_date='2024-12-31'):
        """分析单个股票"""
        try:
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
            
            # 计算简单技术指标
            close_prices = result['close'].astype(float)
            latest_price = float(close_prices.iloc[-1])
            price_change_pct = float(((close_prices.iloc[-1] / close_prices.iloc[0]) - 1) * 100)
            
            # RSI (简化版)
            delta = close_prices.diff()
            gain = delta.where(delta > 0, 0).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss.replace(0, np.nan)
            rsi = 100 - (100 / (1 + rs))
            latest_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None
            
            # 简单趋势判断
            ma_short = close_prices.rolling(window=5).mean().iloc[-1]
            ma_long = close_prices.rolling(window=20).mean().iloc[-1]
            
            if not pd.isna(ma_short) and not pd.isna(ma_long):
                trend = "上升" if ma_short > ma_long else "下降"
            else:
                trend = "未知"
            
            # 返回结构化数据
            analysis_result = {
                "symbol": symbol,
                "name": stock_name,
                "current_price": latest_price,
                "price_change_pct": price_change_pct,
                "rsi": latest_rsi,
                "trend": trend,
                "data_points": len(result),
                "date_range": {
                    "start": str(result['date'].iloc[0]),
                    "end": str(result['date'].iloc[-1])
                }
            }
            
            return analysis_result
            
        except Exception as e:
            try:
                bs.logout()
            except:
                pass
            return {"error": f"分析过程中发生错误: {str(e)}"}
    
    def search_stock(self, keyword):
        """搜索股票"""
        try:
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
    analyzer = StockAnalyzer()
    
    if operation == "analyze":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "需要指定股票代码"}))
            return
        
        symbol = sys.argv[2]
        start_date = sys.argv[3] if len(sys.argv) > 3 else '2024-06-01'
        end_date = sys.argv[4] if len(sys.argv) > 4 else '2024-12-31'
        
        result = analyzer.analyze_single_stock(symbol, start_date, end_date)
        print(json.dumps(result, ensure_ascii=False))
        
    elif operation == "search":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "需要指定搜索关键词"}))
            return
        
        keyword = sys.argv[2]
        result = analyzer.search_stock(keyword)
        print(json.dumps(result, ensure_ascii=False))
        
    else:
        print(json.dumps({"error": "无效的操作类型"}))

if __name__ == "__main__":
    main()