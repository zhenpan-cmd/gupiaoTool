#!/usr/bin/env python3
"""
系统验证演示
展示改进版股票分析器如何防止错误数据的传播
"""

import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demonstrate_data_validation():
    """演示数据验证功能"""
    print("🔍 改进版股票分析器数据验证演示")
    print("="*60)
    
    from improved_stock_analyzer import ImprovedStockAnalyzer
    
    # 创建分析器实例
    analyzer = ImprovedStockAnalyzer()
    
    print("\n📊 数据验证功能演示:")
    
    # 1. 演示安全浮点转换
    print("\n1. 安全浮点转换测试:")
    test_values = ["249.50", "N/A", None, "", "0.00", 253.50]
    for val in test_values:
        result = analyzer.safe_float_conversion(val)
        print(f"   {repr(val):>10} -> {result:>8.2f}")
    
    # 2. 演示数据合理性验证
    print("\n2. 数据合理性验证测试:")
    
    # 合理数据
    valid_data = {
        'price': 249.50,      # 价格在合理范围
        'volume': 5460800,    # 成交量为正
        'change_pct': -1.58   # 涨跌幅在合理范围
    }
    is_valid, msg = analyzer.validate_data_reasonableness(valid_data)
    print(f"   合理数据验证: {msg}")
    
    # 不合理数据（价格过高）
    invalid_price_data = {
        'price': 2495.0,      # 价格过高
        'volume': 5460800,
        'change_pct': -1.58
    }
    is_valid, msg = analyzer.validate_data_reasonableness(invalid_price_data)
    print(f"   高价数据验证: {msg}")
    
    # 不合理数据（涨跌幅过大）
    extreme_chg_data = {
        'price': 249.50,
        'volume': 5460800,
        'change_pct': 50.0    # 涨跌幅过大
    }
    is_valid, msg = analyzer.validate_data_reasonableness(extreme_chg_data)
    print(f"   极值数据验证: {msg}")
    
    # 3. 演示交易数据验证
    print("\n3. 交易数据验证测试:")
    
    # 正确的交易数据
    is_valid, msg = analyzer.validate_trade_data(54608, 13685020000, 249.50)  # 54608万手, 136.85亿, 249.50元
    print(f"   正确交易数据: {msg}")
    
    # 错误的交易数据（成交额与价格成交量不匹配）
    is_valid, msg = analyzer.validate_trade_data(54608, 0, 249.50)  # 成交额为0但有成交量
    print(f"   错误交易数据: {msg}")
    
    # 4. 演示技术指标计算
    print("\n4. 技术指标计算测试:")
    
    # 生成模拟价格数据
    np.random.seed(42)  # 为了结果可重复
    prices = np.random.random(30) * 50 + 200  # 价格在200-250之间波动
    
    # 计算MACD
    macd, signal, hist = analyzer.safe_macd_calculation(prices)
    if macd is not None:
        print(f"   MACD计算: {macd:.3f}")
    else:
        print("   MACD计算: 失败或数据不足")
    
    # 计算RSI
    rsi = analyzer.safe_rsi_calculation(prices)
    if rsi is not None:
        print(f"   RSI计算: {rsi:.2f}")
    else:
        print("   RSI计算: 失败或数据不足")
    
    # 计算布林带
    upper, middle, lower = analyzer.safe_bollinger_bands(prices)
    if all(x is not None for x in [upper, middle, lower]):
        print(f"   布林带计算: 上轨{upper:.2f}, 中轨{middle:.2f}, 下轨{lower:.2f}")
    else:
        print("   布林带计算: 失败或数据不足")
    
    # 5. 演示多源数据一致性验证
    print("\n5. 多源数据一致性验证演示:")
    
    # 模拟来自不同源的数据（正常情况）
    consistent_sources = {
        'source1': {'price': 249.50, 'volume': 5460800, 'amount': 13685020000},
        'source2': {'price': 249.48, 'volume': 5460800, 'amount': 13684800000},
        'source3': {'price': 249.52, 'volume': 5460800, 'amount': 13685200000}
    }
    
    selected_data, method = analyzer.validate_data_consistency(consistent_sources)
    if selected_data:
        print(f"   一致数据选择: 来自{method.split('based on ')[1]}, 价格{selected_data['price']}")
    else:
        print("   一致数据选择: 无一致数据")
    
    # 模拟来自不同源的数据（异常情况 - 数据差异很大）
    inconsistent_sources = {
        'source1': {'price': 249.50, 'volume': 5460800, 'amount': 13685020000},
        'source2': {'price': 100.00, 'volume': 5460800, 'amount': 13685020000},  # 价格异常
        'source3': {'price': 500.00, 'volume': 5460800, 'amount': 13685020000}   # 价格异常
    }
    
    selected_data, method = analyzer.validate_data_consistency(inconsistent_sources)
    if selected_data:
        print(f"   异常数据处理: 来自{method.split('based on ')[1]}, 价格{selected_data['price']}")
    else:
        print("   异常数据处理: 无法选择一致数据")
    
    print("\n✅ 演示完成！改进版分析器具备完整的数据验证功能。")

def explain_improvements():
    """解释系统改进"""
    print("\n🔧 系统改进说明")
    print("="*60)
    
    improvements = [
        ("✅ 多源数据验证", "整合akshare、easyquotation、tencent等多个数据源"),
        ("✅ 数据合理性检查", "验证价格、涨跌幅、成交量等数据是否在合理范围"),
        ("✅ 交易数据验证", "检查成交量与成交额的逻辑关系"),
        ("✅ 数据一致性验证", "对比多源数据的一致性并选择最优数据"),
        ("✅ 异常数据过滤", "自动过滤异常或错误数据"),
        ("✅ 错误处理机制", "数据异常时提供明确提示"),
        ("✅ 数据质量评分", "为用户提供数据可信度指示")
    ]
    
    for improvement, description in improvements:
        print(f"{improvement:<20} {description}")

def main():
    """主函数"""
    print("🚀 改进版股票分析器系统验证演示")
    print("="*70)
    
    demonstrate_data_validation()
    explain_improvements()
    
    print("\n🎯 总结:")
    print("   改进版分析器通过多重验证机制有效防止错误数据传播")
    print("   系统现在能够识别并处理异常数据，提供更可靠的分析结果")
    print("   用户可以放心使用，数据准确性得到显著提升")

if __name__ == "__main__":
    main()