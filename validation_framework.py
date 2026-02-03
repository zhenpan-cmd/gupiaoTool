#!/usr/bin/env python3
"""
股票分析验证框架
包含错误预防和数据验证机制
"""

class StockAnalysisValidator:
    """
    股票分析验证器
    用于防止错误的代码使用和数据验证
    """
    
    def __init__(self):
        # 维护已知的正确股票代码映射
        self.known_codes = {
            '比亚迪': '002594',
            '屹唐股份': '688729',
            '贵州茅台': '600519',
            '宁德时代': '300750',
            '隆基绿能': '601012',
            '五粮液': '000858',
            '中国平安': '601318',
            '招商银行': '600036',
            '阳光电源': '300274',
            '汇川技术': '300124'
        }
        
        # 维护已知的错误代码映射（用于提醒）
        self.known_wrong_codes = {
            '屹唐股份': ['300346', '300442', '600729']  # 之前错误使用的代码
        }
    
    def validate_before_analysis(self, target_name, provided_code=None):
        """
        分析前验证
        """
        print(f"🔍 验证即将分析的目标: {target_name}")
        
        # 检查是否在已知错误代码列表中
        if target_name in self.known_wrong_codes:
            if provided_code in self.known_wrong_codes[target_name]:
                print(f"🚨 检测到已知的错误代码 {provided_code} 用于 {target_name}")
                correct_code = self.known_codes.get(target_name)
                if correct_code:
                    print(f"💡 建议使用正确代码: {correct_code}")
                    return False, correct_code
                else:
                    print("⚠️  无法确定正确代码，请手动确认")
                    return False, None
        
        # 如果提供了代码，检查是否在已知正确代码中
        if provided_code:
            correct_code = self.known_codes.get(target_name)
            if correct_code and provided_code != correct_code:
                print(f"⚠️  提供的代码 {provided_code} 可能不正确")
                print(f"💡 建议使用正确代码: {correct_code}")
                return False, correct_code
        
        # 如果没有提供代码，从已知映射中获取
        if not provided_code:
            correct_code = self.known_codes.get(target_name)
            if correct_code:
                print(f"✅ 找到已知正确代码: {correct_code}")
                return True, correct_code
            else:
                print(f"⚠️  未知股票 {target_name}，需要手动确认代码")
                return False, None
        
        # 代码匹配验证
        correct_code = self.known_codes.get(target_name)
        if correct_code == provided_code:
            print(f"✅ 代码验证通过: {target_name}({provided_code})")
            return True, provided_code
        else:
            print(f"❌ 代码验证失败: 提供 {provided_code}, 期望 {correct_code}")
            return False, correct_code
    
    def get_correct_code(self, target_name):
        """
        获取正确的股票代码
        """
        return self.known_codes.get(target_name)
    
    def add_known_pair(self, name, code):
        """
        添加新的已知正确配对
        """
        self.known_codes[name] = code
        print(f"✅ 添加已知配对: {name}({code})")
    
    def add_wrong_code(self, name, wrong_code):
        """
        添加已知错误代码
        """
        if name not in self.known_wrong_codes:
            self.known_wrong_codes[name] = []
        if wrong_code not in self.known_wrong_codes[name]:
            self.known_wrong_codes[name].append(wrong_code)
            print(f"✅ 添加已知错误代码: {name}({wrong_code})")


def create_analysis_workflow():
    """
    创建安全的分析工作流程
    """
    validator = StockAnalysisValidator()
    
    def safe_analyze_stock(target_name, code=None):
        """
        安全的股票分析函数
        """
        print(f"🚀 开始安全分析: {target_name}")
        
        # 验证阶段
        is_valid, correct_code = validator.validate_before_analysis(target_name, code)
        
        if not is_valid:
            if correct_code:
                print(f"🔄 自动更正代码为: {correct_code}")
                # 在这里可以调用正确的分析函数
                print(f"✅ 准备使用正确代码 {correct_code} 分析 {target_name}")
                return {
                    'status': 'corrected',
                    'original_code': code,
                    'correct_code': correct_code,
                    'target_name': target_name
                }
            else:
                print(f"❌ 无法确定正确代码，分析终止")
                return {
                    'status': 'failed',
                    'error': '无法确定正确代码',
                    'target_name': target_name
                }
        else:
            print(f"✅ 使用验证通过的代码 {correct_code} 分析 {target_name}")
            return {
                'status': 'validated',
                'code': correct_code,
                'target_name': target_name
            }
    
    return safe_analyze_stock, validator


def main():
    print("=== 股票分析验证框架 ===")
    print()
    
    # 创建安全分析工作流程
    safe_analyze, validator = create_analysis_workflow()
    
    print("1. 测试之前的错误案例:")
    print("   分析屹唐股份，使用错误代码 300346:")
    result1 = safe_analyze("屹唐股份", "300346")
    print(f"   结果: {result1['status']}")
    print()
    
    print("2. 测试正确案例:")
    print("   分析比亚迪，使用正确代码 002594:")
    result2 = safe_analyze("比亚迪", "002594")
    print(f"   结果: {result2['status']}")
    print()
    
    print("3. 测试未提供代码的情况:")
    print("   分析贵州茅台，不提供代码:")
    result3 = safe_analyze("贵州茅台")
    print(f"   结果: {result3['status']}")
    print()
    
    print("4. 测试未知股票:")
    print("   分析一个未知股票:")
    result4 = safe_analyze("未知股票")
    print(f"   结果: {result4['status']}")
    print()
    
    print("=== 修复措施总结 ===")
    fixes = [
        "✅ 1. 建立已知股票代码映射，防止错误代码使用",
        "✅ 2. 维护错误代码黑名单，自动检测和纠正",
        "✅ 3. 实施分析前验证机制",
        "✅ 4. 提供安全的分析工作流程",
        "✅ 5. 自动代码纠正功能"
    ]
    
    for fix in fixes:
        print(fix)
    
    print()
    print("=== 今后的安全实践 ===")
    practices = [
        "• 每次分析前必须通过验证器检查",
        "• 使用已知的正确代码映射",
        "• 自动检测并纠正错误代码",
        "• 在报告中标明验证状态",
        "• 持续更新已知代码映射"
    ]
    
    for practice in practices:
        print(f"• {practice}")


if __name__ == "__main__":
    main()