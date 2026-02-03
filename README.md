# gupiaoTool

一个综合性的股票分析工具集，包含技术分析、基本面分析、风险管理和数据验证等功能。

## 项目特点

1. **安全性验证** - 内置股票代码验证机制，防止错误分析
2. **多维分析** - 技术指标、基本面、资金流向等多维度分析
3. **风险管控** - VaR、夏普比率等风险指标计算
4. **数据验证** - 多重数据源交叉验证

## 项目结构

```
├── advanced_stock_analyzer.py     # 高级股票分析器
├── safe_stock_analyzer.py         # 安全的股票分析工具
├── validation_framework.py        # 股票分析验证框架
├── stock_validation_check.py      # 股票代码验证检查
├── stock_analyzer_tool.py         # 股票分析工具
├── stock_analysis_wrapper.py      # 股票分析包装器
├── browser_automation_wrapper.py  # 浏览器自动化包装器
├── enhanced_browser_tool.py       # 增强浏览器工具
├── stock_analysis_quantitative_system_plan.md  # 量化系统规划文档
├── test_stock_analysis.py         # 股票分析测试脚本
├── test_stock_analysis_simple.py  # 简化版测试脚本
├── baidu_screenshot.png           # 项目截图
├── canvas/                        # Web界面相关
│   └── index.html
├── memory/                        # 项目记忆文件
│   ├── 2024-12-17.md
│   ├── 2026-01-30.md
│   ├── 2026-02-02.md
│   └── 2026-02-03.md
├── AGENTS.md                      # 代理配置文件
├── SOUL.md                        # 个性定义文件
├── USER.md                        # 用户信息文件
├── TOOLS.md                       # 工具配置文件
├── BOOTSTRAP.md                   # 启动配置文件
├── HEARTBEAT.md                   # 心跳配置文件
├── IDENTITY.md                    # 身份定义文件
├── package.json                   # Node.js配置文件
├── package-lock.json              # 依赖锁定文件
└── README.md                      # 项目说明文档
```

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

## 核心功能

### 1. 代码验证机制
- 自动验证股票代码与公司名称匹配
- 防止错误代码导致的错误分析
- 维护已知错误代码黑名单

### 2. 技术分析
- MACD、RSI、布林带等技术指标
- KDJ、威廉指标等辅助指标
- 可视化图表展示

### 3. 基本面分析
- 财务指标分析（净利润、ROE、毛利率等）
- 估值指标（PE、PB等）
- 财务健康度评估

### 4. 风险管理
- VaR（风险价值）计算
- 夏普比率分析
- 最大回撤计算
- 波动率分析

## 注意事项

- 本工具仅供学习和研究使用
- 投资有风险，决策需谨慎
- 所有分析结果应结合市场实际情况进行判断
- 使用前请确保网络连接稳定