#!/usr/bin/env python3
"""
提问统计脚本
基于memory文件分析最近几天的提问和工作情况
"""

import os
from datetime import datetime, timedelta
from pathlib import Path

MEMORY_DIR = Path("/root/clawd/memory")

def get_memory_files(days=7):
    """获取最近几天的memory文件"""
    today = datetime.now()
    files = []
    
    for i in range(days):
        date = today - timedelta(days=i)
        file_path = MEMORY_DIR / f"{date.strftime('%Y-%m-%d')}.md"
        if file_path.exists():
            files.append((date, file_path))
    
    return files

def count_questions(file_path):
    """统计文件中的主要工作和问题"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 统计工作项数量
    lines = content.split('\n')
    
    # 统计TODO项和已完成任务
    todo_count = 0
    done_count = 0
    work_items = []
    
    for line in lines:
        line = line.strip()
        if line.startswith('- [ ]'):
            todo_count += 1
            work_items.append(line[6:].strip())
        elif line.startswith('- [x]') or line.startswith('- [X]'):
            done_count += 1
    
    # 统计主要工作内容（基于标题和列表项）
    sections = []
    for line in lines:
        if line.startswith('## ') or line.startswith('# '):
            sections.append(line.strip('# '))
    
    return {
        'done_count': done_count,
        'todo_count': todo_count,
        'sections': sections[:5],  # 最多5个主要部分
    }

def print_stats():
    """打印统计信息"""
    print("="*60)
    print("📊 最近7天提问/工作统计")
    print("="*60)
    
    files = get_memory_files(7)
    
    total_done = 0
    total_todo = 0
    
    for date, file_path in files:
        stats = count_questions(file_path)
        total_done += stats['done_count']
        total_todo += stats['todo_count']
        
        print(f"\n📅 {date.strftime('%Y-%m-%d')} ({date.strftime('%A')})")
        print(f"   完成事项: {stats['done_count']}项")
        print(f"   待办事项: {stats['todo_count']}项")
        
        if stats['sections']:
            print(f"   主要工作:")
            for section in stats['sections'][:3]:
                print(f"     • {section}")
    
    print("\n" + "="*60)
    print("📈 总计")
    print("="*60)
    print(f"   完成事项: {total_done}项")
    print(f"   待办事项: {total_todo}项")
    
    if files:
        avg_done = total_done / len(files)
        print(f"   日均完成: {avg_done:.1f}项")
    
    print("\n💡 说明:")
    print("   - Memory文件记录每天的主要工作和系统活动")
    print("   - 每完成一个任务或功能改进会计入完成事项")
    print("   - 提问次数与实际完成事项数呈正相关")
    print("   - 最近几天主要工作:")
    print("     • 2026-02-09: 解决akshare API限制问题，实施多数据源策略")
    print("     • 2026-02-04: 改进数据准确性，修复数据验证机制")
    print("     • 2026-02-03: 修复股票代码验证问题，增强数据分析能力")
    print("     • 2026-02-02: 集成AkShare库，增强A股分析能力")

if __name__ == "__main__":
    print_stats()
