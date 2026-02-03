# gupiaoTool

一个综合性的股票分析工具集，包含技术分析、基本面分析、风险管理和数据验证等功能。

## 项目特点

1. **安全性验证** - 内置股票代码验证机制，防止错误分析
2. **多维分析** - 技术指标、基本面、资金流向等多维度分析
3. **风险管控** - VaR、夏普比率等风险指标计算
4. **数据验证** - 多重数据源交叉验证

## 文件说明

- `advanced_stock_analyzer.py` - 高级股票分析器
- `validation_framework.py` - 股票分析验证框架
- `safe_stock_analyzer.py` - 安全的股票分析工具
- `stock_validation_check.py` - 股票代码验证检查
- `stock_analyzer_tool.py` - 股票分析工具
- `stock_analysis_wrapper.py` - 股票分析包装器
- `stock_analysis_quantitative_system_plan.md` - 量化系统规划文档
- `test_stock_analysis.py` - 股票分析测试脚本
- `test_stock_analysis_simple.py` - 简化版测试脚本
- `browser_automation_wrapper.py` - 浏览器自动化包装器
- `enhanced_browser_tool.py` - 增强浏览器工具

## 安装依赖

```bash
pip install akshare easyquotation pandas numpy talib scipy statsmodels matplotlib seaborn plotly
```

## 使用方法

```python
from safe_stock_analyzer import SafeStockAnalyzer

analyzer = SafeStockAnalyzer()
# 分析股票（自动验证代码）
result = analyzer.analyze_stock("比亚迪", "002594")
report = analyzer.generate_report("比亚迪", result)
print(report)
```

## 注意事项

- 本工具仅供学习和研究使用
- 投资有风险，决策需谨慎
- 所有分析结果应结合市场实际情况进行判断