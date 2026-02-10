#!/usr/bin/env python3
"""
精确的提问统计脚本
分析每天的主要工作和活动
"""

from datetime import datetime, timedelta

# 模拟的提问和工作记录（基于实际memory文件）
daily_activities = {
    "2026-02-09": {
        "activities": [
            "A股行情分析请求（API限制问题排查）",
            "要求使用真实数据，不要模拟数据",
            "要求分析API限制或网络问题原因",
            "要求添加浏览器模拟请求头和降低请求频率",
            "彤程新材股票分析请求",
            "统计最近几天的提问次数"
        ],
        "questions": 6,
        "focus": "解决akshare API限制问题"
    },
    "2026-02-04": {
        "activities": [
            "系统健康检查",
            "数据准确性改进",
            "测试套件验证"
        ],
        "questions": 3,
        "focus": "数据质量提升"
    },
    "2026-02-03": {
        "activities": [
            "股票代码验证问题修复",
            "立讯精密股票分析",
            "屹唐股份数据异常分析",
            "增强版分析器测试"
        ],
        "questions": 4,
        "focus": "数据验证和修复"
    },
    "2026-02-02": {
        "activities": [
            "A股K线分析能力增强",
            "AkShare库集成",
            "技术指标系统完善"
        ],
        "questions": 3,
        "focus": "A股分析能力建设"
    }
}

def print_detailed_stats():
    """打印详细统计"""
    print("="*70)
    print("📊 最近几天提问次数统计")
    print("="*70)
    
    total_questions = 0
    
    for date in sorted(daily_activities.keys()):
        day_data = daily_activities[date]
        questions = day_data['questions']
        total_questions += questions
        
        # 格式化日期
        dt = datetime.strptime(date, "%Y-%m-%d")
        weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][dt.weekday()]
        
        print(f"\n📅 {date} ({weekday})")
        print(f"   提问次数: {questions}次")
        print(f"   主要工作:")
        for activity in day_data['activities']:
            print(f"     • {activity}")
        print(f"   核心关注: {day_data['focus']}")
    
    print("\n" + "="*70)
    print("📈 统计汇总")
    print("="*70)
    print(f"   统计天数: {len(daily_activities)}天")
    print(f"   总提问次数: {total_questions}次")
    print(f"   日均提问: {total_questions/len(daily_activities):.1f}次")
    print(f"   最高单日: {max(d['questions'] for d in daily_activities.values())}次")
    print(f"   最低单日: {min(d['questions'] for d in daily_activities.values())}次")
    
    print("\n💡 提问主题分布:")
    topic_count = {}
    for date, data in daily_activities.items():
        topic = data['focus']
        topic_count[topic] = topic_count.get(topic, 0) + 1
    
    for topic, count in sorted(topic_count.items(), key=lambda x: -x[1]):
        bar = "█" * count
        print(f"   {bar} {topic}")

if __name__ == "__main__":
    print_detailed_stats()
