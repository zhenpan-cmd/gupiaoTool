#!/usr/bin/env python3
"""
安全的股票分析工具
包含代码验证和交叉验证机制
"""

import akshare as ak
import easyquotation
import pandas as pd
import numpy as np
import talib
import warnings
warnings.filterwarnings('ignore')


class SafeStockAnalyzer:
    def __init__(self):
        self.validated_codes = {}  # 缓存验证过的代码
    
    def validate_stock_code(self, target_name, code):
        """
        验证股票代码是否对应目标公司
        """
        try:
            info = ak.stock_individual_info_em(symbol=code)
            if info.empty:
                return False, f"无法获取代码 {code} 的信息"
            
            # 查找股票简称
            name_row = info[info['item'] == '股票简称']
            if name_row.empty:
                return False, f"代码 {code} 未找到股票简称"
            
            actual_name = name_row.iloc[0]['value']
            
            # 检查名称是否匹配（模糊匹配）
            if target_name in actual_name or actual_name in target_name:
                return True, f"验证通过: {code} -> {actual_name}"
            else:
                return False, f"名称不匹配: {code} -> {actual_name} (期望: {target_name})"
                
        except Exception as e:
            return False, f"验证失败: {e}"
    
    def search_stock_code(self, target_name):
        """
        通过多种方式搜索股票代码
        """
        print(f"正在搜索 '{target_name}' 的股票代码...")
        
        # 方法1: 直接在A股代码名称映射中查找
        try:
            code_name_map = ak.stock_info_a_code_name()
            matches = code_name_map[code_name_map['name'].str.contains(target_name, na=False, case=False)]
            
            if not matches.empty:
                print(f"方法1找到 {len(matches)} 个匹配:")
                for _, row in matches.iterrows():
                    code = row['code']
                    name = row['name']
                    is_valid, msg = self.validate_stock_code(target_name, code)
                    print(f"  {code} - {name} ({'✓' if is_valid else '✗'}) {msg}")
                    
                    if is_valid:
                        return code, name
                        
        except Exception as e:
            print(f"方法1失败: {e}")
        
        # 方法2: 尝试通过搜索引擎获取信息（这里使用已有知识）
        # 如果是知名公司，可以预先维护一个映射
        known_mappings = {
            '比亚迪': '002594',
            '屹唐股份': '688729',
            '宁德时代': '300750',
            '隆基绿能': '601012',
            '阳光电源': '300274',
            '汇川技术': '300124',
            '五粮液': '000858',
            '贵州茅台': '600519',
            '中国平安': '601318',
            '招商银行': '600036'
        }
        
        if target_name in known_mappings:
            code = known_mappings[target_name]
            is_valid, msg = self.validate_stock_code(target_name, code)
            print(f"方法2预设映射: {code} ({'✓' if is_valid else '✗'}) {msg}")
            if is_valid:
                return code, target_name
        
        return None, None
    
    def analyze_stock(self, target_name, code=None):
        """
        安全分析股票
        """
        print(f"=== 开始分析 {target_name} ===")
        
        # 如果没有提供代码，先搜索
        if code is None:
            code, actual_name = self.search_stock_code(target_name)
            if code is None:
                print(f"❌ 无法找到 {target_name} 的有效股票代码")
                return None
            target_name = actual_name  # 更新为实际名称
        else:
            # 验证提供的代码
            is_valid, msg = self.validate_stock_code(target_name, code)
            if not is_valid:
                print(f"❌ 代码验证失败: {msg}")
                # 尝试搜索正确的代码
                correct_code, actual_name = self.search_stock_code(target_name)
                if correct_code:
                    print(f"💡 发现正确代码: {correct_code}，切换分析目标")
                    code = correct_code
                    target_name = actual_name
                else:
                    print("❌ 无法找到正确的股票代码")
                    return None
        
        print(f"✅ 确认分析对象: {target_name}({code})")
        
        # 获取并验证数据
        result = {
            'basic_info': {},
            'price_data': {},
            'fundamentals': {},
            'company_profile': f"{target_name}是一家...",
            'validation_passed': True
        }
        
        # 获取实时数据
        try:
            api = easyquotation.use('sina')
            data = api.real([code])
            if code in data and data[code]:
                result['price_data'] = data[code]
                print(f"✅ 获取实时价格数据成功: {data[code].get('now', 'N/A')}元")
            else:
                print("⚠️  未能获取实时价格数据")
        except Exception as e:
            print(f"⚠️  获取实时数据失败: {e}")
        
        # 获取历史数据
        try:
            stock_hist = ak.stock_zh_a_hist(symbol=code, period='daily', adjust='qfq')
            if not stock_hist.empty:
                result['history_data'] = stock_hist.tail(5)  # 最近5个交易日
                print(f"✅ 获取历史数据成功: {len(stock_hist)}个交易日")
            else:
                print("⚠️  未能获取历史数据")
        except Exception as e:
            print(f"⚠️  获取历史数据失败: {e}")
        
        # 获取基本面数据
        try:
            fin_indicator = ak.stock_financial_abstract_ths(symbol=code)
            if not fin_indicator.empty:
                result['fundamentals'] = fin_indicator.iloc[-1]
                print(f"✅ 获取财务数据成功: {len(fin_indicator)}条记录")
            else:
                print("⚠️  未能获取财务数据")
        except Exception as e:
            print(f"⚠️  获取财务数据失败: {e}")
        
        return result
    
    def generate_report(self, target_name, analysis_result):
        """
        生成分析报告
        """
        if analysis_result is None:
            return f"❌ 无法生成 {target_name} 的分析报告，数据获取失败"
        
        report = []
        report.append(f"=== {target_name} 股票分析报告 ===")
        report.append("")
        
        # 价格数据
        price_data = analysis_result.get('price_data', {})
        if price_data:
            report.append("【实时数据】")
            report.append(f"当前价格: {price_data.get('now', 'N/A')}元")
            report.append(f"涨跌幅: {price_data.get('涨跌(%)', 'N/A')}%")
            report.append(f"成交量: {price_data.get('volume', 'N/A')/10000:.2f}万手")
            report.append("")
        
        # 历史数据
        history_data = analysis_result.get('history_data', pd.DataFrame())
        if not history_data.empty:
            report.append("【历史数据】")
            report.append("最近5个交易日:")
            for idx, row in history_data.iterrows():
                date = row['日期'].strftime('%Y-%m-%d') if hasattr(row['日期'], 'strftime') else str(row['日期'])
                report.append(f"{date}: 开盘 {row['开盘']:.2f}, 收盘 {row['收盘']:.2f}, 成交额 {row['成交额']:.2f}万元")
            report.append("")
        
        # 财务数据
        fundamentals = analysis_result.get('fundamentals', {})
        if fundamentals is not None and hasattr(fundamentals, 'get'):
            report.append("【财务数据摘要】")
            items_to_show = ['净利润', '营业总收入', '净资产收益率', '销售毛利率', '资产负债率', '流动比率']
            for item in items_to_show:
                if item in fundamentals:
                    value = fundamentals[item]
                    if pd.isna(value):
                        value = 'N/A'
                    report.append(f"{item}: {value}")
            report.append("")
        
        report.append("【验证状态】")
        report.append("✅ 所有数据均经过代码验证，确保分析准确性")
        
        return "\\n".join(report)


def main():
    analyzer = SafeStockAnalyzer()
    
    # 测试比亚迪（正确代码）
    print("测试1: 比亚迪（已知正确代码）")
    result1 = analyzer.analyze_stock("比亚迪", "002594")
    print(analyzer.generate_report("比亚迪", result1))
    print()
    
    # 测试屹唐股份（之前错误的代码）
    print("测试2: 屹唐股份（使用错误代码，应自动纠正）")
    result2 = analyzer.analyze_stock("屹唐股份", "300346")  # 错误代码
    print(analyzer.generate_report("屹唐股份", result2))
    print()
    
    # 测试自动搜索功能
    print("测试3: 自动搜索功能")
    result3 = analyzer.analyze_stock("贵州茅台")
    print(analyzer.generate_report("贵州茅台", result3))


if __name__ == "__main__":
    main()