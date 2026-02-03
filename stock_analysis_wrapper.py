#!/usr/bin/env python3
"""
股票分析工具包装器
"""

import subprocess
import json
import sys

def run_stock_analysis(operation, *args):
    """
    运行股票分析工具
    :param operation: 操作类型 (analyze, compare, search)
    :param args: 操作参数
    :return: 分析结果
    """
    cmd = ["python3", "/root/clawd/advanced_stock_analyzer.py", operation] + list(args)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            return {"error": f"执行失败: {result.stderr}"}
        
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"error": f"解析输出失败: {result.stdout}"}
    
    except subprocess.TimeoutExpired:
        return {"error": "操作超时"}
    except Exception as e:
        return {"error": f"执行异常: {str(e)}"}

def analyze_stock(symbol, start_date='2024-06-01', end_date='2024-12-31'):
    """分析单个股票"""
    return run_stock_analysis("analyze", symbol, start_date, end_date)

def compare_stocks(symbols, start_date='2024-06-01', end_date='2024-12-31'):
    """比较多个股票"""
    symbols_str = ','.join(symbols)
    return run_stock_analysis("compare", symbols_str, start_date, end_date)

def search_stocks(keyword):
    """搜索股票"""
    return run_stock_analysis("search", keyword)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 stock_analysis_wrapper.py <operation> [args...]")
        print("Operations: analyze, compare, search")
        sys.exit(1)
    
    operation = sys.argv[1]
    args = sys.argv[2:]
    
    result = run_stock_analysis(operation, *args)
    print(json.dumps(result, ensure_ascii=False, indent=2))